"""
Volatility Breakout Strategy (Donchian + ATR squeeze)
Best for high-momentum moves — combines Donchian channel breakout
with the Bollinger Band / Keltner Channel squeeze (popularised by
Linda Raschke and John Carter).

Logic:
  - Squeeze  : BB inside KC (low volatility coiling)
  - Breakout : price closes above upper Donchian channel + volume surge
  - Momentum : RSI > 55 and MACD histogram positive
  - Stop     : ATR * 1.5 below breakout candle
"""
import pandas as pd
import numpy as np

from strategies.base import BaseStrategy
from risk.manager import RiskManager


class BreakoutStrategy(BaseStrategy):
    name = "breakout"
    description = "Donchian breakout with volatility squeeze confirmation"

    def __init__(self, risk_manager: RiskManager,
                 donchian_period: int = 20, squeeze_bars: int = 5):
        super().__init__(risk_manager)
        self.donchian_period = donchian_period
        self.squeeze_bars    = squeeze_bars

    def _is_squeeze(self, df: pd.DataFrame) -> pd.Series:
        """BB inside KC = low-volatility coil (squeeze active)."""
        bb_up  = next((c for c in df.columns if "BBU_" in c), None)
        bb_low = next((c for c in df.columns if "BBL_" in c), None)
        kc_up  = next((c for c in df.columns if "KCUe_" in c), None)
        kc_low = next((c for c in df.columns if "KCLe_" in c), None)

        if all([bb_up, bb_low, kc_up, kc_low]):
            return (df[bb_up] < df[kc_up]) & (df[bb_low] > df[kc_low])
        return pd.Series(False, index=df.index)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        don_up  = next((c for c in df.columns if "DCU_" in c), None)
        don_low = next((c for c in df.columns if "DCL_" in c), None)
        macd_h  = next((c for c in df.columns if "MACDh_" in c), None)

        squeeze = self._is_squeeze(df)
        # At least N bars in squeeze before breakout
        squeeze_count = squeeze.rolling(self.squeeze_bars).sum()
        was_squeezed  = squeeze_count >= self.squeeze_bars

        # Price breaks above Donchian high of previous bar
        breakout_up   = don_up  and (df["close"] > df[don_up].shift(1))
        breakout_down = don_low and (df["close"] < df[don_low].shift(1))

        rsi    = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        macd_h_series = df[macd_h] if macd_h else pd.Series(0, index=df.index)
        vol_ok = df["vol_ratio"] > 1.5 if "vol_ratio" in df.columns else True

        long_signal  = was_squeezed & breakout_up  & (rsi > 55) & (macd_h_series > 0) & vol_ok
        short_signal = was_squeezed & breakout_down & (rsi < 45) & (macd_h_series < 0) & vol_ok

        df["signal"] = 0
        df.loc[long_signal,  "signal"] = 1
        df.loc[short_signal, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["close"] - atr * 1.5
        df["take_profit"] = df["close"] + atr * 4.5  # Momentum moves deserve wide targets

        return df
