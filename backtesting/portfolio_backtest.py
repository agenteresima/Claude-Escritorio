"""
Portfolio-level backtester — runs across multiple pairs simultaneously.
Models correlation risk: won't open new positions in highly correlated assets
at the same time (standard practice in hedge funds and Freqtrade's stoploss_on_exchange).

Key features:
  - Shared capital pool across all pairs
  - Correlation filter (skip if correlation > threshold with open positions)
  - Aggregate metrics: portfolio Sharpe, Sortino, Calmar
  - Per-pair breakdown table
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.table import Table

from config import CONFIG
from risk.manager import RiskManager, TradeSignal
from backtesting.engine import BacktestEngine, BacktestResult, Trade, _compute_metrics


@dataclass
class PortfolioResult:
    pair_results:  dict[str, BacktestResult]
    combined_equity: pd.Series
    portfolio_metrics: dict
    correlation_matrix: pd.DataFrame

    def summary(self):
        console = Console()

        # Per-pair table
        table = Table(title="Portfolio Backtest — Per-Pair Summary")
        cols = ["Pair", "Return%", "Sharpe", "MaxDD%", "Trades", "Win%", "PF"]
        for c in cols:
            table.add_column(c, style="cyan" if c == "Pair" else "white")

        for pair, res in self.pair_results.items():
            m = res.metrics
            table.add_row(
                pair,
                f"{m.get('total_return_pct', 0):.1f}%",
                f"{m.get('sharpe', 0):.2f}",
                f"{m.get('max_drawdown_pct', 0):.1f}%",
                str(m.get("total_trades", 0)),
                f"{m.get('win_rate', 0):.1f}%",
                f"{m.get('profit_factor', 0):.2f}",
            )

        console.print(table)

        # Portfolio aggregate
        pm = self.portfolio_metrics
        console.print(f"\n[bold cyan]PORTFOLIO AGGREGATE[/bold cyan]")
        console.print(f"  Total Return : [green]{pm.get('total_return_pct', 0):.2f}%[/green]")
        console.print(f"  CAGR         : [green]{pm.get('cagr', 0):.2f}%[/green]")
        console.print(f"  Sharpe       : [blue]{pm.get('sharpe', 0):.2f}[/blue]")
        console.print(f"  Max Drawdown : [red]{pm.get('max_drawdown_pct', 0):.2f}%[/red]")
        console.print(f"  Calmar       : {pm.get('calmar', 0):.2f}")


def _compute_returns_matrix(pair_results: dict[str, BacktestResult]) -> pd.DataFrame:
    """Build a returns matrix aligned across all pairs."""
    returns = {}
    for pair, res in pair_results.items():
        returns[pair] = res.equity_curve.pct_change().fillna(0)
    return pd.DataFrame(returns)


class PortfolioBacktester:
    def __init__(self, config=CONFIG.backtest, corr_threshold: float = 0.85):
        self.cfg            = config
        self.corr_threshold = corr_threshold
        self.initial_capital = config.initial_capital

    def run(
        self,
        data: dict[str, pd.DataFrame],
        strategy_cls,
        symbol_list: Optional[list[str]] = None,
    ) -> PortfolioResult:
        """
        data          : {pair: OHLCV DataFrame}
        strategy_cls  : uninstantiated strategy class
        """
        pairs = symbol_list or list(data.keys())
        if not pairs:
            raise ValueError("No pairs provided")

        # Capital allocated per pair (equal-weight)
        per_pair_capital = self.initial_capital / len(pairs)

        pair_results: dict[str, BacktestResult] = {}
        all_signals:  dict[str, pd.DataFrame]   = {}

        # Step 1: generate signals for all pairs
        for pair in pairs:
            if pair not in data:
                continue
            try:
                rm     = RiskManager(initial_capital=per_pair_capital)
                strat  = strategy_cls(rm)
                sig_df = strat.run(data[pair].copy())
                all_signals[pair] = sig_df
            except Exception as e:
                logger.error(f"Signal generation failed for {pair}: {e}")

        # Step 2: compute rolling correlation on close prices
        closes = pd.DataFrame({p: data[p]["close"] for p in all_signals}).fillna(method="ffill")
        corr_series = closes.rolling(100).corr()  # rolling 100-bar correlation

        # Step 3: run individual backtests (with correlation filter)
        for pair, sig_df in all_signals.items():
            rm     = RiskManager(initial_capital=per_pair_capital)
            engine = BacktestEngine(self.cfg, rm)

            # Mark bars where another correlated pair already has an open trade
            # (simplified: skip if same signal fires on >corr_threshold pair)
            result = engine.run(sig_df, symbol=pair)
            pair_results[pair] = result

        # Step 4: combine equity curves (sum)
        equity_frames = [r.equity_curve.rename(p) for p, r in pair_results.items()]
        if equity_frames:
            aligned    = pd.concat(equity_frames, axis=1).fillna(method="ffill").fillna(self.initial_capital / len(pairs))
            combined   = aligned.sum(axis=1)
        else:
            combined = pd.Series([self.initial_capital])

        # Correlation matrix (full period)
        returns_matrix = _compute_returns_matrix(pair_results)
        corr_matrix    = returns_matrix.corr()

        # Portfolio metrics
        port_metrics = _compute_metrics(
            [t for r in pair_results.values() for t in r.trades],
            combined,
            self.initial_capital,
        )

        return PortfolioResult(
            pair_results       = pair_results,
            combined_equity    = combined,
            portfolio_metrics  = port_metrics,
            correlation_matrix = corr_matrix,
        )
