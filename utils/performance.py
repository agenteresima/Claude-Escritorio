"""
Extended performance analytics — beyond basic Sharpe/DD.
Used for professional reporting and strategy selection.
"""
import numpy as np
import pandas as pd
from typing import Optional


def monthly_returns(equity: pd.Series) -> pd.DataFrame:
    """Pivot table: rows=year, columns=month, values=return%."""
    monthly = equity.resample("ME").last().pct_change().dropna() * 100
    monthly.index = pd.to_datetime(monthly.index)
    df = monthly.to_frame("return")
    df["year"]  = df.index.year
    df["month"] = df.index.month
    pivot = df.pivot(index="year", columns="month", values="return")
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot.columns)]
    return pivot


def rolling_sharpe(equity: pd.Series, window: int = 365 * 24) -> pd.Series:
    returns = equity.pct_change().dropna()
    return (
        returns.rolling(window).mean()
        / returns.rolling(window).std()
        * np.sqrt(365 * 24)
    ).rename("rolling_sharpe")


def max_consecutive_losses(trades_pnl: list[float]) -> int:
    max_streak = streak = 0
    for p in trades_pnl:
        if p < 0:
            streak  += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def expectancy(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Mathematical expectancy per trade in % of risked capital.
    Positive = profitable system.
    """
    return win_rate * avg_win - (1 - win_rate) * abs(avg_loss)


def r_multiples(trades) -> pd.Series:
    """
    Express each trade as a multiple of initial risk (R).
    Distribution shape reveals strategy quality.
    """
    rmults = []
    for t in trades:
        if t.is_open:
            continue
        initial_risk = abs(t.entry_price - t.stop_loss) * t.size
        if initial_risk > 0:
            rmults.append(t.pnl / initial_risk)
    return pd.Series(rmults, name="R_multiple")


def ulcer_index(equity: pd.Series) -> float:
    """
    Ulcer Index — measures depth and duration of drawdowns.
    Lower is better (< 5 is excellent, < 15 is acceptable).
    """
    roll_max   = equity.cummax()
    drawdown   = (equity - roll_max) / roll_max * 100
    return np.sqrt((drawdown ** 2).mean())


def mar_ratio(cagr_pct: float, max_dd_pct: float) -> float:
    """Managed Accounts Reports ratio — same as Calmar but explicit."""
    return cagr_pct / abs(max_dd_pct) if max_dd_pct != 0 else 0.0


def full_analytics(result, initial_capital: float = 10_000) -> dict:
    """
    Compute the complete analytics suite from a BacktestResult.
    """
    from backtesting.engine import _compute_metrics
    base = result.metrics.copy()

    closed = [t for t in result.trades if not t.is_open]
    pnl_list = [t.pnl for t in closed]

    wins   = [p for p in pnl_list if p > 0]
    losses = [p for p in pnl_list if p <= 0]

    avg_win  = np.mean(wins)   if wins   else 0.0
    avg_loss = np.mean(losses) if losses else 0.0
    wr       = base.get("win_rate", 0) / 100

    base["expectancy"]        = expectancy(wr, avg_win, avg_loss)
    base["ulcer_index"]       = ulcer_index(result.equity_curve)
    base["max_consec_losses"] = max_consecutive_losses(pnl_list)
    base["mar_ratio"]         = mar_ratio(base.get("cagr", 0), base.get("max_drawdown_pct", 0))
    base["avg_win_pct"]       = avg_win  / initial_capital * 100
    base["avg_loss_pct"]      = avg_loss / initial_capital * 100
    base["payoff_ratio"]      = abs(avg_win / avg_loss) if avg_loss != 0 else 0.0

    rmult = r_multiples(result.trades)
    if not rmult.empty:
        base["r_expectancy"]  = rmult.mean()
        base["r_std"]         = rmult.std()

    return base
