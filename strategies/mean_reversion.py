"""
Mean Reversion Strategy (RSI + Bollinger Bands)
Best-in-class for sideways/ranging markets.

Logic:
  - Entry long  : RSI < 30 AND price touches lower BB AND MFI < 25
  - Entry short : RSI > 70 AND price touches upper BB AND MFI > 75
  - Exit        : RSI returns to 50 OR price reaches BB mid-line
  - Filter      : ADX < 25 (confirm ranging, not trending)
"""
import pandas as pd
import numpy as np

from strategies.base import BaseStrategy
from risk.manager import RiskManager


class MeanReversionStrategy(BaseStrategy):
    name = "mean_reversion"
    description = "RSI + Bollinger Band mean reversion for ranging markets"

    def __init__(self, risk_manager: RiskManager,
                 rsi_oversold: float = 30.0, rsi_overbought: float = 70.0,
                 adx_max: float = 25.0, bb_std: float = 2.0):
        super().__init__(risk_manager)
        self.rsi_oversold   = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.adx_max        = adx_max
        self.bb_std         = bb_std

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        adx_col    = next((c for c in df.columns if c.startswith("ADX_")), None)
        bb_low_col = next((c for c in df.columns if "BBL_" in c), None)
        bb_up_col  = next((c for c in df.columns if "BBU_" in c), None)
        bb_mid_col = next((c for c in df.columns if "BBM_" in c), None)

        ranging = df[adx_col] < self.adx_max if adx_col else True
        rsi     = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        mfi     = df["mfi"]    if "mfi"    in df.columns else pd.Series(50, index=df.index)

        at_bb_low = df["close"] <= df[bb_low_col] if bb_low_col else False
        at_bb_up  = df["close"] >= df[bb_up_col]  if bb_up_col  else False

        # Require two-bar confirmation to reduce false signals
        oversold_conf   = (rsi < self.rsi_oversold)  & (rsi.shift(1) < self.rsi_oversold)
        overbought_conf = (rsi > self.rsi_overbought) & (rsi.shift(1) > self.rsi_overbought)

        long_signal  = ranging & oversold_conf  & at_bb_low & (mfi < 30)
        short_signal = ranging & overbought_conf & at_bb_up  & (mfi > 70)

        # Exit when RSI reverts past midpoint
        exit_long  = rsi > 55
        exit_short = rsi < 45

        df["signal"] = 0
        df.loc[long_signal,  "signal"] = 1
        df.loc[short_signal, "signal"] = -1
        df.loc[exit_long,    "signal"] = df.loc[exit_long, "signal"].where(
            df.loc[exit_long, "signal"] == -1, 0
        )

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        bb_mid = df[bb_mid_col] if bb_mid_col else df["close"]

        df["stop_loss"]   = df["close"] - atr * 1.5
        df["take_profit"] = bb_mid   # Target: return to the mean

        return df
