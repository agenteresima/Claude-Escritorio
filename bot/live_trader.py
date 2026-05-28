"""
Live / paper trading executor.
Uses CCXT unified API so swapping exchanges requires only a config change.
Always starts in dry_run=True mode — set dry_run=False only after
extensive paper trading and backtesting.
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
from utils.indicators import add_all_indicators


class LiveTrader:
    def __init__(self, config=CONFIG):
        self.cfg     = config
        self.dry_run = config.dry_run

        # Exchange setup
        exchange_cls = getattr(ccxt, config.exchange.name)
        creds = {}
        if config.exchange.api_key:
            creds = {
                "apiKey":    config.exchange.api_key,
                "secret":    config.exchange.api_secret,
                "enableRateLimit": True,
            }
        if config.exchange.sandbox:
            creds["options"] = {"defaultType": "future"}

        self.exchange = exchange_cls(creds)
        if config.exchange.sandbox:
            self.exchange.set_sandbox_mode(True)

        # Strategy
        self.risk     = RiskManager(initial_capital=10_000)
        StratCls      = STRATEGIES[config.active_strategy]
        self.strategy = StratCls(self.risk)

        self.open_positions: dict[str, dict] = {}
        logger.info(
            f"LiveTrader init | strategy={config.active_strategy} "
            f"| dry_run={self.dry_run} | exchange={config.exchange.name}"
        )

    # ------------------------------------------------------------------

    def fetch_latest(self, symbol: str) -> pd.DataFrame:
        df = fetch_ohlcv_ccxt(
            symbol, self.cfg.timeframe, use_cache=False,
            exchange_name=self.cfg.exchange.name,
        )
        return df.iloc[-500:]  # last 500 bars is enough for all indicators

    def get_balance(self) -> float:
        if self.dry_run:
            return self.risk.portfolio.capital
        balance = self.exchange.fetch_balance()
        return float(balance["USDT"]["free"])

    def place_order(self, symbol: str, side: str, amount: float,
                    stop_loss: float, take_profit: float):
        if self.dry_run:
            price = self._last_price(symbol)
            logger.info(
                f"[DRY RUN] {side.upper()} {amount:.4f} {symbol} @ {price:.2f} "
                f"| SL={stop_loss:.2f} TP={take_profit:.2f}"
            )
            self.open_positions[symbol] = {
                "side": side, "amount": amount, "entry": price,
                "sl": stop_loss, "tp": take_profit, "time": datetime.utcnow(),
            }
            return

        order = self.exchange.create_order(symbol, "market", side, amount)
        logger.info(f"Order placed: {order['id']} | {side} {amount} {symbol}")

        # OCO stop-limit + take-profit (Binance-specific)
        self.exchange.create_order(
            symbol, "STOP_MARKET", "sell" if side == "buy" else "buy",
            amount, None, {"stopPrice": stop_loss}
        )

    def _last_price(self, symbol: str) -> float:
        ticker = self.exchange.fetch_ticker(symbol)
        return float(ticker["last"])

    # ------------------------------------------------------------------

    def tick(self, symbol: str):
        """Process one trading cycle for a symbol."""
        try:
            df       = self.fetch_latest(symbol)
            sig_df   = self.strategy.run(df)
            last_row = sig_df.iloc[-1]
            signal   = int(last_row.get("signal", 0))
            price    = float(last_row["close"])

            # --- Manage existing position ---
            if symbol in self.open_positions:
                pos = self.open_positions[symbol]
                new_sl = self.risk.update_trailing_stop(price, pos["entry"], pos["sl"])
                self.open_positions[symbol]["sl"] = new_sl

                if price <= new_sl or price >= pos["tp"] or signal == -1:
                    reason = "sl" if price <= new_sl else ("tp" if price >= pos["tp"] else "signal")
                    logger.info(f"Closing {symbol} @ {price:.2f} | reason={reason}")
                    del self.open_positions[symbol]

            # --- Open new position ---
            elif signal == 1 and symbol not in self.open_positions:
                sl  = float(last_row.get("stop_loss",   price * 0.97))
                tp  = float(last_row.get("take_profit", price * 1.06))
                sig = TradeSignal(symbol, "long", price, sl, tp)

                if self.risk.validate_signal(sig):
                    atr    = float(last_row.get("atr_14", price * 0.02))
                    size   = self.risk.atr_size(price, atr)
                    balance= self.get_balance()
                    amount = min(size, balance * self.risk.cfg.max_position_size_pct / price)
                    self.place_order(symbol, "buy", amount, sl, tp)

        except Exception as e:
            logger.error(f"Tick error for {symbol}: {e}")

    def run(self):
        """Main loop — iterates over all pairs on each timeframe close."""
        logger.info("Starting trading loop...")
        while True:
            for symbol in self.cfg.pairs:
                self.tick(symbol)
            wait = self._seconds_to_next_close()
            logger.debug(f"Sleeping {wait}s until next candle close...")
            time.sleep(wait)

    def _seconds_to_next_close(self) -> int:
        tf_seconds = {
            "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
            "1h": 3600, "4h": 14400, "1d": 86400,
        }
        period = tf_seconds.get(self.cfg.timeframe, 3600)
        now    = int(time.time())
        return period - (now % period) + 5  # +5s buffer
