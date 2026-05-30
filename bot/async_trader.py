"""
Full async live trader — replaces the synchronous polling loop.
Uses asyncio + WebSocket feed + REST API + Telegram bot concurrently.

Architecture:
  ┌─────────────────────────────────────────────────────┐
  │  asyncio event loop                                  │
  │  ├── WebSocketFeed.stream()   → candle queue         │
  │  ├── _process_candles()       → strategy → orders    │
  │  ├── _compound_loop()         → weekly auto-compound │
  │  ├── _health_loop()           → strategy monitor     │
  │  └── uvicorn (API + webhook)  → REST control         │
  └─────────────────────────────────────────────────────┘
"""
import asyncio
import time
from datetime import datetime
from typing import Optional
from loguru import logger

from config import CONFIG
from data.websocket_feed import WebSocketFeed, CandleBuffer
from data.database import (
    init_db, insert_trade, close_trade as db_close,
    save_equity, log_signal, get_state, set_state,
)
from strategies import STRATEGIES
from risk.manager import RiskManager, TradeSignal
from bot.position_manager import PositionManager
from bot.notifier import notify_startup, notify_drawdown_alert
from bot.auto_compound import AutoCompounder, CompoundMode
from bot.strategy_monitor import StrategyMonitor
from utils.correlation import CorrelationFilter
from utils.sentiment import get_current_fng, get_funding_rate, sentiment_gate
from utils.events_filter import EventsFilter
from utils.candle_patterns import add_candle_patterns
from utils.orderbook import fetch_orderbook, orderbook_filter


