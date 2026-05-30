"""
Volume Profile Strategy
Institutional technique: identifies where most volume traded (Point of Control)
and High/Low Value Areas. Price gravitates to POC and bounces off VAH/VAL.

Used by: CME market profile traders, prop firms, hedge funds.

Concepts:
  POC  (Point of Control) : price level with highest traded volume
  VAH  (Value Area High)  : top of zone where 70% of volume occurred
  VAL  (Value Area Low)   : bottom of same zone

Trading logic:
  Long  : price pulls back to VAL / POC from above + bullish candle pattern
  Short : price rallies to VAH from below + bearish pattern
  Breakout: price closes cleanly above VAH / below VAL with volume surge
"""
import pandas as pd
import numpy as np
from strategies.base import BaseStrategy
from risk.manager import RiskManager


def compute_volume_profile(df: pd.DataFrame, n_bins: int = 50,
                            period: int = 200) -> pd.DataFrame:
    """
    Compute rolling Volume Profile: POC, VAH, VAL for each bar
    based on the last `period` candles.
    Returns df with added columns.
    """
    df = df.copy()
    poc_list  = []
    vah_list  = []
    val_list  = []

    for i in range(len(df)):
        start = max(0, i - period)
        chunk = df.iloc[start:i+1]

        if len(chunk) < 10:
            poc_list.append(np.nan)
            vah_list.append(np.nan)
            val_list.append(np.nan)
            continue

        # Bin prices
        lo, hi = chunk["low"].min(), chunk["high"].max()
        bins   = np.linspace(lo, hi, n_bins + 1)
        bucket_vol = np.zeros(n_bins)

        for _, row in chunk.iterrows():
            # Distribute bar's volume across bins it spans
            bar_lo = row["low"]
            bar_hi = row["high"]
            bar_vol = row["volume"]
            spans  = np.where((bins[:-1] <= bar_hi) & (bins[1:] >= bar_lo))[0]
            if len(spans) > 0:
                bucket_vol[spans] += bar_vol / len(spans)

        poc_bin  = int(np.argmax(bucket_vol))
        poc_price = (bins[poc_bin] + bins[poc_bin + 1]) / 2

        # Value Area: 70% of total volume centred around POC
        total_vol    = bucket_vol.sum()
        target_vol   = total_vol * 0.70
        accum        = bucket_vol[poc_bin]
        lo_idx = hi_idx = poc_bin

        while accum < target_vol:
            up_vol = bucket_vol[hi_idx + 1] if hi_idx + 1 < n_bins else 0
            dn_vol = bucket_vol[lo_idx - 1] if lo_idx - 1 >= 0     else 0
            if up_vol >= dn_vol and hi_idx + 1 < n_bins:
                hi_idx += 1
                accum  += up_vol
            elif lo_idx - 1 >= 0:
                lo_idx -= 1
                accum  += dn_vol
            else:
                break

        poc_list.append(poc_price)
        vah_list.append((bins[hi_idx] + bins[hi_idx + 1]) / 2)
        val_list.append((bins[lo_idx] + bins[lo_idx + 1]) / 2)

    df["vp_poc"] = poc_list
    df["vp_vah"] = vah_list
    df["vp_val"] = val_list
    return df


class VolumeProfileStrategy(BaseStrategy):
    name = "volume_profile"
    description = "Institutional volume profile — POC/VAH/VAL support-resistance trading"

    def __init__(self, risk_manager: RiskManager,
                 n_bins: int = 30, period: int = 150,
                 proximity_pct: float = 0.005):
        super().__init__(risk_manager)
        self.n_bins       = n_bins
        self.period       = period
        self.proximity    = proximity_pct   # how close to level = "at level"

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare(df)
        from loguru import logger
        logger.debug("Computing volume profile (may take a moment)...")
        return compute_volume_profile(df, self.n_bins, self.period)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "vp_poc" not in df.columns:
            df = compute_volume_profile(df, self.n_bins, self.period)

        poc = df["vp_poc"]
        vah = df["vp_vah"]
        val = df["vp_val"]
        close = df["close"]

        # Near a level = within proximity_pct %
        near_val = (close - val).abs() / val < self.proximity
        near_poc = (close - poc).abs() / poc < self.proximity
        near_vah = (close - vah).abs() / vah < self.proximity

        # Confirm with candle direction
        bull_candle = close > df["open"]
        bear_candle = close < df["open"]

        # Breakout above VAH with volume
        vol_surge   = df["vol_ratio"] > 1.5 if "vol_ratio" in df.columns else True
        break_above = (close > vah) & (df["close"].shift(1) <= vah.shift(1)) & vol_surge
        break_below = (close < val) & (df["close"].shift(1) >= val.shift(1)) & vol_surge

        df["signal"] = 0
        # Bounce long at VAL or POC
        df.loc[(near_val | near_poc) & bull_candle, "signal"] = 1
        # Bounce short at VAH
        df.loc[near_vah & bear_candle, "signal"] = -1
        # Breakout
        df.loc[break_above, "signal"] = 1
        df.loc[break_below, "signal"] = -1

        atr = df["atr_14"] if "atr_14" in df.columns else close * 0.02
        df["stop_loss"]   = close - atr * 1.5
        df["take_profit"] = close + atr * 3.0

        return df
