"""
Benchmark comparison module.
Compares the bot's performance against:
  1. Buy & Hold BTC
  2. Buy & Hold ETH
  3. Equal-weight crypto index (BTC+ETH+BNB+SOL)
  4. S&P 500 (SPY)

Outputs a side-by-side Sharpe / CAGR / MaxDD / Calmar comparison.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from loguru import logger

from config import CONFIG


def _compute_benchmark_metrics(prices: pd.Series, initial: float = 10_000) -> dict:
    equity   = prices / prices.iloc[0] * initial
    returns  = equity.pct_change().dropna()
    ann      = np.sqrt(365 * 24)

    sharpe   = (returns.mean() / (returns.std() + 1e-9)) * ann
    roll_max = equity.cummax()
    max_dd   = ((equity - roll_max) / roll_max).min() * 100
    n_years  = len(equity) / (365 * 24)
    cagr     = ((equity.iloc[-1] / initial) ** (1 / max(n_years, 0.01)) - 1) * 100
    calmar   = cagr / abs(max_dd + 1e-9)

    return {
        "total_return_%": round((equity.iloc[-1] / initial - 1) * 100, 2),
        "cagr_%":         round(cagr,   2),
        "sharpe":         round(sharpe, 2),
        "max_dd_%":       round(max_dd, 2),
        "calmar":         round(calmar, 2),
    }


def run_benchmark(
    bot_equity: pd.Series,
    start: str = "2021-01-01",
    end: str   = "2024-12-31",
    initial:   float = 10_000,
    output_dir: Path = CONFIG.reports_dir,
) -> pd.DataFrame:
    """
    Fetch benchmark data, compute metrics, plot comparison.
    Returns comparison DataFrame.
    """
    from data.fetcher import fetch_ohlcv_yfinance, fetch_ohlcv_ccxt

    benchmarks: dict[str, pd.Series] = {}

    # Crypto benchmarks via CCXT
    for sym, name in [("BTC/USDT", "BTC Buy&Hold"), ("ETH/USDT", "ETH Buy&Hold")]:
        try:
            df = fetch_ohlcv_ccxt(sym, "1h", start, end)
            benchmarks[name] = df["close"]
        except Exception as e:
            logger.warning(f"Could not fetch {sym}: {e}")

    # Stock benchmarks via yfinance
    for ticker, name in [("SPY", "S&P 500 (SPY)"), ("QQQ", "Nasdaq (QQQ)")]:
        try:
            df = fetch_ohlcv_yfinance(ticker, "1h", start, end)
            benchmarks[name] = df["close"]
        except Exception as e:
            logger.debug(f"Could not fetch {ticker}: {e}")

    # Bot performance
    bot_metrics = _compute_benchmark_metrics(bot_equity, initial)
    bot_metrics["strategy"] = "Bot Strategy"

    rows = [bot_metrics]
    equity_series = {"Bot": bot_equity / bot_equity.iloc[0] * initial}

    for name, prices in benchmarks.items():
        # Align to bot equity timeframe
        aligned = prices.reindex(bot_equity.index).ffill().dropna()
        if len(aligned) < 10:
            continue
        m = _compute_benchmark_metrics(aligned, initial)
        m["strategy"] = name
        rows.append(m)
        equity_series[name] = aligned / aligned.iloc[0] * initial

    df = pd.DataFrame(rows)[["strategy", "total_return_%", "cagr_%", "sharpe", "max_dd_%", "calmar"]]
    df = df.sort_values("sharpe", ascending=False)

    # Plot
    fig = go.Figure()
    colors = ["#58a6ff", "#3fb950", "#ffa657", "#d2a8ff", "#f85149"]
    for i, (name, eq) in enumerate(equity_series.items()):
        width = 3 if name == "Bot" else 1.5
        fig.add_trace(go.Scatter(
            x=eq.index, y=eq.values, name=name,
            line=dict(color=colors[i % len(colors)], width=width),
        ))

    fig.update_layout(
        title="Bot vs Benchmarks — Equity Curves",
        template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        yaxis_title="Equity (USDT)", font=dict(color="#c9d1d9"),
        height=500, legend=dict(orientation="h", y=-0.15),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    chart_path = output_dir / "benchmark_comparison.html"
    fig.write_html(str(chart_path))

    csv_path = output_dir / "benchmark_comparison.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Benchmark report: {chart_path}")

    return df
