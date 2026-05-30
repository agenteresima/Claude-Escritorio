"""
Regime-Adaptive Strategy
Automatically switches between trend-following and mean-reversion
based on the current market regime.

Regime detection (Hidden Markov Model approach simplified):
  - High ADX + rising price  → TREND_UP    → use TrendEMA
  - High ADX + falling price → TREND_DOWN  → short or flat
  - Low ADX + tight BB       → RANGING     → use MeanReversion
  - Low ADX + expanding BB   → BREAKOUT    → use Breakout strategy

This is the "holy grail" approach: no single strategy works in all markets,
so we dynamically select the best one.
"""
import pandas as pd
import numpy as np
from enum import Enum
from loguru import logger

from strategies.base import BaseStrategy
from strategies.trend_ema import TrendEMAStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.breakout import BreakoutStrategy
from risk.manager import RiskManager


class Regime(Enum):
    TREND_UP    = "trend_up"
    TREND_DOWN  = "trend_down"
    RANGING     = "ranging"
    BREAKOUT    = "breakout"
    UNDEFINED   = "undefined"


def detect_regime(df: pd.DataFrame) -> pd.Series:
    """
    Returns a Series of Regime enum values for each bar.
    """
    adx_col = next((c for c in df.columns if c.startswith("ADX_")), None)
    bb_up   = next((c for c in df.columns if "BBU_" in c), None)
    bb_low  = next((c for c in df.columns if "BBL_" in c), None)
    kc_up   = next((c for c in df.columns if "KCUe_" in c), None)
    kc_low  = next((c for c in df.columns if "KCLe_" in c), None)

    regimes = pd.Series(Regime.UNDEFINED, index=df.index)

    if adx_col:
        adx       = df[adx_col]
        trending  = adx > 25
        ranging   = adx <= 25
        up_trend  = df["close"] > df["ema_50"] if "ema_50" in df.columns else pd.Series(True, index=df.index)

        # Squeeze: BB inside KC
        squeeze = pd.Series(False, index=df.index)
        if bb_up and bb_low and kc_up and kc_low:
            squeeze = (df[bb_up] < df[kc_up]) & (df[bb_low] > df[kc_low])

        # BB width expanding (breakout candidate)
        if bb_up and bb_low:
            bb_width = df[bb_up] - df[bb_low]
            bb_expanding = bb_width > bb_width.rolling(10).mean()
        else:
            bb_expanding = pd.Series(False, index=df.index)

        regimes[trending & up_trend]             = Regime.TREND_UP
        regimes[trending & ~up_trend]            = Regime.TREND_DOWN
        regimes[ranging  & ~squeeze]             = Regime.RANGING
        regimes[ranging  & squeeze & bb_expanding] = Regime.BREAKOUT

    return regimes


class RegimeAdaptiveStrategy(BaseStrategy):
    name = "regime_adaptive"
    description = "Auto-switches trend/mean-reversion/breakout based on market regime"

    def __init__(self, risk_manager: RiskManager):
        super().__init__(risk_manager)
        self._trend  = TrendEMAStrategy(risk_manager)
        self._mean   = MeanReversionStrategy(risk_manager)
        self._break  = BreakoutStrategy(risk_manager)
        self._regime_counts: dict = {}

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df       = df.copy()
        regimes  = detect_regime(df)
        df["regime"] = regimes.map(lambda r: r.value if isinstance(r, Regime) else r)

        # Run each sub-strategy once on the full df
        t_df = self._trend.generate_signals(df.copy())
        m_df = self._mean.generate_signals(df.copy())
        b_df = self._break.generate_signals(df.copy())

        df["signal"]      = 0
        df["stop_loss"]   = df["close"] * 0.97
        df["take_profit"] = df["close"] * 1.06

        for col in ("signal", "stop_loss", "take_profit"):
            df.loc[regimes == Regime.TREND_UP,   col] = t_df.loc[regimes == Regime.TREND_UP,   col]
            df.loc[regimes == Regime.RANGING,    col] = m_df.loc[regimes == Regime.RANGING,    col]
            df.loc[regimes == Regime.BREAKOUT,   col] = b_df.loc[regimes == Regime.BREAKOUT,   col]
        # TREND_DOWN and UNDEFINED → signal stays 0 (flat)

        # Log regime distribution
        counts = regimes.value_counts()
        logger.debug(f"Regime distribution: {counts.to_dict()}")

        return df
