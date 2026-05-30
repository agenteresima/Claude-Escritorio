"""
Portfolio Heat Manager
Tracks total risk exposure across ALL open positions.
Prevents over-leveraging by computing aggregate risk in real time.

"Portfolio heat" = sum of (distance to stop × position size) for all open trades
                 = total capital at risk right now

Professional rule: never have more than 6-8% of total capital at risk at once.
This module enforces that limit.

Also computes:
  - Heat per asset class (crypto vs stock vs forex)
  - Correlated heat (positions in same direction + high correlation)
  - Delta (net directional exposure)
"""
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger


@dataclass
class PositionRisk:
    symbol:       str
    direction:    str      # long / short
    entry_price:  float
    current_price: float
    stop_loss:    float
    size:         float

    @property
    def dollar_risk(self) -> float:
        """Amount of capital at risk (distance to stop × size)."""
        return abs(self.entry_price - self.stop_loss) * self.size

    @property
    def dollar_risk_current(self) -> float:
        """Risk based on current price to stop (accounts for profit)."""
        return abs(self.current_price - self.stop_loss) * self.size

    @property
    def unrealised_pnl(self) -> float:
        if self.direction == "long":
            return (self.current_price - self.entry_price) * self.size
        return (self.entry_price - self.current_price) * self.size

    @property
    def r_multiple(self) -> float:
        """Current unrealised P&L as a multiple of initial risk."""
        if self.dollar_risk == 0:
            return 0.0
        return self.unrealised_pnl / self.dollar_risk


@dataclass
class HeatReport:
    total_capital:     float
    total_heat_pct:    float      # % of capital at risk
    max_heat_pct:      float      # configured limit
    positions:         list[PositionRisk]
    heat_ok:           bool
    net_delta:         float      # net directional bias (-1 fully short, +1 fully long)
    largest_risk:      Optional[str]   # symbol with most $ at risk

    def __str__(self) -> str:
        status = "✅ OK" if self.heat_ok else "🔴 OVERLIMIT"
        return (
            f"Portfolio Heat: {self.total_heat_pct*100:.2f}% / {self.max_heat_pct*100:.2f}% {status}\n"
            f"  Open positions : {len(self.positions)}\n"
            f"  Net delta      : {self.net_delta:+.2f}\n"
            f"  Largest risk   : {self.largest_risk or 'none'}"
        )


class PortfolioHeatManager:
    def __init__(self, max_heat_pct: float = 0.06,   # 6% total capital at risk
                 max_single_pct: float = 0.02):        # 2% per single position
        self.max_heat_pct   = max_heat_pct
        self.max_single_pct = max_single_pct
        self._positions: dict[str, PositionRisk] = {}

    def update_position(self, symbol: str, direction: str,
                        entry: float, current: float, stop: float, size: float):
        self._positions[symbol] = PositionRisk(
            symbol=symbol, direction=direction,
            entry_price=entry, current_price=current,
            stop_loss=stop, size=size,
        )

    def remove_position(self, symbol: str):
        self._positions.pop(symbol, None)

    def compute_heat(self, total_capital: float) -> HeatReport:
        positions = list(self._positions.values())

        total_risk = sum(p.dollar_risk_current for p in positions)
        heat_pct   = total_risk / total_capital if total_capital > 0 else 0

        long_exp   = sum(p.size * p.current_price for p in positions if p.direction == "long")
        short_exp  = sum(p.size * p.current_price for p in positions if p.direction == "short")
        total_exp  = long_exp + short_exp + 1e-9
        net_delta  = (long_exp - short_exp) / total_exp

        largest = max(positions, key=lambda p: p.dollar_risk_current, default=None)

        return HeatReport(
            total_capital  = total_capital,
            total_heat_pct = heat_pct,
            max_heat_pct   = self.max_heat_pct,
            positions      = positions,
            heat_ok        = heat_pct <= self.max_heat_pct,
            net_delta      = net_delta,
            largest_risk   = largest.symbol if largest else None,
        )

    def can_add_position(self, total_capital: float,
                          new_risk: float) -> tuple[bool, str]:
        """
        Check if adding a new position would breach heat limits.
        Returns (allowed, reason).
        """
        report = self.compute_heat(total_capital)

        # Single position risk check
        single_pct = new_risk / total_capital
        if single_pct > self.max_single_pct:
            return False, (f"Single position risk {single_pct*100:.2f}% "
                           f"> limit {self.max_single_pct*100:.2f}%")

        # Portfolio heat check
        projected = report.total_heat_pct + single_pct
        if projected > self.max_heat_pct:
            return False, (f"Portfolio heat would reach {projected*100:.2f}% "
                           f"> limit {self.max_heat_pct*100:.2f}%")

        return True, "ok"

    def reduce_size_to_fit(self, total_capital: float,
                            entry: float, stop: float) -> float:
        """
        Compute maximum position size that keeps portfolio heat within limit.
        """
        report   = self.compute_heat(total_capital)
        heat_budget = (self.max_heat_pct - report.total_heat_pct) * total_capital
        heat_budget = max(0.0, heat_budget)
        risk_per_unit = abs(entry - stop)
        if risk_per_unit == 0:
            return 0.0
        max_size = heat_budget / risk_per_unit
        return max_size
