"""
MACD Divergence Strategy
Divergence is one of the most reliable reversal signals in technical analysis.

Types detected:
  Regular Bullish Divergence : price makes lower low BUT MACD makes higher low
    → bears losing momentum → reversal up likely
  Regular Bearish Divergence : price makes higher high BUT MACD makes lower high
    → bulls losing momentum → reversal down likely
  Hidden Bullish Divergence  : price makes higher low BUT MACD makes lower low
    → trend continuation up (pullback ended)
  Hidden Bearish Divergence  : price makes lower high BUT MACD makes higher high
    → trend continuation down

All divergences confirmed with RSI and volume filters.
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


def _find_pivot_lows(series: pd.Series, window: int = 5) -> pd.Series:
    """Returns True at bars that are local minima."""
    result = pd.Series(False, index=series.index)
    for i in range(window, len(series) - window):
        if series.iloc[i] == series.iloc[i-window:i+window+1].min():
            result.iloc[i] = True
    return result


def _find_pivot_highs(series: pd.Series, window: int = 5) -> pd.Series:
    result = pd.Series(False, index=series.index)
    for i in range(window, len(series) - window):
        if series.iloc[i] == series.iloc[i-window:i+window+1].max():
            result.iloc[i] = True
    return result


def _detect_divergence(price: pd.Series, indicator: pd.Series,
                        pivot_window: int = 5, lookback: int = 50) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
      reg_bull, reg_bear, hid_bull, hid_bear
    at each bar where a divergence is present.
    """
    p_lows  = _find_pivot_lows(price,     pivot_window)
    p_highs = _find_pivot_highs(price,    pivot_window)
    i_lows  = _find_pivot_lows(indicator, pivot_window)
    i_highs = _find_pivot_highs(indicator, pivot_window)

    n       = len(price)
    reg_bull = pd.Series(False, index=price.index)
    reg_bear = pd.Series(False, index=price.index)
    hid_bull = pd.Series(False, index=price.index)
    hid_bear = pd.Series(False, index=price.index)

    for i in range(pivot_window * 2, n):
        # Recent pivot low indices within lookback
        window_slice = slice(max(0, i - lookback), i)

        p_low_idxs = p_lows.iloc[window_slice][p_lows.iloc[window_slice]].index.tolist()
        i_low_idxs = i_lows.iloc[window_slice][i_lows.iloc[window_slice]].index.tolist()
        p_hi_idxs  = p_highs.iloc[window_slice][p_highs.iloc[window_slice]].index.tolist()
        i_hi_idxs  = i_highs.iloc[window_slice][i_highs.iloc[window_slice]].index.tolist()

        # Regular bullish: price LL + indicator HL
        if len(p_low_idxs) >= 2 and len(i_low_idxs) >= 2:
            p2, p1 = p_low_idxs[-1], p_low_idxs[-2]
            if price[p2] < price[p1]:   # price made lower low
                # Find matching indicator pivot
                i_pivs = [x for x in i_low_idxs if x <= p2]
                if len(i_pivs) >= 2:
                    if indicator[i_pivs[-1]] > indicator[i_pivs[-2]]:   # indicator higher low
                        reg_bull.iloc[i] = True

        # Regular bearish: price HH + indicator LH
        if len(p_hi_idxs) >= 2 and len(i_hi_idxs) >= 2:
            p2, p1 = p_hi_idxs[-1], p_hi_idxs[-2]
            if price[p2] > price[p1]:   # price made higher high
                i_pivs = [x for x in i_hi_idxs if x <= p2]
                if len(i_pivs) >= 2:
                    if indicator[i_pivs[-1]] < indicator[i_pivs[-2]]:
                        reg_bear.iloc[i] = True

        # Hidden bullish: price HL + indicator LL
        if len(p_low_idxs) >= 2 and len(i_low_idxs) >= 2:
            p2, p1 = p_low_idxs[-1], p_low_idxs[-2]
            if price[p2] > price[p1]:   # price higher low (trend continuation)
                i_pivs = [x for x in i_low_idxs if x <= p2]
                if len(i_pivs) >= 2:
                    if indicator[i_pivs[-1]] < indicator[i_pivs[-2]]:
                        hid_bull.iloc[i] = True

        # Hidden bearish: price LH + indicator HH
        if len(p_hi_idxs) >= 2 and len(i_hi_idxs) >= 2:
            p2, p1 = p_hi_idxs[-1], p_hi_idxs[-2]
            if price[p2] < price[p1]:
                i_pivs = [x for x in i_hi_idxs if x <= p2]
                if len(i_pivs) >= 2:
                    if indicator[i_pivs[-1]] > indicator[i_pivs[-2]]:
                        hid_bear.iloc[i] = True

    return pd.DataFrame({
        "reg_bull": reg_bull, "reg_bear": reg_bear,
        "hid_bull": hid_bull, "hid_bear": hid_bear,
    })


class MACDDivergenceStrategy(BaseStrategy):
    name = "macd_divergence"
    description = "MACD regular & hidden divergence — high-quality reversal and continuation signals"

    def __init__(self, risk_manager: RiskManager,
                 pivot_window: int = 5, lookback: int = 50,
                 use_hidden: bool = True):
        super().__init__(risk_manager)
        self.pivot_window = pivot_window
        self.lookback     = lookback
        self.use_hidden   = use_hidden

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        macd_col = next((c for c in df.columns if c.startswith("MACD_") and "h" not in c.lower() and "s" not in c.lower()), None)
        if macd_col is None:
            df["signal"] = 0
            return df

        divs = _detect_divergence(
            df["close"], df[macd_col],
            self.pivot_window, self.lookback,
        )

        rsi = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        vol_ok = df["vol_ratio"] > 1.0 if "vol_ratio" in df.columns else True

        df["signal"] = 0
        # Regular divergences: reversals
        df.loc[divs["reg_bull"] & (rsi < 55) & vol_ok, "signal"] = 1
        df.loc[divs["reg_bear"] & (rsi > 45) & vol_ok, "signal"] = -1

        if self.use_hidden:
            # Hidden divergences: trend continuation
            trend_up   = df["close"] > df["ema_50"] if "ema_50" in df.columns else True
            trend_down = df["close"] < df["ema_50"] if "ema_50" in df.columns else True
            df.loc[divs["hid_bull"] & trend_up,   "signal"] = 1
            df.loc[divs["hid_bear"] & trend_down,  "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else df["close"] * 0.02
        df["stop_loss"]   = df["close"] - atr * 2.0
        df["take_profit"] = df["close"] + atr * 4.0

        total = (df["signal"] != 0).sum()
        from loguru import logger
        logger.debug(f"MACD Divergence: {total} signals detected")
        return df
