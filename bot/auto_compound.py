"""
Auto-compound module — reinvests profits automatically.
Also handles periodic rebalancing when capital allocation drifts.

Compound modes:
  REINVEST_ALL    : 100% of profits back into trading capital
  REINVEST_HALF   : 50% reinvested, 50% "withdrawn" (simulated)
  FIXED_WITHDRAW  : withdraw a fixed amount per period, compound the rest
  PERCENT_WITHDRAW: withdraw X% per period, compound the rest

Rebalancing:
  - Checks if any pair's allocation drifted > threshold from equal weight
  - Generates rebalance orders when drift detected
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from loguru import logger

from data.database import get_state, set_state, save_equity, trade_stats


class CompoundMode(Enum):
    REINVEST_ALL     = "reinvest_all"
    REINVEST_HALF    = "reinvest_half"
    FIXED_WITHDRAW   = "fixed_withdraw"
    PERCENT_WITHDRAW = "percent_withdraw"


@dataclass
class CompoundState:
    initial_capital:   float
    current_capital:   float
    total_withdrawn:   float = 0.0
    total_compounded:  float = 0.0
    last_compound_ts:  Optional[datetime] = None
    compound_count:    int = 0
    compound_log:      list[dict] = field(default_factory=list)

    @property
    def total_return_pct(self) -> float:
        return (self.current_capital + self.total_withdrawn - self.initial_capital) / self.initial_capital * 100

    @property
    def net_profit(self) -> float:
        return self.current_capital + self.total_withdrawn - self.initial_capital


class AutoCompounder:
    def __init__(self,
                 initial_capital: float,
                 mode: CompoundMode = CompoundMode.REINVEST_ALL,
                 compound_interval_days: int = 7,
                 withdraw_amount: float = 0.0,
                 withdraw_pct: float = 0.20):
        self.mode     = mode
        self.interval = timedelta(days=compound_interval_days)
        self.withdraw_amount = withdraw_amount
        self.withdraw_pct    = withdraw_pct

        # Load or init state
        saved = get_state("compound_state")
        if saved:
            self.state = CompoundState(**saved)
        else:
            self.state = CompoundState(
                initial_capital = initial_capital,
                current_capital = initial_capital,
            )
            self._save()

    def _save(self):
        d = {
            "initial_capital":  self.state.initial_capital,
            "current_capital":  self.state.current_capital,
            "total_withdrawn":  self.state.total_withdrawn,
            "total_compounded": self.state.total_compounded,
            "last_compound_ts": self.state.last_compound_ts.isoformat()
                                if self.state.last_compound_ts else None,
            "compound_count":   self.state.compound_count,
            "compound_log":     self.state.compound_log[-50:],  # keep last 50
        }
        set_state("compound_state", d)

    def should_compound(self) -> bool:
        if self.state.last_compound_ts is None:
            return False
        return datetime.utcnow() - self.state.last_compound_ts >= self.interval

    def run(self, current_equity: float) -> dict:
        """
        Execute compound cycle. Call periodically (e.g., weekly).
        Returns dict with actions taken.
        """
        prev_capital = self.state.current_capital
        profit       = current_equity - prev_capital
        self.state.current_capital = current_equity
        self.state.last_compound_ts = datetime.utcnow()
        self.state.compound_count   += 1

        actions = {"mode": self.mode.value, "profit": profit, "prev_capital": prev_capital}

        if profit <= 0:
            logger.info(f"AutoCompound: no profit to compound ({profit:.2f})")
            actions["compounded"] = 0
            actions["withdrawn"]  = 0
            self._save()
            return actions

        if self.mode == CompoundMode.REINVEST_ALL:
            compounded = profit
            withdrawn  = 0.0

        elif self.mode == CompoundMode.REINVEST_HALF:
            compounded = profit * 0.50
            withdrawn  = profit * 0.50

        elif self.mode == CompoundMode.FIXED_WITHDRAW:
            withdrawn  = min(self.withdraw_amount, profit)
            compounded = profit - withdrawn

        elif self.mode == CompoundMode.PERCENT_WITHDRAW:
            withdrawn  = profit * self.withdraw_pct
            compounded = profit * (1 - self.withdraw_pct)

        else:
            compounded = profit
            withdrawn  = 0.0

        self.state.total_withdrawn  += withdrawn
        self.state.total_compounded += compounded
        self.state.compound_log.append({
            "ts":         datetime.utcnow().isoformat(),
            "profit":     round(profit, 2),
            "compounded": round(compounded, 2),
            "withdrawn":  round(withdrawn, 2),
            "equity":     round(current_equity, 2),
        })

        actions["compounded"]     = round(compounded, 2)
        actions["withdrawn"]      = round(withdrawn, 2)
        actions["new_capital"]    = round(self.state.current_capital, 2)
        actions["total_return_%"] = round(self.state.total_return_pct, 2)

        logger.info(f"AutoCompound cycle #{self.state.compound_count}: "
                    f"profit={profit:.2f} | compounded={compounded:.2f} | "
                    f"withdrawn={withdrawn:.2f} | total_return={self.state.total_return_pct:.1f}%")
        self._save()
        return actions

    def rebalance_check(self, pair_equities: dict[str, float]) -> list[str]:
        """
        Check if any pair's allocation has drifted more than 20% from equal weight.
        Returns list of pairs that need rebalancing.
        """
        if not pair_equities:
            return []
        total    = sum(pair_equities.values())
        target   = total / len(pair_equities)
        drifted  = []
        for pair, equity in pair_equities.items():
            drift = abs(equity - target) / target
            if drift > 0.20:
                drifted.append(pair)
                logger.info(f"Rebalance needed: {pair} drifted {drift*100:.1f}% from target")
        return drifted

    @property
    def summary(self) -> str:
        s = self.state
        return (
            f"AutoCompounder | mode={self.mode.value}\n"
            f"  Initial capital   : {s.initial_capital:,.2f}\n"
            f"  Current capital   : {s.current_capital:,.2f}\n"
            f"  Total compounded  : {s.total_compounded:,.2f}\n"
            f"  Total withdrawn   : {s.total_withdrawn:,.2f}\n"
            f"  Net profit        : {s.net_profit:,.2f}\n"
            f"  Total return      : {s.total_return_pct:.2f}%\n"
            f"  Compound cycles   : {s.compound_count}"
        )