class AsyncLiveTrader:
    def __init__(self, config=CONFIG):
        self.cfg      = config
        self.dry_run  = config.dry_run

        init_db()
        self.risk        = RiskManager(initial_capital=10_000)
        self.pos_mgr     = PositionManager(dry_run=self.dry_run)
        self.corr_filter = CorrelationFilter(threshold=0.80)
        self.events      = EventsFilter()
        self.compounder  = AutoCompounder(
            initial_capital=10_000,
            mode=CompoundMode.REINVEST_ALL,
        )
        self.monitor = StrategyMonitor(
            strategy_name     = config.active_strategy,
            baseline_sharpe   = 1.5,
            baseline_win_rate = 55.0,
        )
        self.buffer = CandleBuffer(maxlen=500)

        # Sentiment cache
        self._sentiment: dict = {"allow_long": True, "allow_short": True, "reason": "ok"}
        self._sentiment_ts: float = 0.0

        notify_startup(config.active_strategy, config.pairs, self.dry_run)
        logger.info("AsyncLiveTrader ready.")

    # ── Main entry ────────────────────────────────────────────────────────────

    async def run(self):
        feed = WebSocketFeed(self.cfg.pairs, self.cfg.timeframe, self.cfg.exchange.name)

        tasks = [
            asyncio.create_task(self._candle_consumer(feed)),
            asyncio.create_task(self._compound_loop()),
            asyncio.create_task(self._health_loop()),
            asyncio.create_task(self._sentiment_refresh_loop()),
        ]
        logger.info("Starting async trading loop...")
        await asyncio.gather(*tasks)

    # ── Candle consumer ───────────────────────────────────────────────────────

    async def _candle_consumer(self, feed: WebSocketFeed):
        async for candle in feed.stream():
            if not candle.closed:
                continue
            self.buffer.push(candle)
            if self.buffer.is_ready(candle.symbol, min_bars=100):
                await self._process_symbol(candle.symbol)

    async def _process_symbol(self, symbol: str):
        if get_state("paused", False):
            return

        # Hot-swap strategy
        active = get_state("active_strategy", self.cfg.active_strategy)
        StratCls = STRATEGIES.get(active)
        if not StratCls:
            return
        strategy = StratCls(self.risk)

        df = self.buffer.to_df(symbol)
        if df.empty:
            return

        self.corr_filter.update(symbol, df["close"])

        try:
            sig_df  = strategy.run(df)
            last    = sig_df.iloc[-1]
            signal  = int(last.get("signal", 0))
            price   = float(last["close"])
        except Exception as e:
            logger.error(f"Strategy error on {symbol}: {e}")
            return

        log_signal(symbol, strategy.name, signal, price,
                   float(last.get("ml_confidence", 1.0)))

        # Manage open position
        if symbol in self.pos_mgr.positions:
            actions = self.pos_mgr.update(symbol, price)
            if signal == -1 and symbol in self.pos_mgr.positions:
                self.pos_mgr._close(symbol, price, "signal_exit")
            dd = self.risk.portfolio.current_drawdown()
            if dd > self.cfg.risk.max_drawdown_pct * 0.80:
                notify_drawdown_alert(dd, self.risk.portfolio.capital)
            return

        if signal != 1:
            return

        # Filters
        safe_ev, ev_reason = self.events.is_safe_to_trade()
        if not safe_ev:
            logger.info(f"Events filter blocked {symbol}: {ev_reason}")
            return

        if not self._sentiment.get("allow_long", True):
            return

        if self.corr_filter.is_correlated_with_open(symbol, list(self.pos_mgr.positions)):
            return

        # Order book confirmation
        ob = await fetch_orderbook(symbol, self.cfg.exchange.name)
        ob_ok, ob_reason = orderbook_filter(ob, "long")
        if not ob_ok:
            logger.debug(f"OB filter blocked {symbol}: {ob_reason}")
            return

        # Candle pattern confirmation
        df_pat = add_candle_patterns(df)
        if float(df_pat["candle_score"].iloc[-1]) < 0:
            return

        # Size and validate
        sl    = float(last.get("stop_loss",   price * 0.97))
        tp1   = price + (price - sl) * self.cfg.risk.risk_reward_ratio
        tp2   = price + (price - sl) * self.cfg.risk.risk_reward_ratio * 2
        sig   = TradeSignal(symbol, "long", price, sl, tp2)

        if not self.risk.validate_signal(sig):
            return

        atr    = float(last.get("atr_14", price * 0.02))
        size   = self.risk.atr_size(price, atr)
        amount = min(size, self.risk.portfolio.capital
                     * self.cfg.risk.max_position_size_pct / price)

        if amount * price < 10:
            return

        self.pos_mgr.open_position(symbol, "long", price, amount, sl, tp1, tp2)
        insert_trade(symbol, "long", strategy.name, price, amount, sl, tp2, self.dry_run)
        save_equity(strategy.name, self.risk.portfolio.capital,
                    self.risk.portfolio.current_drawdown())

    # ── Background loops ──────────────────────────────────────────────────────

    async def _compound_loop(self):
        while True:
            await asyncio.sleep(3600)   # check every hour
            if self.compounder.should_compound():
                result = self.compounder.run(self.risk.portfolio.capital)
                logger.info(f"Compound cycle: {result}")

    async def _health_loop(self):
        while True:
            await asyncio.sleep(3600 * 6)   # check every 6h
            health = self.monitor.check()
            logger.info(f"Strategy health: {health.status.value} — {health.message}")

    async def _sentiment_refresh_loop(self):
        while True:
            fng = get_current_fng()
            fr  = get_funding_rate("BTC/USDT:USDT", self.cfg.exchange.name)
            self._sentiment    = sentiment_gate(fng["value"] if fng else None, fr)
            self._sentiment_ts = time.time()
            logger.debug(f"Sentiment refreshed: {self._sentiment}")
            await asyncio.sleep(4 * 3600)   # every 4h


async def run_all_services(config=CONFIG):
    """
    Start trader + API + Telegram bot + webhook receiver concurrently.
    Called from main.py live --async mode.
    """
    import uvicorn
    from bot.api import app as api_app
    from bot.webhook import app as webhook_app, set_live_trader

    trader = AsyncLiveTrader(config)
    set_live_trader(trader)

    api_server     = uvicorn.Server(uvicorn.Config(api_app,     host="0.0.0.0", port=8000, log_level="warning"))
    webhook_server = uvicorn.Server(uvicorn.Config(webhook_app, host="0.0.0.0", port=8001, log_level="warning"))

    await asyncio.gather(
        trader.run(),
        api_server.serve(),
        webhook_server.serve(),
    )
