"""
Strategy parameter optimizer using Walk-Forward Analysis.
Walk-Forward avoids overfitting by training on a rolling window
and testing on unseen data — the industry-standard approach.
"""
import itertools
from dataclasses import dataclass
from typing import Any, Callable
import pandas as pd
import numpy as np
from loguru import logger
from rich.table import Table
from rich.console import Console

from backtesting.engine import BacktestEngine, BacktestResult
from config import CONFIG


@dataclass
class OptimizationResult:
    params: dict
    in_sample: dict    # metrics on training period
    out_of_sample: dict  # metrics on test period (what matters)
    combined_score: float


def _score(metrics: dict) -> float:
    """
    Composite score:  Sharpe * win_rate * (1 - |max_drawdown|/100)
    Balances return quality, consistency, and downside risk.
    """
    sharpe = metrics.get("sharpe", 0)
    wr     = metrics.get("win_rate", 0) / 100
    dd     = abs(metrics.get("max_drawdown_pct", 100)) / 100
    pf     = min(metrics.get("profit_factor", 0), 5)  # cap outliers
    return sharpe * wr * (1 - dd) * (pf / 5)


def grid_search(
    strategy_cls,
    df: pd.DataFrame,
    param_grid: dict[str, list],
    backtest_cfg=CONFIG.backtest,
    max_combos: int = 500,
) -> list[OptimizationResult]:
    """
    Exhaustive grid search with walk-forward validation.
    Train on first 70 %, test on last 30 %.
    """
    from risk.manager import RiskManager

    split = int(len(df) * 0.70)
    train_df = df.iloc[:split]
    test_df  = df.iloc[split:]

    keys   = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))
    if len(combos) > max_combos:
        logger.warning(f"Grid has {len(combos)} combos — sampling {max_combos}")
        np.random.seed(42)
        idx    = np.random.choice(len(combos), max_combos, replace=False)
        combos = [combos[i] for i in idx]

    results: list[OptimizationResult] = []

    for combo in combos:
        params = dict(zip(keys, combo))
        try:
            rm       = RiskManager(initial_capital=backtest_cfg.initial_capital)
            strategy = strategy_cls(rm, **params)
            engine   = BacktestEngine(backtest_cfg, rm)

            in_df   = strategy.run(train_df)
            out_df  = strategy.run(test_df)
            in_res  = engine.run(in_df)
            out_res = engine.run(out_df)

            score = _score(out_res.metrics)
            results.append(OptimizationResult(
                params=params,
                in_sample=in_res.metrics,
                out_of_sample=out_res.metrics,
                combined_score=score,
            ))
        except Exception as e:
            logger.debug(f"Combo {params} failed: {e}")

    results.sort(key=lambda r: r.combined_score, reverse=True)
    rows = []
    for r in results:
        rows.append({"params": r.params, **r.out_of_sample,
                     "combined_score": r.combined_score})
    return pd.DataFrame(rows)


def walk_forward_test(
    strategy_cls,
    df: pd.DataFrame,
    param_grid: dict[str, list],
    n_windows: int = 5,
    train_ratio: float = 0.70,
    backtest_cfg=CONFIG.backtest,
) -> pd.DataFrame:
    """
    Rolling walk-forward: divides data into N windows,
    optimises params in each training period, tests on next OOS period.
    Returns a DataFrame of OOS metrics per window.
    """
    window_size = len(df) // n_windows
    oos_results = []

    for i in range(n_windows - 1):
        train_end = (i + 1) * window_size
        test_end  = train_end + window_size

        train = df.iloc[:train_end]
        test  = df.iloc[train_end:test_end]

        top = grid_search(strategy_cls, train, param_grid, backtest_cfg, max_combos=200)
        if top.empty:
            continue

        best_params = top.iloc[0]["params"]
        from risk.manager import RiskManager
        rm       = RiskManager(initial_capital=backtest_cfg.initial_capital)
        strategy = strategy_cls(rm, **best_params)
        engine   = BacktestEngine(backtest_cfg, rm)

        oos_df  = strategy.run(test)
        oos_res = engine.run(oos_df)
        oos_results.append({"window": i + 1, "params": best_params, **oos_res.metrics})
        logger.info(f"WF window {i+1}: Sharpe={oos_res.metrics.get('sharpe',0):.2f}, "
                    f"params={best_params}")

    return pd.DataFrame(oos_results)


def print_top_results(results: pd.DataFrame, top_n: int = 10):
    console = Console()
    table   = Table(title="Top Optimisation Results (Out-of-Sample)")

    table.add_column("Rank",      style="bold cyan")
    table.add_column("Params",    style="white")
    table.add_column("Score",     style="green")
    table.add_column("Sharpe",    style="green")
    table.add_column("Win%",      style="yellow")
    table.add_column("MaxDD%",    style="red")
    table.add_column("PF",        style="blue")

    for rank, (_, row) in enumerate(results.head(top_n).iterrows(), 1):
        table.add_row(
            str(rank),
            str(row.get("params", {})),
            f"{row.get('combined_score', 0):.4f}",
            f"{row.get('sharpe', 0):.2f}",
            f"{row.get('win_rate', 0):.1f}%",
            f"{row.get('max_drawdown_pct', 0):.1f}%",
            f"{row.get('profit_factor', 0):.2f}",
        )

    console.print(table)
