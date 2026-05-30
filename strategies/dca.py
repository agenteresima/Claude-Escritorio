"""
DCA (Dollar-Cost Averaging) Strategy
Professional DCA with:
  - Safety orders (scale in on dips, like 3Commas)
  - Dynamic deviation thresholds
  - Take profit on the average entry price
  - Max safety orders limit

This is one of the most popular retail strategies and works
remarkably well in uptrending crypto markets.

Parameters:
  base_order_pct    : % of capital for first entry
  safety_order_pct  : % of capital per safety order (scales up)
  safety_deviation  : % drop from last entry to trigger safety order
  max_safety_orders : max number of DCA fills
  take_profit_pct   : TP from average entry price
  volume_scale      : multiply safety order size by this each time (2.0 = double)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from loguru import logger

from strategies.base import BaseStrategy
from risk.manager import RiskManager


@dataclass
class DCAPosition:
    entries:    list[float] = field(default_factory=list)
    sizes:      list[float] = field(default_factory=list)
    safety_count: int = 0

    @property
    def avg_entry(self) -> float:
        if not self.entries:
            return 0.0
        total_cost = sum(e * s for e, s in zip(self.entries, self.sizes))
        total_size = sum(self.sizes)
        return total_cost / total_size if total_size else 0.0

    @property
    def total_size(self) -> float:
        return sum(self.sizes)

    @property
    def last_entry(self) -> float:
        return self.entries[-1] if self.entries else 0.0

    def is_open(self) -> bool:
        return len(self.entries) > 0


class DCAStrategy(BaseStrategy):
    name = "dca"
    description = "Dollar-cost averaging with safety orders — professional 3Commas-style DCA"

    def __init__(self, risk_manager: RiskManager,
                 base_order_pct:    float = 0.02,
                 safety_order_pct:  float = 0.015,
                 safety_deviation:  float = 0.025,   # 2.5% dip triggers safety
                 max_safety_orders: int   = 4,
                 take_profit_pct:   float = 0.03,    # 3% from avg entry
                 volume_scale:      float = 1.5):    # each safety order 1.5× bigger
        super().__init__(risk_manager)
        self.base_order_pct    = base_order_pct
        self.safety_order_pct  = safety_order_pct
        self.safety_deviation  = safety_deviation
        self.max_safety_orders = max_safety_orders
        self.take_profit_pct   = take_profit_pct
        self.volume_scale      = volume_scale
        self._pos = DCAPosition()

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df       = df.copy()
        signals  = pd.Series(0,  index=df.index)
        stops    = pd.Series(0.0, index=df.index)
        targets  = pd.Series(0.0, index=df.index)

        rsi   = df["rsi_14"] if "rsi_14" in df.columns else pd.Series(50, index=df.index)
        trend = df["ema_50"]  if "ema_50"  in df.columns else df["close"]

        self._pos = DCAPosition()   # reset for each backtest run

        for i, (ts, row) in enumerate(df.iterrows()):
            price = float(row["close"])

            # ── Manage open position ──────────────────────────────────
            if self._pos.is_open():
                avg   = self._pos.avg_entry
                tp    = avg * (1 + self.take_profit_pct)
                sl    = avg * (1 - self.safety_deviation * (self.max_safety_orders + 1))

                # Take profit hit
                if price >= tp:
                    signals.iloc[i] = -1   # signal to close
                    stops.iloc[i]   = sl
                    targets.iloc[i] = tp
                    self._pos = DCAPosition()
                    continue

                # Safety order: price dropped safety_deviation% from last entry
                deviation = (self._pos.last_entry - price) / self._pos.last_entry
                if (deviation >= self.safety_deviation
                        and self._pos.safety_count < self.max_safety_orders):
                    scale  = self.volume_scale ** self._pos.safety_count
                    size   = (self.risk.portfolio.capital
                               * self.safety_order_pct * scale / price)
                    self._pos.entries.append(price)
                    self._pos.sizes.append(size)
                    self._pos.safety_count += 1
                    signals.iloc[i] = 1   # DCA buy
                    stops.iloc[i]   = sl
                    targets.iloc[i] = tp
                    logger.debug(f"DCA safety #{self._pos.safety_count} "
                                 f"@ {price:.2f} | avg={self._pos.avg_entry:.2f}")
                    continue

                stops.iloc[i]   = sl
                targets.iloc[i] = tp
                continue

            # ── Open new base order ───────────────────────────────────
            # Only enter when RSI is not overbought and price is above trend
            rsi_ok   = float(rsi.iloc[i]) < 65
            trend_ok = price > float(trend.iloc[i]) if hasattr(trend.iloc[i], '__float__') else True

            if rsi_ok and trend_ok:
                capital = self.risk.portfolio.capital
                size    = capital * self.base_order_pct / price
                self._pos.entries.append(price)
                self._pos.sizes.append(size)

                tp = price * (1 + self.take_profit_pct)
                sl = price * (1 - self.safety_deviation * (self.max_safety_orders + 1))
                signals.iloc[i] = 1
                stops.iloc[i]   = sl
                targets.iloc[i] = tp

        df["signal"]      = signals
        df["stop_loss"]   = stops
        df["take_profit"] = targets

        return df
