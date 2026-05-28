"""
Strategy comparator — runs all strategies on the same dataset
and produces a side-by-side ranking with a Plotly report.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from loguru import logger

from config import CONFIG
from risk.manager import RiskManager
from backtesting.engine import BacktestEngine, BacktestResult
from strategies import STRATEGIES


def compare_strategies(
    df: pd.DataFrame,
    symbol: str = "ASSET",
    initial_capital: float = CONFIG.backtest.initial_capital,
    output_dir: Path = CONFIG.reports_dir,
) -> pd.DataFrame:
    """
    Run every registered strategy on df and return a ranked comparison table.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, BacktestResult] = {}

    for name, StratCls in STRATEGIES.items():
        try:
            rm       = RiskManager(initial_capital=initial_capital)
            strategy = StratCls(rm)
            engine   = BacktestEngine(CONFIG.backtest, rm)
            sig_df   = strategy.run(df.copy())
            result   = engine.run(sig_df, symbol=symbol)
            results[name] = result
            logger.info(f"{name}: Sharpe={result.metrics.get('sharpe',0):.2f}, "
                        f"Return={result.metrics.get('total_return_pct',0):.1f}%")
        except Exception as e:
            logger.error(f"Strategy '{name}' failed: {e}")

    # Build comparison DataFrame
    rows = []
    for name, res in results.items():
        m = res.metrics
        rows.append({
            "strategy":        name,
            "total_return_%":  round(m.get("total_return_pct", 0), 2),
            "cagr_%":          round(m.get("cagr", 0), 2),
            "sharpe":          round(m.get("sharpe", 0), 2),
            "sortino":         round(m.get("sortino", 0), 2),
            "max_dd_%":        round(m.get("max_drawdown_pct", 0), 2),
            "calmar":          round(m.get("calmar", 0), 2),
            "win_rate_%":      round(m.get("win_rate", 0), 2),
            "profit_factor":   round(m.get("profit_factor", 0), 2),
            "total_trades":    m.get("total_trades", 0),
        })

    cmp_df = pd.DataFrame(rows).sort_values("sharpe", ascending=False)

    # HTML report
    _save_html_report(cmp_df, results, symbol, output_dir)
    csv_path = output_dir / f"{symbol.replace('/', '_')}_strategy_comparison.csv"
    cmp_df.to_csv(csv_path, index=False)
    logger.info(f"Comparison saved to {csv_path}")

    return cmp_df


def _save_html_report(
    cmp_df: pd.DataFrame,
    results: dict[str, BacktestResult],
    symbol: str,
    output_dir: Path,
):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Equity Curves",
            "Sharpe vs Max Drawdown",
            "Win Rate vs Profit Factor",
            "Total Return % by Strategy",
        ],
    )

    colors = ["#00b4d8", "#90e0ef", "#f77f00", "#d62828", "#3a86ff", "#8338ec"]

    # Equity curves
    for i, (name, res) in enumerate(results.items()):
        eq = res.equity_curve
        fig.add_trace(
            go.Scatter(x=eq.index, y=eq.values, name=name, line=dict(color=colors[i % len(colors)])),
            row=1, col=1,
        )

    # Sharpe vs DD scatter
    fig.add_trace(
        go.Scatter(
            x=cmp_df["max_dd_%"], y=cmp_df["sharpe"],
            mode="markers+text",
            text=cmp_df["strategy"],
            textposition="top center",
            marker=dict(size=12, color=colors[:len(cmp_df)]),
            name="Sharpe/DD",
        ),
        row=1, col=2,
    )

    # Win rate vs PF scatter
    fig.add_trace(
        go.Scatter(
            x=cmp_df["win_rate_%"], y=cmp_df["profit_factor"],
            mode="markers+text",
            text=cmp_df["strategy"],
            textposition="top center",
            marker=dict(size=12, color=colors[:len(cmp_df)]),
            name="WR/PF",
        ),
        row=2, col=1,
    )

    # Bar chart total return
    fig.add_trace(
        go.Bar(
            x=cmp_df["strategy"], y=cmp_df["total_return_%"],
            marker_color=colors[:len(cmp_df)],
            name="Total Return %",
        ),
        row=2, col=2,
    )

    fig.update_layout(
        height=900,
        title_text=f"Strategy Comparison — {symbol}",
        template="plotly_dark",
        showlegend=True,
    )

    out = output_dir / f"{symbol.replace('/', '_')}_comparison.html"
    fig.write_html(str(out))
    logger.info(f"HTML report: {out}")
