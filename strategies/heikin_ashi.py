"""
Heikin Ashi Trend Strategy
Heikin Ashi candles smooth out noise and make trend direction clearer.
Used by: Jesse Livermore approach modernised, many Japanese traders.

HA candle formulas:
  HA_Close = (O + H + L + C) / 4
  HA_Open  = (prev_HA_Open + prev_HA_Close) / 2
  HA_High  = max(H, HA_Open, HA_Close)
  HA_Low   = min(L, HA_Open, HA_Close)

Signals:
  Long  : HA_Close > HA_Open (bull candle) AND no lower shadow (strong bull)
           + switch from bear to bull candle (trend flip)
  Short : HA_Close < HA_Open (bear candle) AND no upper shadow (strong bear)

Advantage over regular candles: much fewer whipsaws.
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


def compute_heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    ha = pd.DataFrame(index=df.index)
    ha["ha_close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4

    ha_open = [0.0] * len(df)
    ha_open[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
    for i in range(1, len(df)):
        ha_open[i] = (ha_open[i-1] + ha["ha_close"].iloc[i-1]) / 2
    ha["ha_open"]  = ha_open
    ha["ha_high"]  = df[["high"]].join(ha[["ha_open", "ha_close"]]).max(axis=1)
    ha["ha_low"]   = df[["low"]].join(ha[["ha_open", "ha_close"]]).min(axis=1)

    ha["ha_bull"]        = ha["ha_close"] > ha["ha_open"]
    ha["ha_no_low_wick"] = ha["ha_low"]  == ha[["ha_open","ha_close"]].min(axis=1)
    ha["ha_no_up_wick"]  = ha["ha_high"] == ha[["ha_open","ha_close"]].max(axis=1)
    return ha


class HeikinAshiStrategy(BaseStrategy):
    name = "heikin_ashi"
    description = "Heikin Ashi smooth-candle trend — fewer whipsaws than regular candles"

    def __init__(self, risk_manager: RiskManager,
                 require_no_wick: bool = True, confirm_bars: int = 2):
        super().__init__(risk_manager)
        self.require_no_wick = require_no_wick
        self.confirm_bars    = confirm_bars

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df  = super().prepare(df)
        ha  = compute_heikin_ashi(df)
        return pd.concat([df, ha], axis=1)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "ha_bull" not in df.columns:
            ha = compute_heikin_ashi(df)
            df = pd.concat([df, ha], axis=1)

        bull = df["ha_bull"]
        bear = ~df["ha_bull"]

        # Flip: N consecutive bull candles after a bear period
        bull_streak = bull.astype(int).groupby(
            (bull != bull.shift()).cumsum()
        ).cumcount() + 1

        bear_streak = bear.astype(int).groupby(
            (bear != bear.shift()).cumsum()
        ).cumcount() + 1

        flip_up   = (bull_streak == self.confirm_bars) & (bull)
        flip_down = (bear_streak == self.confirm_bars) & (bear)

        # Optional: only strong candles (no opposing wick)
        if self.require_no_wick:
            flip_up   &= df["ha_no_low_wick"]
            flip_down &= df["ha_no_up_wick"]

        # Trend filter: only trade in direction of EMA50
        trend_up   = df["close"] > df["ema_50"] if "ema_50" in df.columns else True
        trend_down = df["close"] < df["ema_50"] if "ema_50" in df.columns else True

        df["signal"] = 0
        df.loc[flip_up   & trend_up,   "signal"] = 1
        df.loc[flip_down & trend_down, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["ha_low"]  - atr * 0.5
        df["take_profit"] = df["close"]   + atr * 3.0

        return df
