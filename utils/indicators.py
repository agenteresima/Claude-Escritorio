"""
Technical indicator library — pure pandas-ta wrappers with sane defaults.
All functions receive a DataFrame with OHLCV columns and return it enriched.
"""
import pandas as pd
import pandas_ta as ta
import numpy as np


def add_trend_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # EMAs (most reliable trend signals)
    for period in [9, 21, 50, 100, 200]:
        df[f"ema_{period}"] = ta.ema(df["close"], length=period)
    # MACD
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    # ADX (trend strength)
    adx = ta.adx(df["high"], df["low"], df["close"], length=14)
    df = pd.concat([df, adx], axis=1)
    # Supertrend (great for trend-following)
    st = ta.supertrend(df["high"], df["low"], df["close"], length=10, multiplier=3.0)
    df = pd.concat([df, st], axis=1)
    return df


def add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # RSI
    df["rsi_14"] = ta.rsi(df["close"], length=14)
    df["rsi_7"] = ta.rsi(df["close"], length=7)
    # Stochastic
    stoch = ta.stoch(df["high"], df["low"], df["close"])
    df = pd.concat([df, stoch], axis=1)
    # Williams %R
    df["willr"] = ta.willr(df["high"], df["low"], df["close"], length=14)
    # CCI
    df["cci"] = ta.cci(df["high"], df["low"], df["close"], length=20)
    # MFI (Money Flow Index — combines price + volume)
    df["mfi"] = ta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14)
    return df


def add_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Bollinger Bands
    bb = ta.bbands(df["close"], length=20, std=2.0)
    df = pd.concat([df, bb], axis=1)
    # ATR (essential for position sizing and stops)
    df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["atr_pct"] = df["atr_14"] / df["close"]
    # Keltner Channel
    kc = ta.kc(df["high"], df["low"], df["close"], length=20, scalar=2.0)
    df = pd.concat([df, kc], axis=1)
    # Historical Volatility
    df["hv_20"] = df["close"].pct_change().rolling(20).std() * np.sqrt(365 * 24)
    return df


def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # OBV
    df["obv"] = ta.obv(df["close"], df["volume"])
    # VWAP (intraday reference)
    df["vwap"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
    # Volume SMA for breakout confirmation
    df["vol_sma_20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / df["vol_sma_20"]
    # Chaikin Money Flow
    df["cmf"] = ta.cmf(df["high"], df["low"], df["close"], df["volume"], length=20)
    return df


def add_support_resistance(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    df["pivot_high"] = df["high"].rolling(window, center=True).max()
    df["pivot_low"] = df["low"].rolling(window, center=True).min()
    # Donchian channels (breakout levels)
    don = ta.donchian(df["high"], df["low"], lower_length=window, upper_length=window)
    df = pd.concat([df, don], axis=1)
    return df


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add the full indicator suite in one call."""
    df = add_trend_indicators(df)
    df = add_momentum_indicators(df)
    df = add_volatility_indicators(df)
    df = add_volume_indicators(df)
    df = add_support_resistance(df)
    return df


def compute_market_regime(df: pd.DataFrame) -> pd.Series:
    """
    Simple regime classifier:
      1 = strong bull trend
      0 = ranging / sideways
     -1 = strong bear trend
    Based on ADX + EMA slope (same approach as Freqtrade's HeikinAshi regime filter).
    """
    adx_col = [c for c in df.columns if c.startswith("ADX_")]
    if not adx_col:
        df = add_trend_indicators(df)
        adx_col = [c for c in df.columns if c.startswith("ADX_")]

    adx = df[adx_col[0]]
    ema_slope = df["ema_50"].diff(5) / df["ema_50"].shift(5)

    regime = pd.Series(0, index=df.index)
    regime[adx > 25] = np.where(ema_slope[adx > 25] > 0, 1, -1)
    return regime
