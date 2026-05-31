"""
Z-score mean reversion strategy for equities.
Buys statistically oversold names (z-score below -z_entry) confirmed by
elevated volume, and targets a return to the rolling mean.
"""
import numpy as np
import pandas as pd

from strategies.base import BaseStrategy
from risk.manager import RiskManager


class EquityMeanReversionStrategy(BaseStrategy):
    name = "equity_mean_reversion"
    description = "Z-score mean reversion against rolling mean for equities"

    def __init__(self, risk_manager: RiskManager,
                 window: int = 20,
                 z_entry: float = 2.0,
                 z_exit: float = 0.5):
        super().__init__(risk_manager)
        self.window = window
        self.z_entry = z_entry
        self.z_exit = z_exit

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        rolling_mean = df["close"].rolling(self.window).mean()
        rolling_std = df["close"].rolling(self.window).std()
        df["zscore"] = (df["close"] - rolling_mean) / (rolling_std + 1e-9)

        vol_ratio = df["volume"] / df["volume"].rolling(self.window).mean()
        vol_ok = vol_ratio > 1.2

        buy_cond = (df["zscore"] < -self.z_entry) & vol_ok
        sell_cond = df["zscore"] > self.z_exit

        df["signal"] = 0
        df.loc[buy_cond, "signal"] = 1
        df.loc[sell_cond, "signal"] = -1

        df["stop_loss"] = df["close"] * 0.95
        df["take_profit"] = rolling_mean  # mean-reversion target

        return df
