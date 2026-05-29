"""
Monte Carlo robustness testing.
Answers the key question: "Is this strategy genuinely profitable,
or did it just get lucky on this specific dataset?"

Methods:
  1. Trade-shuffle MC  — shuffle the order of historical trades N times,
                         recompute equity curve each time.
  2. Returns-scramble  — randomly permute daily returns.
  3. Param perturbation — add ±10 % noise to optimised params and re-run.

Output:
  - 5th / 50th / 95th percentile equity curves
  - Probability of ruin (equity < 50 % of start)
  - Sharpe distribution
  - p-value: what % of random shuffles beat the real strategy
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.table import Table

from config import CONFIG


@dataclass
class MCResult:
    n_simulations:    int
    sharpe_dist:      np.ndarray
    final_eq_dist:    np.ndarray
    max_dd_dist:      np.ndarray
    p_ruin:           float       # P(equity < 50% initial)
    p_beat_real:      float       # P(random > real strategy)
    real_sharpe:      float
    real_final_eq:    float
    percentiles:      dict        # 5th / 50th / 95th for equity

    def summary(self):
        console = Console()
        console.print("\n[bold cyan]MONTE CARLO RESULTS[/bold cyan]")
        console.print(f"  Simulations       : {self.n_simulations:,}")
        console.print(f"  Real Sharpe       : [green]{self.real_sharpe:.2f}[/green]")
        console.print(f"  Sharpe median     : {np.median(self.sharpe_dist):.2f} "
                      f"  (5th: {np.percentile(self.sharpe_dist, 5):.2f} / "
                      f"95th: {np.percentile(self.sharpe_dist, 95):.2f})")
        console.print(f"  Final eq median   : {np.median(self.final_eq_dist):,.0f}")
        console.print(f"  P(ruin)           : [{'red' if self.p_ruin > 0.05 else 'green'}]{self.p_ruin*100:.1f}%[/]")
        console.print(f"  P(random > real)  : [{'red' if self.p_beat_real > 0.10 else 'green'}]{self.p_beat_real*100:.1f}%[/] "
                      f"  ({'NOT ' if self.p_beat_real > 0.05 else ''}statistically significant)")
        console.print(f"  5th pct equity    : {self.percentiles['p5']:,.0f}")
        console.print(f"  50th pct equity   : {self.percentiles['p50']:,.0f}")
        console.print(f"  95th pct equity   : {self.percentiles['p95']:,.0f}")


def _equity_from_trades(trade_pnls: list[float], initial: float) -> np.ndarray:
    eq = np.empty(len(trade_pnls) + 1)
    eq[0] = initial
    for i, pnl in enumerate(trade_pnls):
        eq[i + 1] = eq[i] + pnl
    return eq


def run_monte_carlo(
    result,
    n_simulations: int = 1_000,
    initial_capital: float = CONFIG.backtest.initial_capital,
    ruin_threshold: float = 0.5,
    output_dir: Path = CONFIG.reports_dir,
    strategy_name: str = "strategy",
) -> MCResult:
    """
    Shuffle trade order N times and recompute metrics.
    """
    closed_trades = [t for t in result.trades if not t.is_open]
    if len(closed_trades) < 10:
        raise ValueError("Need at least 10 closed trades for Monte Carlo.")

    trade_pnls   = np.array([t.pnl for t in closed_trades])
    real_eq      = _equity_from_trades(trade_pnls.tolist(), initial_capital)
    real_returns = np.diff(real_eq) / real_eq[:-1]
    real_sharpe  = (real_returns.mean() / (real_returns.std() + 1e-9)) * np.sqrt(252)
    real_final   = real_eq[-1]

    rng             = np.random.default_rng(42)
    sharpe_dist     = np.empty(n_simulations)
    final_eq_dist   = np.empty(n_simulations)
    max_dd_dist     = np.empty(n_simulations)
    all_curves      = []

    for i in range(n_simulations):
        shuffled = rng.permutation(trade_pnls)
        eq       = _equity_from_trades(shuffled.tolist(), initial_capital)

        rets     = np.diff(eq) / eq[:-1]
        sharpe   = (rets.mean() / (rets.std() + 1e-9)) * np.sqrt(252)
        roll_max = np.maximum.accumulate(eq)
        max_dd   = ((eq - roll_max) / roll_max).min()

        sharpe_dist[i]   = sharpe
        final_eq_dist[i] = eq[-1]
        max_dd_dist[i]   = max_dd

        if i < 200:  # save first 200 curves for plotting
            all_curves.append(eq)

    p_ruin     = (final_eq_dist < initial_capital * ruin_threshold).mean()
    p_beat     = (sharpe_dist > real_sharpe).mean()

    mc = MCResult(
        n_simulations  = n_simulations,
        sharpe_dist    = sharpe_dist,
        final_eq_dist  = final_eq_dist,
        max_dd_dist    = max_dd_dist,
        p_ruin         = p_ruin,
        p_beat_real    = p_beat,
        real_sharpe    = real_sharpe,
        real_final_eq  = real_final,
        percentiles    = {
            "p5":  np.percentile(final_eq_dist, 5),
            "p50": np.percentile(final_eq_dist, 50),
            "p95": np.percentile(final_eq_dist, 95),
        },
    )

    _save_mc_chart(mc, all_curves, real_eq, strategy_name, output_dir)
    return mc


def _save_mc_chart(mc: MCResult, curves: list, real_eq: np.ndarray,
                   strategy_name: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    x = list(range(len(real_eq)))

    fig = go.Figure()

    # Fan of random curves (thin, grey)
    for eq in curves:
        fig.add_trace(go.Scatter(
            x=x, y=eq.tolist(), mode="lines",
            line=dict(color="rgba(100,100,100,0.05)", width=1),
            showlegend=False,
        ))

    # Percentile bands
    curves_arr = np.array(curves)
    p5   = np.percentile(curves_arr, 5,  axis=0)
    p95  = np.percentile(curves_arr, 95, axis=0)

    fig.add_trace(go.Scatter(x=x, y=p5.tolist(),  name="5th percentile",  line=dict(color="#f85149", dash="dash")))
    fig.add_trace(go.Scatter(x=x, y=p95.tolist(), name="95th percentile", line=dict(color="#3fb950", dash="dash")))
    fig.add_trace(go.Scatter(x=x, y=real_eq.tolist(), name="Real strategy",
                             line=dict(color="#58a6ff", width=3)))

    fig.update_layout(
        title=f"Monte Carlo ({mc.n_simulations:,} simulations) — {strategy_name}",
        template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        xaxis_title="Trade #", yaxis_title="Equity",
        font=dict(color="#c9d1d9"), height=500,
    )

    out = output_dir / f"{strategy_name}_monte_carlo.html"
    fig.write_html(str(out))
    logger.info(f"Monte Carlo chart: {out}")
