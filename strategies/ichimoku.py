"""
Ichimoku Cloud Strategy
Japanese institutional system — 5 components give a complete market picture.
Most reliable when all signals align (called 'ichimoku confluence').

Components used:
  Tenkan (9)  — conversion line (fast trend)
  Kijun  (26) — base line      (slow trend / stop reference)
  Senkou A/B  — cloud (support/resistance zone)
  Chikou      — lagging span   (confirmation)

Entry conditions (TK cross strategy — most backtested ichimoku variant):
  Long  : Tenkan crosses above Kijun ABOVE the cloud
           + price > cloud + chikou above price 26 bars ago
  Short : Tenkan crosses below Kijun BELOW the cloud
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


def _ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    high  = df["high"]
    low   = df["low"]
    close = df["close"]

    tenkan  = (high.rolling(9).max()  + low.rolling(9).min())  / 2
    kijun   = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    chikou   = close.shift(-26)

    df = df.copy()
    df["ichi_tenkan"]  = tenkan
    df["ichi_kijun"]   = kijun
    df["ichi_sa"]      = senkou_a
    df["ichi_sb"]      = senkou_b
    df["ichi_chikou"]  = chikou
    df["ichi_cloud_top"]    = df[["ichi_sa", "ichi_sb"]].max(axis=1)
    df["ichi_cloud_bottom"] = df[["ichi_sa", "ichi_sb"]].min(axis=1)
    return df


class IchimokuStrategy(BaseStrategy):
    name = "ichimoku"
    description = "Ichimoku TK-cross with cloud and chikou confluence"

    def __init__(self, risk_manager: RiskManager):
        super().__init__(risk_manager)

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare(df)
        return _ichimoku(df)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "ichi_tenkan" not in df.columns:
            df = _ichimoku(df)

        tk     = df["ichi_tenkan"]
        kj     = df["ichi_kijun"]
        cloud_t = df["ichi_cloud_top"]
        cloud_b = df["ichi_cloud_bottom"]

        tk_cross_up   = (tk > kj) & (tk.shift(1) <= kj.shift(1))
        tk_cross_down = (tk < kj) & (tk.shift(1) >= kj.shift(1))

        above_cloud = df["close"] > cloud_t
        below_cloud = df["close"] < cloud_b

        # Chikou confirmation (current close vs price 26 bars back)
        chikou_bull = df["close"] > df["close"].shift(26)
        chikou_bear = df["close"] < df["close"].shift(26)

        df["signal"] = 0
        df.loc[tk_cross_up   & above_cloud & chikou_bull, "signal"] =  1
        df.loc[tk_cross_down & below_cloud & chikou_bear, "signal"] = -1

        # Kijun acts as natural stop
        df["stop_loss"]   = df["ichi_kijun"]
        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["take_profit"] = df["close"] + atr * 4.0

        return df
