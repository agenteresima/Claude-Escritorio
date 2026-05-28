"""
Live / paper trading executor — upgraded with:
  - PositionManager (partial TPs, break-even, time exits)
  - CorrelationFilter (no concurrent correlated positions)
  - Sentiment gate (Fear & Greed + funding rate)
  - Telegram notifications
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
from bot.position_manager import PositionManager
from bot.notifier import notify_startup, notify_drawdown_alert
from utils.correlation import CorrelationFilter
from utils.sentiment import get_current_fng, get_funding_rate, sentiment_gate


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

        self.risk       = RiskManager(initial_capital=10_000)
        StratCls        = STRATEGIES[config.active_strategy]
        self.strategy   = StratCls(self.risk)
        self.pos_mgr    = PositionManager(dry_run=self.dry_run)
        self.corr_filter = CorrelationFilter(threshold=0.80)

        # Sentiment refresh every 4h
        self._last_sentiment_ts = 0.0
        self._sentiment_gate    = {"allow_long": True, "allow_short": True, "reason": "ok"}

        notify_startup(config.active_strategy, config.pairs, self.dry_run)
        logger.info(
            f"LiveTrader ready | strategy={config.active_strategy} "
            f"| dry_run={self.dry_run} | pairs={config.pairs}"
        )

    # ------------------------------------------------------------------

    def _refresh_sentiment(self):
        if time.time() - self._last_sentiment_ts < 4 * 3600:
            return
        fng = get_current_fng()
        fr  = get_funding_rate("BTC/USDT:USDT", self.cfg.exchange.name)
        self._sentiment_gate    = sentiment_gate(fng["value"] if fng else None, fr)
        self._last_sentiment_ts = time.time()
        logger.info(f"Sentiment gate: {self._sentiment_gate}")

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
            if signal != 1:
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

            if amount * price < 10:   # minimum order size guard
                return

            self._place_order(symbol, "buy", amount, sl, tp1, tp2)

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
