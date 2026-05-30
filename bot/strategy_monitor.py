"""
Strategy performance decay detector.
Monitors live Sharpe ratio in a rolling window.
If performance drops significantly below the backtest benchmark → alert.

Professional trading firms (Winton, AHL) use similar "strategy health" monitors
to detect when a strategy has stopped working (regime change, market structure shift).

Thresholds:
  - WARNING  : rolling Sharpe drops > 50% below backtest Sharpe
  - CRITICAL  : rolling Sharpe < 0 for 2+ consecutive windows
  - DEGRADED : win rate drops > 20pp below backtest win rate
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger

from bot.notifier import notify
from data.database import get_trade_history, get_equity_history


class HealthStatus(Enum):
    HEALTHY   = "healthy"
    WARNING   = "warning"
    CRITICAL  = "critical"
    DEGRADED  = "degraded"
    PAUSED    = "paused"
    NO_DATA   = "no_data"


@dataclass
class StrategyHealth:
    strategy:         str
    status:           HealthStatus
    rolling_sharpe:   float
    baseline_sharpe:  float
    rolling_win_rate: float
    baseline_win_rate: float
    recent_trades:    int
    message:          str
    checked_at:       datetime = field(default_factory=datetime.utcnow)


class StrategyMonitor:
    def __init__(self,
                 strategy_name:    str,
                 baseline_sharpe:  float = 1.0,
                 baseline_win_rate: float = 55.0,
                 window_trades:    int   = 20,
                 sharpe_drop_pct:  float = 0.50,
                 win_rate_drop_pp: float = 20.0):
        self.strategy_name     = strategy_name
        self.baseline_sharpe   = baseline_sharpe
        self.baseline_win_rate = baseline_win_rate
        self.window            = window_trades
        self.sharpe_drop_pct   = sharpe_drop_pct
        self.win_rate_drop_pp  = win_rate_drop_pp
        self._consecutive_neg_sharpe = 0

    def check(self) -> StrategyHealth:
        trades = get_trade_history(limit=self.window * 3)
        trades = [t for t in trades if t.get("strategy") == self.strategy_name]

        if len(trades) < 5:
            return StrategyHealth(
                strategy=self.strategy_name, status=HealthStatus.NO_DATA,
                rolling_sharpe=0, baseline_sharpe=self.baseline_sharpe,
                rolling_win_rate=0, baseline_win_rate=self.baseline_win_rate,
                recent_trades=len(trades), message="Insufficient trade data",
            )

        recent = trades[:self.window]
        pnls   = [t["pnl"] for t in recent if t.get("pnl") is not None]
        wins   = [p for p in pnls if p > 0]

        if not pnls:
            return StrategyHealth(
                strategy=self.strategy_name, status=HealthStatus.NO_DATA,
                rolling_sharpe=0, baseline_sharpe=self.baseline_sharpe,
                rolling_win_rate=0, baseline_win_rate=self.baseline_win_rate,
                recent_trades=0, message="No closed trades with PnL data",
            )

        # Rolling Sharpe (annualised assuming ~4 trades/day on 1h TF)
        pnl_arr  = np.array(pnls)
        ann      = np.sqrt(252 * 4)
        r_sharpe = (pnl_arr.mean() / (pnl_arr.std() + 1e-9)) * ann

        r_win_rate = len(wins) / len(pnls) * 100

        # Determine status
        sharpe_threshold  = self.baseline_sharpe * (1 - self.sharpe_drop_pct)
        win_rate_threshold = self.baseline_win_rate - self.win_rate_drop_pp

        if r_sharpe < 0:
            self._consecutive_neg_sharpe += 1
        else:
            self._consecutive_neg_sharpe = 0

        if self._consecutive_neg_sharpe >= 2:
            status = HealthStatus.CRITICAL
            msg    = (f"CRITICAL: Negative Sharpe ({r_sharpe:.2f}) "
                      f"for {self._consecutive_neg_sharpe} consecutive windows")
        elif r_sharpe < sharpe_threshold:
            status = HealthStatus.WARNING
            msg    = (f"WARNING: Rolling Sharpe {r_sharpe:.2f} dropped >50% "
                      f"below baseline {self.baseline_sharpe:.2f}")
        elif r_win_rate < win_rate_threshold:
            status = HealthStatus.DEGRADED
            msg    = (f"DEGRADED: Win rate {r_win_rate:.1f}% dropped {self.win_rate_drop_pp}pp "
                      f"below baseline {self.baseline_win_rate:.1f}%")
        else:
            status = HealthStatus.HEALTHY
            msg    = f"Healthy | Sharpe={r_sharpe:.2f} WR={r_win_rate:.1f}%"

        health = StrategyHealth(
            strategy         = self.strategy_name,
            status           = status,
            rolling_sharpe   = r_sharpe,
            baseline_sharpe  = self.baseline_sharpe,
            rolling_win_rate = r_win_rate,
            baseline_win_rate= self.baseline_win_rate,
            recent_trades    = len(recent),
            message          = msg,
        )

        self._dispatch_alerts(health)
        return health

    def _dispatch_alerts(self, health: StrategyHealth):
        if health.status in (HealthStatus.CRITICAL, HealthStatus.WARNING, HealthStatus.DEGRADED):
            icon = {"critical": "🚨", "warning": "⚠️", "degraded": "📉"}[health.status.value]
            msg  = (
                f"{icon} *Strategy Health Alert*\n"
                f"Strategy : `{health.strategy}`\n"
                f"Status   : *{health.status.value.upper()}*\n"
                f"Sharpe   : {health.rolling_sharpe:.2f} (baseline: {health.baseline_sharpe:.2f})\n"
                f"Win rate : {health.rolling_win_rate:.1f}% (baseline: {health.baseline_win_rate:.1f}%)\n"
                f"Message  : {health.message}"
            )
            notify(msg)
            logger.warning(f"[HEALTH] {health.message}")
        else:
            logger.debug(f"[HEALTH] {health.strategy}: {health.message}")


class MultiStrategyMonitor:
    """Monitor multiple strategies and report aggregate health."""

    def __init__(self, strategies: dict[str, dict]):
        """
        strategies = {
            "trend_ema":  {"baseline_sharpe": 1.5, "baseline_win_rate": 58.0},
            "ensemble":   {"baseline_sharpe": 1.8, "baseline_win_rate": 62.0},
        }
        """
        self._monitors = {
            name: StrategyMonitor(name, **params)
            for name, params in strategies.items()
        }

    def check_all(self) -> dict[str, StrategyHealth]:
        results = {}
        for name, monitor in self._monitors.items():
            results[name] = monitor.check()
        return results

    def any_critical(self) -> bool:
        return any(h.status == HealthStatus.CRITICAL
                   for h in self.check_all().values())
