"""
SuperTrend Strategy
One of the best single-indicator trend systems, popularised by Olivier Seban.
Combines ATR-based dynamic support/resistance with a clear trend signal.

Entry  : SuperTrend flips from red to green (direction changes to 1)
Exit   : SuperTrend flips back (direction -1) OR hard stop
Filter : Volume above average, RSI not overbought
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


class SuperTrendStrategy(BaseStrategy):
    name = "supertrend"
    description = "SuperTrend ATR-based trend-following with volume filter"

    def __init__(self, risk_manager: RiskManager,
                 period: int = 10, multiplier: float = 3.0):
        super().__init__(risk_manager)
        self.period     = period
        self.multiplier = multiplier

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Find SuperTrend columns from pandas-ta output
        st_d_col = next((c for c in df.columns if c.startswith("SUPERTd_")), None)
        st_col   = next((c for c in df.columns if c.startswith("SUPERT_") and "d" not in c and "l" not in c and "s" not in c), None)

        if st_d_col is None:
            # Recompute in case prepare() used different params
            import pandas_ta as ta
            st = ta.supertrend(df["high"], df["low"], df["close"],
                               length=self.period, multiplier=self.multiplier)
            if st is not None:
                df = pd.concat([df, st], axis=1)
                st_d_col = next((c for c in df.columns if c.startswith("SUPERTd_")), None)

        if st_d_col is None:
            df["signal"] = 0
            return df

        direction      = df[st_d_col]
        prev_direction = direction.shift(1)

        flip_up   = (direction == 1)  & (prev_direction == -1)
        flip_down = (direction == -1) & (prev_direction == 1)

        rsi    = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        vol_ok = df["vol_ratio"] > 1.0 if "vol_ratio" in df.columns else True

        df["signal"] = 0
        df.loc[flip_up   & (rsi < 75) & vol_ok, "signal"] =  1
        df.loc[flip_down & (rsi > 25) & vol_ok, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["close"] - atr * 2.5
        df["take_profit"] = df["close"] + atr * 5.0

        return df
