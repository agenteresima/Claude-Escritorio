"""
Grid Trading Strategy
Places buy/sell orders at fixed price intervals creating a grid.
Profits from oscillation without predicting direction.
Best in: ranging/sideways markets (ADX < 20), high-frequency oscillation.

Inspired by: 3Commas grid bot, Binance grid trading, Pionex.

Grid math:
  - Lower bound  = current_price * (1 - range_pct)
  - Upper bound  = current_price * (1 + range_pct)
  - N grid lines spaced equally between bounds
  - Each line has a BUY order below and a SELL order above

Backtest approximation: simulate fills as price crosses grid levels.
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from loguru import logger

from strategies.base import BaseStrategy
from risk.manager import RiskManager


@dataclass
class GridLevel:
    price:      float
    order_type: str   # "buy" | "sell"
    filled:     bool = False
    fill_price: float = 0.0


class GridTradingStrategy(BaseStrategy):
    name = "grid_trading"
    description = "Price-grid oscillation — profits from sideways chop"

    def __init__(self, risk_manager: RiskManager,
                 n_grids: int = 10,
                 range_pct: float = 0.05,
                 only_in_range: bool = True):
        super().__init__(risk_manager)
        self.n_grids      = n_grids
        self.range_pct    = range_pct
        self.only_in_range = only_in_range
        self._grid: list[GridLevel] = []
        self._grid_center: float = 0.0
        self._lower: float = 0.0
        self._upper: float = 0.0

    def _build_grid(self, center_price: float):
        self._grid_center = center_price
        self._lower = center_price * (1 - self.range_pct)
        self._upper = center_price * (1 + self.range_pct)
        levels = np.linspace(self._lower, self._upper, self.n_grids + 1)
        self._grid = []
        for i, price in enumerate(levels):
            order_type = "buy" if price < center_price else "sell"
            self._grid.append(GridLevel(price=price, order_type=order_type))

    def _needs_rebuild(self, current_price: float) -> bool:
        if not self._grid:
            return True
        # Rebuild if price breaks out of grid by > 1 grid step
        step = (self._upper - self._lower) / self.n_grids
        return current_price < self._lower - step or current_price > self._upper + step

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df       = df.copy()
        signals  = pd.Series(0, index=df.index)
        stops    = pd.Series(df["close"] * 0.97, index=df.index)
        targets  = pd.Series(df["close"] * 1.03, index=df.index)

        adx_col  = next((c for c in df.columns if c.startswith("ADX_")), None)

        for i, (ts, row) in enumerate(df.iterrows()):
            price = float(row["close"])

            # Only grid-trade in ranging market
            if adx_col and self.only_in_range:
                if df[adx_col].iloc[i] > 25:
                    continue

            if self._needs_rebuild(price):
                self._build_grid(price)
                logger.debug(f"Grid rebuilt @ {price:.2f} "
                             f"[{self._lower:.2f} – {self._upper:.2f}]")

            # Check which grid levels price crossed
            for lvl in self._grid:
                if lvl.filled:
                    continue
                crossed_buy  = lvl.order_type == "buy"  and price <= lvl.price
                crossed_sell = lvl.order_type == "sell" and price >= lvl.price

                if crossed_buy:
                    lvl.filled     = True
                    lvl.fill_price = price
                    signals.iloc[i] = 1
                    # Stop below the next lower grid level
                    idx = self._grid.index(lvl)
                    sl  = self._grid[idx - 1].price if idx > 0 else price * 0.97
                    tp  = self._grid[idx + 1].price if idx < len(self._grid) - 1 else price * 1.03
                    stops.iloc[i]   = sl
                    targets.iloc[i] = tp
                    break

                elif crossed_sell and any(g.filled and g.order_type == "buy"
                                          for g in self._grid):
                    lvl.filled     = True
                    lvl.fill_price = price
                    signals.iloc[i] = -1
                    for g in self._grid:
                        if g.filled and g.order_type == "buy":
                            g.filled = False   # reset for re-entry
                    break

        df["signal"]      = signals
        df["stop_loss"]   = stops
        df["take_profit"] = targets

        n_buys  = (df["signal"] == 1).sum()
        n_sells = (df["signal"] == -1).sum()
        logger.debug(f"Grid: {n_buys} buy fills, {n_sells} sell fills | "
                     f"grids={self.n_grids} range±{self.range_pct*100:.1f}%")
        return df
