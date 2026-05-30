"""
Technical indicator library — pure numpy/pandas implementations.
Column naming follows pandas-ta conventions for drop-in compatibility.
"""
import pandas as pd
import numpy as np


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _rma(series: pd.Series, length: int) -> pd.Series:
    """Wilder's moving average (RMA), used in RSI / ATR."""
    alpha = 1.0 / length
    return series.ewm(alpha=alpha, adjust=False).mean()


def _true_range(high, low, close):
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr


# ─── Trend ────────────────────────────────────────────────────────────────────

def add_trend_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for p in [9, 21, 50, 100, 200]:
        df[f"ema_{p}"] = _ema(df["close"], p)

    # MACD (pandas-ta naming: MACD_12_26_9 / MACDs_12_26_9 / MACDh_12_26_9)
    ema12 = _ema(df["close"], 12)
    ema26 = _ema(df["close"], 26)
    macd_line = ema12 - ema26
    signal    = _ema(macd_line, 9)
    df["MACD_12_26_9"]  = macd_line
    df["MACDs_12_26_9"] = signal
    df["MACDh_12_26_9"] = macd_line - signal

    # ADX (pandas-ta naming: ADX_14 / DMP_14 / DMN_14)
    n = 14
    tr  = _true_range(df["high"], df["low"], df["close"])
    up  = df["high"].diff()
    dn  = -df["low"].diff()
    dm_p = np.where((up > dn) & (up > 0), up, 0.0)
    dm_n = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr14  = _rma(tr, n)
    dip    = pd.Series(dm_p, index=df.index)
    din    = pd.Series(dm_n, index=df.index)
    di_p   = 100 * _rma(dip, n) / atr14
    di_n   = 100 * _rma(din, n) / atr14
    dx     = 100 * (di_p - di_n).abs() / (di_p + di_n).replace(0, np.nan)
    df["ADX_14"] = _rma(dx, n)
    df["DMP_14"] = di_p
    df["DMN_14"] = di_n

    # Supertrend (pandas-ta naming: SUPERT_10_3.0 / SUPERTd_10_3.0)
    _compute_supertrend(df, length=10, multiplier=3.0)

    return df


def _compute_supertrend(df: pd.DataFrame, length: int = 10,
                        multiplier: float = 3.0) -> None:
    """Adds SUPERT_10_3.0, SUPERTd_10_3.0, SUPERTs_10_3.0, SUPERTl_10_3.0 in-place."""
    tr  = _true_range(df["high"], df["low"], df["close"])
    atr = _rma(tr, length)
    hl2 = (df["high"] + df["low"]) / 2
    up_band = hl2 + multiplier * atr
    dn_band = hl2 - multiplier * atr

    tag = f"{length}_{multiplier}"
    supert = pd.Series(np.nan, index=df.index)
    direction = pd.Series(1, index=df.index, dtype=int)

    up_arr  = up_band.values.copy()
    dn_arr  = dn_band.values.copy()
    close   = df["close"].values
    sup_arr = supert.values.copy()
    dir_arr = direction.values.copy()

    for i in range(1, len(close)):
        # Finalise bands
        up_arr[i] = up_arr[i] if up_arr[i] < up_arr[i-1] or close[i-1] > up_arr[i-1] else up_arr[i-1]
        dn_arr[i] = dn_arr[i] if dn_arr[i] > dn_arr[i-1] or close[i-1] < dn_arr[i-1] else dn_arr[i-1]

        if dir_arr[i-1] == -1:
            dir_arr[i] = -1 if close[i] < up_arr[i] else 1
        else:
            dir_arr[i] =  1 if close[i] > dn_arr[i] else -1

        sup_arr[i] = dn_arr[i] if dir_arr[i] == 1 else up_arr[i]

    df[f"SUPERT_{tag}"]  = sup_arr
    df[f"SUPERTd_{tag}"] = dir_arr
    df[f"SUPERTl_{tag}"] = np.where(dir_arr ==  1, dn_arr, np.nan)
    df[f"SUPERTs_{tag}"] = np.where(dir_arr == -1, up_arr, np.nan)


# ─── Momentum ─────────────────────────────────────────────────────────────────

def add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # MACD (also in trend, but duplicated here for standalone use)
    ema12 = _ema(df["close"], 12)
    ema26 = _ema(df["close"], 26)
    macd_line = ema12 - ema26
    signal    = _ema(macd_line, 9)
    if "MACD_12_26_9" not in df.columns:
        df["MACD_12_26_9"]  = macd_line
        df["MACDs_12_26_9"] = signal
        df["MACDh_12_26_9"] = macd_line - signal

    # RSI (Wilder)
    for n in [7, 14]:
        delta  = df["close"].diff()
        gain   = delta.clip(lower=0)
        loss   = (-delta).clip(lower=0)
        avg_g  = _rma(gain, n)
        avg_l  = _rma(loss, n)
        rs     = avg_g / avg_l.replace(0, np.nan)
        df[f"rsi_{n}"] = 100 - 100 / (1 + rs)

    # Stochastic (pandas-ta: STOCHk_14_3_3 / STOCHd_14_3_3)
    k_period, d_period, smooth = 14, 3, 3
    low_k  = df["low"].rolling(k_period).min()
    high_k = df["high"].rolling(k_period).max()
    stoch_k = 100 * (df["close"] - low_k) / (high_k - low_k).replace(0, np.nan)
    stoch_k_s = stoch_k.rolling(smooth).mean()
    df["STOCHk_14_3_3"] = stoch_k_s
    df["STOCHd_14_3_3"] = stoch_k_s.rolling(d_period).mean()

    # Williams %R
    df["willr"] = -100 * (df["high"].rolling(14).max() - df["close"]) / \
                  (df["high"].rolling(14).max() - df["low"].rolling(14).min()).replace(0, np.nan)

    # CCI
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    df["cci"] = (tp - tp.rolling(20).mean()) / (0.015 * mad)

    # MFI
    tp  = (df["high"] + df["low"] + df["close"]) / 3
    mf  = tp * df["volume"]
    pos = mf.where(tp > tp.shift(1), 0.0)
    neg = mf.where(tp < tp.shift(1), 0.0)
    pmf = pos.rolling(14).sum()
    nmf = neg.rolling(14).sum()
    df["mfi"] = 100 - 100 / (1 + pmf / nmf.replace(0, np.nan))

    return df


