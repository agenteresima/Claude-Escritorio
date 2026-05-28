"""
Multi-Timeframe Strategy (MTF)
Higher timeframe sets the bias, lower timeframe gives the entry.

Logic:
  4h trend bias:
    - Bull  : price > EMA200(4h) AND EMA50(4h) > EMA200(4h)
    - Bear  : price < EMA200(4h) AND EMA50(4h) < EMA200(4h)
    - Neutral: between

  1h entry (only in direction of 4h bias):
    - Long  : RSI(1h) < 45 pulling back into EMA21(1h) + MACD turning up
    - Short : RSI(1h) > 55 pulling back into EMA21(1h) + MACD turning down

This approach eliminates counter-trend trades — the #1 cause of blown accounts.
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager
from utils.indicators import add_all_indicators


class MultiTimeframeStrategy(BaseStrategy):
    name = "mtf"
    description = "4h trend bias + 1h entry — eliminates counter-trend trades"

    def __init__(self, risk_manager: RiskManager,
                 htf_ema_fast: int = 50, htf_ema_slow: int = 200,
                 ltf_ema: int = 21, rsi_dip: float = 45.0):
        super().__init__(risk_manager)
        self.htf_ema_fast = htf_ema_fast
        self.htf_ema_slow = htf_ema_slow
        self.ltf_ema      = ltf_ema
        self.rsi_dip      = rsi_dip

    def _htf_bias(self, htf: pd.DataFrame) -> pd.Series:
        """Compute 4h trend bias resampled back to 1h index."""
        h = add_all_indicators(htf)
        bias = pd.Series(0, index=h.index)
        bull = (h["close"] > h[f"ema_{self.htf_ema_slow}"]) & \
               (h[f"ema_{self.htf_ema_fast}"] > h[f"ema_{self.htf_ema_slow}"])
        bear = (h["close"] < h[f"ema_{self.htf_ema_slow}"]) & \
               (h[f"ema_{self.htf_ema_fast}"] < h[f"ema_{self.htf_ema_slow}"])
        bias[bull] =  1
        bias[bear] = -1
        return bias

    def run_mtf(self, ltf: pd.DataFrame, htf: pd.DataFrame) -> pd.DataFrame:
        """Main entry point when two timeframes are available."""
        ltf_ind  = self.prepare(ltf)
        htf_bias = self._htf_bias(htf)

        # Forward-fill 4h bias onto 1h index (no lookahead)
        bias_reindexed = htf_bias.reindex(ltf_ind.index, method="ffill").fillna(0)
        ltf_ind["htf_bias"] = bias_reindexed

        return self.generate_signals(ltf_ind)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        bias = df.get("htf_bias", pd.Series(1, index=df.index))  # default bull if no HTF
        rsi  = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        ema  = df[f"ema_{self.ltf_ema}"] if f"ema_{self.ltf_ema}" in df.columns else df["close"]

        macd_h_col = next((c for c in df.columns if "MACDh_" in c), None)
        macd_turn_up   = pd.Series(False, index=df.index)
        macd_turn_down = pd.Series(False, index=df.index)
        if macd_h_col:
            macd_h = df[macd_h_col]
            macd_turn_up   = (macd_h > 0) & (macd_h.shift(1) <= 0)
            macd_turn_down = (macd_h < 0) & (macd_h.shift(1) >= 0)

        pullback_to_ema = (df["low"] <= ema * 1.005) & (df["close"] > ema)

        long_entry  = (bias == 1)  & (rsi < self.rsi_dip) & pullback_to_ema & macd_turn_up
        short_entry = (bias == -1) & (rsi > (100 - self.rsi_dip)) & (~pullback_to_ema) & macd_turn_down

        df["signal"] = 0
        df.loc[long_entry,  "signal"] =  1
        df.loc[short_entry, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["close"] - atr * 2.0
        df["take_profit"] = df["close"] + atr * 5.0   # Trend trades deserve wide targets

        return df

    # Fallback: single-timeframe mode
    def generate_signals_single(self, df: pd.DataFrame) -> pd.DataFrame:
        df["htf_bias"] = 1  # assume bull in single-TF mode
        return self.generate_signals(df)
