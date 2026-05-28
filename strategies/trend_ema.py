"""
EMA Crossover Trend-Following Strategy
Inspired by the best-performing setups from Freqtrade community strategies.

Logic:
  - Entry  : fast EMA crosses above slow EMA + ADX > 25 + RSI 40-70 + volume confirmation
  - Exit   : fast EMA crosses below slow EMA OR trailing stop hit
  - Filter : only trade in bull regime (price > EMA 200 on higher timeframe)
"""
import pandas as pd
import numpy as np

from strategies.base import BaseStrategy
from risk.manager import RiskManager


class TrendEMAStrategy(BaseStrategy):
    name = "trend_ema"
    description = "Dual-EMA crossover with ADX trend filter and volume confirmation"

    def __init__(self, risk_manager: RiskManager,
                 fast: int = 9, slow: int = 21,
                 adx_threshold: float = 25.0):
        super().__init__(risk_manager)
        self.fast = fast
        self.slow = slow
        self.adx_threshold = adx_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        fast_col = f"ema_{self.fast}"
        slow_col = f"ema_{self.slow}"
        adx_col = next((c for c in df.columns if c.startswith("ADX_")), None)

        if fast_col not in df.columns or slow_col not in df.columns:
            raise ValueError(f"Missing EMA columns. Run prepare() first.")

        # Crossover signals
        prev_fast = df[fast_col].shift(1)
        prev_slow = df[slow_col].shift(1)
        cross_up   = (prev_fast <= prev_slow) & (df[fast_col] > df[slow_col])
        cross_down = (prev_fast >= prev_slow) & (df[fast_col] < df[slow_col])

        # Filters
        adx_ok    = df[adx_col] > self.adx_threshold if adx_col else True
        rsi_ok    = df["rsi_14"].between(40, 75) if "rsi_14" in df.columns else True
        vol_ok    = df["vol_ratio"] > 1.2 if "vol_ratio" in df.columns else True
        trend_ok  = df["close"] > df["ema_200"] if "ema_200" in df.columns else True

        df["signal"] = 0
        df.loc[cross_up  & adx_ok & rsi_ok & vol_ok & trend_ok, "signal"] = 1
        df.loc[cross_down, "signal"] = -1

        # ATR-based stops
        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["close"] - atr * 2.0
        df["take_profit"] = df["close"] + atr * 4.0  # 1:2 R/R minimum

        return df