# ─── Volatility ───────────────────────────────────────────────────────────────

def add_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Bollinger Bands (pandas-ta: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0)
    mid  = df["close"].rolling(20).mean()
    std  = df["close"].rolling(20).std(ddof=0)
    df["BBL_20_2.0"] = mid - 2.0 * std
    df["BBM_20_2.0"] = mid
    df["BBU_20_2.0"] = mid + 2.0 * std
    df["BBB_20_2.0"] = (df["BBU_20_2.0"] - df["BBL_20_2.0"]) / df["BBM_20_2.0"] * 100
    df["BBP_20_2.0"] = (df["close"] - df["BBL_20_2.0"]) / \
                       (df["BBU_20_2.0"] - df["BBL_20_2.0"]).replace(0, np.nan)

    # ATR
    tr = _true_range(df["high"], df["low"], df["close"])
    df["atr_14"]  = _rma(tr, 14)
    df["atr_pct"] = df["atr_14"] / df["close"]

    # Keltner Channel (pandas-ta: KCLe_20_2, KCBe_20_2, KCUe_20_2)
    kc_mid = _ema(df["close"], 20)
    kc_atr = _rma(tr, 20)
    df["KCLe_20_2"] = kc_mid - 2.0 * kc_atr
    df["KCBe_20_2"] = kc_mid
    df["KCUe_20_2"] = kc_mid + 2.0 * kc_atr

    # Historical Volatility (annualised hourly)
    df["hv_20"] = df["close"].pct_change().rolling(20).std() * np.sqrt(365 * 24)

    return df


# ─── Volume ───────────────────────────────────────────────────────────────────

def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # OBV
    direction = np.sign(df["close"].diff().fillna(0))
    df["obv"] = (direction * df["volume"]).cumsum()

    # VWAP (session-based — resets daily when timestamp drops)
    tp = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (tp * df["volume"]).cumsum() / df["volume"].cumsum()

    # Volume SMA + ratio
    df["vol_sma_20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"]  = df["volume"] / df["vol_sma_20"].replace(0, np.nan)

    # CMF (Chaikin Money Flow)
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / \
          (df["high"] - df["low"]).replace(0, np.nan)
    df["cmf"] = (mfm * df["volume"]).rolling(20).sum() / \
                df["volume"].rolling(20).sum().replace(0, np.nan)

    return df


# ─── Support / Resistance ─────────────────────────────────────────────────────

def add_support_resistance(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    df["pivot_high"] = df["high"].rolling(window, center=True).max()
    df["pivot_low"]  = df["low"].rolling(window, center=True).min()

    # Donchian channels (pandas-ta: DCL_20_20, DCM_20_20, DCU_20_20)
    dcl = df["low"].rolling(window).min()
    dcu = df["high"].rolling(window).max()
    df["DCL_20_20"] = dcl
    df["DCM_20_20"] = (dcl + dcu) / 2
    df["DCU_20_20"] = dcu

    return df


# ─── All-in-one ───────────────────────────────────────────────────────────────

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = add_trend_indicators(df)
    df = add_momentum_indicators(df)
    df = add_volatility_indicators(df)
    df = add_volume_indicators(df)
    df = add_support_resistance(df)
    return df


# ─── Market regime ────────────────────────────────────────────────────────────

def compute_market_regime(df: pd.DataFrame) -> pd.Series:
    """
    Classify each bar as:
      1 = strong bull trend  (ADX > 25 and EMA slope positive)
      0 = sideways / ranging
     -1 = strong bear trend  (ADX > 25 and EMA slope negative)
    """
    adx_col = next((c for c in df.columns if c.startswith("ADX_")), None)
    if adx_col is None:
        df = add_trend_indicators(df)
        adx_col = next((c for c in df.columns if c.startswith("ADX_")), None)

    if "ema_50" not in df.columns:
        df["ema_50"] = _ema(df["close"], 50)

    adx        = df[adx_col]
    ema_slope  = df["ema_50"].diff(5) / df["ema_50"].shift(5)

    trending = adx > 25
    regime   = pd.Series(0, index=df.index, dtype=int)
    regime[trending & (ema_slope > 0)] =  1
    regime[trending & (ema_slope < 0)] = -1
    return regime
