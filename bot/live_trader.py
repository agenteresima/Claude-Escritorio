"""
Live / paper trading executor — full production stack:
  - PositionManager (partial TPs, break-even, time exits)
  - CorrelationFilter (no concurrent correlated positions)
  - Sentiment gate (Fear & Greed + funding rate)
  - EventsFilter (macro news blackout)
  - Candle pattern confirmation
  - DB persistence (survives restarts)
  - Telegram notifications
  - REST API state reads (pause/resume/force-close)
"""
import time
from datetime import datetime
from typing import Optional

import ccxt
import pandas as pd
from loguru import logger

from config import CONFIG
from risk.manager import RiskManager, TradeSignal
from strategies import STRATEGIES
from data.fetcher import fetch_ohlcv_ccxt
from data.database import (
    init_db, insert_trade, close_trade as db_close_trade,
    get_open_trades, save_equity, log_signal, get_state,
)
from bot.position_manager import PositionManager
from bot.notifier import notify_startup, notify_drawdown_alert
from utils.correlation import CorrelationFilter
from utils.sentiment import get_current_fng, get_funding_rate, sentiment_gate
from utils.events_filter import EventsFilter
from utils.candle_patterns import add_candle_patterns
from utils.macro_filter import get_macro_gate


class LiveTrader:
    def __init__(self, config=CONFIG):
        self.cfg     = config
        self.dry_run = config.dry_run

        # Exchange
        exchange_cls = getattr(ccxt, config.exchange.name)
        creds: dict  = {"enableRateLimit": True}
        if config.exchange.api_key:
            creds["apiKey"]  = config.exchange.api_key
            creds["secret"]  = config.exchange.api_secret
        self.exchange = exchange_cls(creds)
        if config.exchange.sandbox:
            self.exchange.set_sandbox_mode(True)

        init_db()
        self.risk        = RiskManager(initial_capital=10_000)
        active_strategy  = get_state("active_strategy", config.active_strategy)
        StratCls         = STRATEGIES[active_strategy]
        self.strategy    = StratCls(self.risk)
        self.pos_mgr     = PositionManager(dry_run=self.dry_run)
        self.corr_filter = CorrelationFilter(threshold=0.80)
        self.events      = EventsFilter()

        # Sentiment refresh every 4h
        self._last_sentiment_ts = 0.0
        self._sentiment_gate    = {"allow_long": True, "allow_short": True, "reason": "ok"}

        # Macro prediction filter refresh every 1h
        self._last_macro_ts  = 0.0
        self._macro_gate     = None   # MacroGate populated on first tick

        # Restore open positions from DB (survives restarts)
        self._restore_positions()

        notify_startup(active_strategy, config.pairs, self.dry_run)
        logger.info(
            f"LiveTrader ready | strategy={config.active_strategy} "
            f"| dry_run={self.dry_run} | pairs={config.pairs}"
        )

    # ------------------------------------------------------------------

    def _restore_positions(self):
        """Re-populate PositionManager from DB after a restart."""
        for trade in get_open_trades():
            from bot.position_manager import OpenPosition
            self.pos_mgr.positions[trade["symbol"]] = OpenPosition(
                symbol       = trade["symbol"],
                direction    = trade["direction"],
                entry_price  = trade["entry_price"],
                size         = trade["size"],
                stop_loss    = trade["stop_loss"],
                take_profit1 = trade["take_profit"],
                take_profit2 = trade["take_profit"] * 1.5,
            )
        if self.pos_mgr.positions:
            logger.info(f"Restored {len(self.pos_mgr.positions)} open positions from DB.")

    def _check_api_commands(self):
        """Check for commands issued via REST API (pause, force-close, strategy switch)."""
        if get_state("paused", False):
            return False   # signal caller to skip this tick

        new_strat = get_state("active_strategy", self.cfg.active_strategy)
        if new_strat != self.strategy.name:
            StratCls      = STRATEGIES.get(new_strat)
            if StratCls:
                self.strategy = StratCls(self.risk)
                logger.info(f"Strategy switched to: {new_strat}")

        return True

    def _refresh_sentiment(self):
        if time.time() - self._last_sentiment_ts < 4 * 3600:
            return
        fng = get_current_fng()
        fr  = get_funding_rate("BTC/USDT:USDT", self.cfg.exchange.name)
        self._sentiment_gate    = sentiment_gate(fng["value"] if fng else None, fr)
        self._last_sentiment_ts = time.time()
        logger.info(f"Sentiment gate: {self._sentiment_gate}")

    def _refresh_macro_gate(self, symbol: str):
        """Refresh macro prediction market filter (Polymarket + WSB) every 1h."""
        if time.time() - self._last_macro_ts < 3600:
            return
        try:
            self._macro_gate    = get_macro_gate(ticker=symbol.split("/")[0])
            self._last_macro_ts = time.time()
            logger.info(f"Macro gate: score={self._macro_gate.macro_score:.1f} "
                        f"wsb={self._macro_gate.wsb_mood} "
                        f"allow_long={self._macro_gate.allow_long} "
                        f"size_factor={self._macro_gate.size_factor:.0%}")
        except Exception as e:
            logger.warning(f"Macro gate refresh failed: {e}")

    def fetch_latest(self, symbol: str) -> pd.DataFrame:
        df = fetch_ohlcv_ccxt(
            symbol, self.cfg.timeframe, use_cache=False,
            exchange_name=self.cfg.exchange.name,
        )
        return df.iloc[-500:]

    def get_balance(self) -> float:
        if self.dry_run:
            return self.risk.portfolio.capital
        bal = self.exchange.fetch_balance()
        return float(bal["USDT"]["free"])

    def _last_price(self, symbol: str) -> float:
        return float(self.exchange.fetch_ticker(symbol)["last"])

    def _place_order(self, symbol: str, side: str, amount: float,
                     stop: float, tp1: float, tp2: float):
        entry = self._last_price(symbol)
        if self.dry_run:
            logger.info(f"[DRY] {side} {amount:.4f} {symbol} @ {entry:.4f} | SL={stop:.4f} TP1={tp1:.4f}")
            self.pos_mgr.open_position(symbol, side, entry, amount, stop, tp1, tp2)
            return

        order = self.exchange.create_order(symbol, "market", side, amount)
        logger.info(f"Order: {order['id']} | {side} {amount} {symbol}")
        self.pos_mgr.open_position(symbol, side, entry, amount, stop, tp1, tp2)

    # ------------------------------------------------------------------

    def tick(self, symbol: str):
        try:
            if not self._check_api_commands():
                return   # bot is paused

            # Force-close command from API
            if get_state(f"force_close_{symbol}", False):
                price = self._last_price(symbol)
                self.pos_mgr._close(symbol, price, "api_force_close")
                from data.database import set_state
                set_state(f"force_close_{symbol}", False)
                return

            df  = self.fetch_latest(symbol)
            self.corr_filter.update(symbol, df["close"])

            sig_df   = self.strategy.run(df)
            last_row = sig_df.iloc[-1]
            signal   = int(last_row.get("signal", 0))
            price    = float(last_row["close"])

            # Manage open position via PositionManager
            if symbol in self.pos_mgr.positions:
                actions = self.pos_mgr.update(symbol, price)

                dd = self.risk.portfolio.current_drawdown()
                if dd > self.cfg.risk.max_drawdown_pct * 0.80:
                    notify_drawdown_alert(dd, self.risk.portfolio.capital)

                # Override close if strategy says exit
                if signal == -1 and symbol in self.pos_mgr.positions:
                    self.pos_mgr._close(symbol, price, "signal_exit")
                return

            # Open new position
            log_signal(symbol, self.strategy.name, signal, price,
                       float(last_row.get("ml_confidence", 1.0)))

            if signal != 1:
                return

            # ── Events filter ──
            safe, reason = self.events.is_safe_to_trade()
            if not safe:
                logger.info(f"Events filter blocked {symbol}: {reason}")
                return

            # ── Candle pattern confirmation ──
            df_pat = add_candle_patterns(df)
            candle_score = float(df_pat["candle_score"].iloc[-1])
            if candle_score < 0:
                logger.debug(f"Candle patterns negative ({candle_score}) — skipping {symbol}")
                return

            # ── Macro prediction filter (Polymarket + WSB) ──
            self._refresh_macro_gate(symbol)
            if self._macro_gate:
                if not self._macro_gate.allow_long:
                    logger.info(
                        f"Macro gate blocked long on {symbol}: {self._macro_gate.reason}"
                    )
                    return

            self._refresh_sentiment()
            gate = self._sentiment_gate

            if not gate["allow_long"]:
                logger.debug(f"Sentiment gate blocks long on {symbol}: {gate['reason']}")
                return

            open_pairs = list(self.pos_mgr.positions.keys())
            if self.corr_filter.is_correlated_with_open(symbol, open_pairs):
                logger.debug(f"Correlation filter skipped {symbol}")
                return

            sl   = float(last_row.get("stop_loss",   price * 0.97))
            tp1  = price + (price - sl) * self.cfg.risk.risk_reward_ratio
            tp2  = price + (price - sl) * self.cfg.risk.risk_reward_ratio * 2
            sig  = TradeSignal(symbol, "long", price, sl, tp2)

            if not self.risk.validate_signal(sig):
                return

            atr    = float(last_row.get("atr_14", price * 0.02))
            size   = self.risk.atr_size(price, atr)
            bal    = self.get_balance()
            amount = min(size, bal * self.cfg.risk.max_position_size_pct / price)

            # Apply macro size factor (Polymarket + WSB overcrowding)
            if self._macro_gate and self._macro_gate.size_factor < 1.0:
                amount *= self._macro_gate.size_factor
                logger.info(
                    f"Macro gate reduced size to {self._macro_gate.size_factor:.0%} "
                    f"for {symbol}: {self._macro_gate.reason}"
                )

            if amount * price < 10:   # minimum order size guard
                return

            self._place_order(symbol, "buy", amount, sl, tp1, tp2)

            # Persist to DB
            insert_trade(
                symbol, "long", self.strategy.name, price, amount,
                sl, tp2, dry_run=self.dry_run,
            )

            # Equity snapshot
            save_equity(self.strategy.name, self.risk.portfolio.capital,
                        self.risk.portfolio.current_drawdown())

        except Exception as e:
            logger.error(f"Tick error {symbol}: {e}")

    def run(self):
        logger.info("Starting trading loop...")
        while True:
            for symbol in self.cfg.pairs:
                self.tick(symbol)
            wait = self._seconds_to_next_close()
            logger.debug(f"Sleeping {wait}s until next candle close...")
            time.sleep(wait)

    def _seconds_to_next_close(self) -> int:
        tf_map = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800,
                  "1h": 3600, "4h": 14400, "1d": 86400}
        period = tf_map.get(self.cfg.timeframe, 3600)
        return period - (int(time.time()) % period) + 5
