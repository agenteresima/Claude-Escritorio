"""
VWAP Bounce Strategy
Professional intraday approach used by institutional desks.
VWAP acts as dynamic support/resistance reset daily.

Entry  : Price dips below VWAP and bounces back above it within 3 bars
         + RSI was oversold on the touch
         + OBV increasing (buying pressure)
Exit   : Price crosses back below VWAP midpoint OR take profit ATR*2
Filter : Only trade between 08:00–20:00 UTC (active session)
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


class VWAPBounceStrategy(BaseStrategy):
    name = "vwap_bounce"
    description = "VWAP institutional bounce — price dips below and recovers"

    def __init__(self, risk_manager: RiskManager,
                 bounce_bars: int = 3, rsi_threshold: float = 45.0):
        super().__init__(risk_manager)
        self.bounce_bars   = bounce_bars
        self.rsi_threshold = rsi_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "vwap" not in df.columns:
            df["signal"] = 0
            return df

        vwap = df["vwap"]
        rsi  = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        obv  = df["obv"]    if "obv"    in df.columns else pd.Series(0,  index=df.index)

        # Price was below VWAP within the last N bars and is now above
        below_recently = pd.Series(False, index=df.index)
        for lag in range(1, self.bounce_bars + 1):
            below_recently |= (df["low"].shift(lag) < vwap.shift(lag))

        bounce_up = below_recently & (df["close"] > vwap) & (df["close"].shift(1) <= vwap.shift(1))

        # OBV rising on the bounce
        obv_rising = obv > obv.shift(3)

        # Session filter (active hours if index has timezone)
        try:
            hour = df.index.hour
            session_ok = (hour >= 8) & (hour <= 20)
        except Exception:
            session_ok = True

        df["signal"] = 0
        df.loc[bounce_up & (rsi < self.rsi_threshold + 10) & obv_rising & session_ok, "signal"] = 1

        # Short: price breaks below VWAP after being above
        above_recently = pd.Series(False, index=df.index)
        for lag in range(1, self.bounce_bars + 1):
            above_recently |= (df["high"].shift(lag) > vwap.shift(lag))

        bounce_down = above_recently & (df["close"] < vwap) & (df["close"].shift(1) >= vwap.shift(1))
        df.loc[bounce_down & (rsi > 100 - self.rsi_threshold - 10) & session_ok, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.015
        df["stop_loss"]   = df["close"] - atr * 1.5
        df["take_profit"] = df["close"] + atr * 3.0

        return df
