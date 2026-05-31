"""
Cross-sectional momentum strategy for individual equities.
Uses the classic 12-1 month momentum factor: 12-month return minus the most
recent 1-month return (skip period avoids short-term reversal contamination).
"""
import numpy as np
import pandas as pd

from strategies.base import BaseStrategy
from risk.manager import RiskManager


class MomentumFactorStrategy(BaseStrategy):
    name = "momentum_factor"
    description = "12-1 month cross-sectional momentum for equities"

    def __init__(self, risk_manager: RiskManager,
                 lookback_days: int = 252,
                 skip_days: int = 21,
                 holding_days: int = 21):
        super().__init__(risk_manager)
        self.lookback_days = lookback_days
        self.skip_days = skip_days
        self.holding_days = holding_days

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 12-1 month momentum: shift by skip_days to exclude the most recent month
        formation_period = self.lookback_days - self.skip_days
        df["momentum_score"] = df["close"].pct_change(formation_period).shift(self.skip_days)

        # Trend filter: close must be above 200-day SMA
        sma200 = df["close"].rolling(200).mean()
        above_trend = df["close"] > sma200

        # RSI filter: avoid entering overbought momentum names
        rsi = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        rsi_ok = rsi < 75

        df["signal"] = 0
        buy_cond = (df["momentum_score"] > 0) & above_trend & rsi_ok
        df.loc[buy_cond, "signal"] = 1

        df["stop_loss"] = df["close"] * 0.93
        df["take_profit"] = df["close"] * 1.25

        return df
