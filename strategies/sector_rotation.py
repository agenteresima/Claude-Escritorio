"""
Sector ETF rotation strategy.
Ranks ETFs by 63-day relative strength and buys the strongest names
that are also in an uptrend (price above long-term moving average).
"""
import numpy as np
import pandas as pd

from strategies.base import BaseStrategy
from risk.manager import RiskManager


SECTOR_ETFS = {
    "XLK":  "Technology",
    "XLV":  "Healthcare",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLY":  "Consumer Disc",
    "XLP":  "Consumer Staples",
    "XLI":  "Industrials",
    "XLU":  "Utilities",
    "XLRE": "Real Estate",
    "XLB":  "Materials",
    "XLC":  "Communication",
}


class SectorRotationStrategy(BaseStrategy):
    name = "sector_rotation"
    description = "Rotate into strongest sector ETF by relative strength"

    def __init__(self, risk_manager: RiskManager,
                 rs_period: int = 63,
                 ma_period: int = 200):
        super().__init__(risk_manager)
        self.rs_period = rs_period
        self.ma_period = ma_period

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["rs_score"] = df["close"] / df["close"].shift(self.rs_period) - 1
        df["above_ma"] = (df["close"] > df["close"].rolling(self.ma_period).mean()).astype(int)

        df["signal"] = np.where(
            (df["rs_score"] > 0) & (df["above_ma"] == 1), 1, 0
        )

        # ATR-based stop; fall back to 2 % of price when atr_14 is unavailable
        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"] = df["close"] - 2 * atr
        df["take_profit"] = df["close"] * 1.20

        return df
