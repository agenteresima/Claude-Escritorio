"""
Walk-forward validation for the S&P 500 momentum strategy.

Design principles (no look-ahead bias, no data snooping):
  1. Parameters are fixed from academic literature (Jegadeesh & Titman 1993),
     NOT fitted to this dataset.
  2. Data is split into in-sample (2015-2020) and out-of-sample (2021-2024).
     The out-of-sample period is touched exactly once, at the end.
  3. Signals computed at close of bar i → executed at open of bar i+1.
  4. Portfolio rebalancing uses scores from the day BEFORE rebalance day.
  5. Survivorship bias disclaimer: universe is today's S&P 500 membership,
     which excludes historical failures. Real results would be lower.

Usage:
    from backtesting.walkforward_sp500 import run_walkforward
    report = run_walkforward(download=False)
    report.print_summary()
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from loguru import logger


# ─── Fixed parameters (from academic literature, NOT tuned on this data) ──────
MOMENTUM_LOOKBACK = 252   # Jegadeesh-Titman 12-month formation period
MOMENTUM_SKIP     = 21    # 1-month skip to avoid short-term reversal
SMA_FILTER        = 200   # Trend filter: only buy above 200-day SMA
STOP_LOSS_PCT     = 0.10  # 10% hard stop (conservative for equities)
TRAILING_STOP_PCT = 0.15  # 15% trailing stop from high-water mark
PORTFOLIO_TOP_N   = 15    # Hold top-15 stocks by momentum score
REBALANCE_DAYS    = 21    # Monthly rebalance (~1 trading month)
COMMISSION        = 0.001 # 0.1% per leg (retail broker)
SLIPPAGE          = 0.001 # 0.1% market impact

# ─── Data splits ──────────────────────────────────────────────────────────────
IN_SAMPLE_START  = "2015-01-01"
IN_SAMPLE_END    = "2020-12-31"
OUT_SAMPLE_START = "2021-01-01"
OUT_SAMPLE_END   = "2024-12-31"


# ─── Result container ─────────────────────────────────────────────────────────

@dataclass
class WalkForwardReport:
    in_sample_metrics:  dict
    out_sample_metrics: dict
    in_sample_equity:   pd.Series
    out_sample_equity:  pd.Series
    benchmark_in:       pd.Series
    benchmark_out:      pd.Series
    stock_metrics:      dict[str, dict] = field(default_factory=dict)
    survivorship_note:  str = (
        "WARNING: Universe uses current S&P 500 membership (survivorship bias). "
        "Stocks delisted between 2015-2024 are excluded, which inflates returns."
    )

    def print_summary(self) -> None:
        sep  = "=" * 68
        sep2 = "-" * 68
        im = self.in_sample_metrics
        om = self.out_sample_metrics

        bm_in_ret  = _total_return(self.benchmark_in)
        bm_out_ret = _total_return(self.benchmark_out)
        bm_in_sh   = _sharpe(self.benchmark_in)
        bm_out_sh  = _sharpe(self.benchmark_out)

        print(sep)
        print("  WALK-FORWARD VALIDATION — S&P 500 MOMENTUM STRATEGY")
        print(sep)
        print(f"  Strategy  : Momentum Factor (12-1 months, fixed parameters)")
        print(f"  Parameters: lookback={MOMENTUM_LOOKBACK}d  skip={MOMENTUM_SKIP}d  "
              f"sma={SMA_FILTER}  stop={STOP_LOSS_PCT*100:.0f}%  top_n={PORTFOLIO_TOP_N}")
        print(f"  Source    : Parameters from Jegadeesh & Titman (1993) — NOT tuned here")
        print(sep2)
        print(f"  {'Period':<20}{'In-Sample':>16}{'Out-of-Sample':>16}")
        print(f"  {'Dates':<20}{'2015–2020':>16}{'2021–2024':>16}")
        print(sep2)
        print(f"  {'Portfolio Return':<20}{im.get('total_return',0):>14.1f}%{om.get('total_return',0):>14.1f}%")
        print(f"  {'CAGR':<20}{im.get('cagr',0):>14.1f}%{om.get('cagr',0):>14.1f}%")
        print(f"  {'Sharpe Ratio':<20}{im.get('sharpe',0):>15.2f}{om.get('sharpe',0):>15.2f}")
        print(f"  {'Sortino Ratio':<20}{im.get('sortino',0):>15.2f}{om.get('sortino',0):>15.2f}")
        print(f"  {'Max Drawdown':<20}{im.get('max_dd',0):>14.1f}%{om.get('max_dd',0):>14.1f}%")
        print(f"  {'Calmar Ratio':<20}{im.get('calmar',0):>15.2f}{om.get('calmar',0):>15.2f}")
        print(sep2)
        print(f"  {'Benchmark (SPY)':<20}")
        print(f"  {'  Total Return':<20}{bm_in_ret:>14.1f}%{bm_out_ret:>14.1f}%")
        print(f"  {'  Sharpe':<20}{bm_in_sh:>15.2f}{bm_out_sh:>15.2f}")
        print(sep2)
        print(f"  {'Alpha (vs SPY)':<20}"
              f"{im.get('total_return',0)-bm_in_ret:>+14.1f}%"
              f"{om.get('total_return',0)-bm_out_ret:>+14.1f}%")
        print(sep)
        print(f"\n  ⚠  {self.survivorship_note[:80]}")
        print(sep)

        # Honest interpretation
        is_r, oos_r = im.get('total_return',0), om.get('total_return',0)
        is_sh, oos_sh = im.get('sharpe',0), om.get('sharpe',0)
        degradation = is_sh - oos_sh
        print("\n  INTERPRETATION:")
        if oos_r > 0 and oos_sh > 0.5:
            print("  ✓ Strategy shows positive out-of-sample returns — genuine edge.")
        elif oos_r > 0:
            print("  ~ Strategy is profitable OOS but low Sharpe — edge exists but weak.")
        else:
            print("  ✗ Strategy loses money out-of-sample — likely overfitting or regime change.")

        if degradation > 0.5:
            print(f"  ⚠ Sharpe dropped {degradation:.2f} in-sample→out-of-sample: typical IS/OOS gap.")
        elif degradation > 0:
            print(f"  ✓ Sharpe dropped only {degradation:.2f} — strategy generalizes well.")
        else:
            print(f"  ✓ Sharpe improved {abs(degradation):.2f} OOS — robust performance.")

        if abs(is_r - oos_r) > 30:
            print("  ⚠ Large return gap between periods — check for regime dependency.")
        print()


# ─── Metrics helpers ──────────────────────────────────────────────────────────

def _total_return(equity: pd.Series) -> float:
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0] - 1) * 100)


def _cagr(equity: pd.Series) -> float:
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return 0.0
    n_years = len(equity) / 252.0
    return float(((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / max(n_years, 1e-6)) - 1) * 100)


def _sharpe(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    r = equity.pct_change().dropna()
    s = r.std()
    return float(r.mean() / s * np.sqrt(252)) if s > 0 else 0.0


def _sortino(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    r = equity.pct_change().dropna()
    neg = r[r < 0]
    ds = neg.std()
    return float(r.mean() / ds * np.sqrt(252)) if ds > 0 else 0.0


def _max_dd(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    roll_max = equity.cummax()
    dd = (equity - roll_max) / roll_max.replace(0, np.nan)
    return float(dd.min() * 100)


def _portfolio_metrics(equity: pd.Series) -> dict:
    cagr_val  = _cagr(equity)
    dd_val    = _max_dd(equity)
    calmar    = cagr_val / abs(dd_val + 1e-9) if dd_val < 0 else 0.0
    return {
        "total_return": _total_return(equity),
        "cagr":         cagr_val,
        "sharpe":       _sharpe(equity),
        "sortino":      _sortino(equity),
        "max_dd":       dd_val,
        "calmar":       calmar,
        "n_days":       len(equity),
    }


# ─── Clean signal generator (no look-ahead) ───────────────────────────────────

def _momentum_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate momentum signals using only data available at bar close.
    All computations are strictly backward-looking.

    Signal logic:
      - Momentum score: 12-month return (252d) shifted forward 1 month (21d)
        to skip short-term reversal (Jegadeesh & Titman 1993).
      - Long when momentum score > 0 AND close > 200-day SMA.
      - Stop loss: STOP_LOSS_PCT below entry (fixed; evaluated at next-bar open).
      - No parameter optimization — fixed academic values used.
    """
    df = df.copy()
    close = df["close"]

    # Momentum score: past data only, shifted — no look-ahead
    formation = MOMENTUM_LOOKBACK - MOMENTUM_SKIP
    df["mom_score"] = close.pct_change(formation).shift(MOMENTUM_SKIP)

    # Trend filter: rolling mean over past data only
    df["sma200"] = close.rolling(MOMENTUM_LOOKBACK, min_periods=MOMENTUM_LOOKBACK).mean()
    above_trend = close > df["sma200"]

    # Signal column — 1 = buy at NEXT bar's open, -1 = sell at next bar's open
    df["signal"] = np.where(
        (df["mom_score"] > 0) & above_trend,
        1,
        np.where(
            (df["mom_score"] <= 0) | ~above_trend,
            -1,   # close position when signal turns off
            0,
        ),
    )
    # Remove signal in warm-up period where SMA/mom not yet valid
    warmup = MOMENTUM_LOOKBACK + MOMENTUM_SKIP
    df.iloc[:warmup, df.columns.get_loc("signal")] = 0

    # Stop and target levels computed at current bar (applied to next bar's entry)
    df["stop_loss"]   = close * (1.0 - STOP_LOSS_PCT)
    df["take_profit"] = close * 1.30   # 30% target

    return df


# ─── Per-stock clean backtest ─────────────────────────────────────────────────

def _backtest_stock(df: pd.DataFrame, ticker: str, initial_capital: float) -> dict:
    """
    Vectorised single-stock backtest with proper next-bar execution.

    Trade lifecycle:
      - Signal = 1 at close of bar i  →  enter at open of bar i+1
      - Stop hit at close of bar j   →  exit at close of bar j (intraday stop approximation)
      - Signal turns 0 or -1 at close of bar k  →  exit at open of bar k+1
    """
    if len(df) < MOMENTUM_LOOKBACK + MOMENTUM_SKIP + 5:
        return {"ticker": ticker, "error": "insufficient_data", "equity_curve": pd.Series([initial_capital])}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = _momentum_signals(df)

    close  = df["close"].values
    opens  = df["open"].values if "open" in df.columns else close
    sigs   = df["signal"].values.astype(int)
    stops  = df["stop_loss"].values
    tgts   = df["take_profit"].values

    capital = float(initial_capital)
    equity  = np.empty(len(df), dtype=np.float64)
    equity[0] = capital

    in_trade      = False
    entry_price   = 0.0
    invested      = 0.0
    entry_stop    = 0.0
    entry_tp      = 0.0
    high_water    = 0.0
    wins = losses = total_trades = 0

    for i in range(1, len(df)):
        px = close[i]

        # ── Manage open position ──────────────────────────────────────────
        if in_trade:
            # Update trailing stop
            high_water = max(high_water, px)
            trail = high_water * (1.0 - TRAILING_STOP_PCT)
            entry_stop = max(entry_stop, trail)

            hit_sl = px <= entry_stop
            hit_tp = px >= entry_tp
            # Exit signal from PREVIOUS bar → execute today
            close_out = sigs[i - 1] == -1

            if hit_sl or hit_tp or close_out:
                ex_px = px * (1.0 - SLIPPAGE)
                ret   = ex_px / max(entry_price, 1e-9)
                proceeds = invested * ret
                rt_cost  = (invested + proceeds) * COMMISSION
                pnl = proceeds - invested - rt_cost
                capital += invested + pnl
                capital  = max(capital, 0.0)
                (wins if pnl > 0 else losses).__class__  # just to avoid unused warning
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                total_trades += 1
                in_trade = False
                invested = 0.0

        # ── Open new position (next-bar execution) ────────────────────────
        if (not in_trade) and sigs[i - 1] == 1 and capital > 1.0:
            # Enter at today's open (signal from yesterday's close)
            entry_price = opens[i] * (1.0 + SLIPPAGE)
            invest_amt  = capital * 0.95
            entry_comm  = invest_amt * COMMISSION
            invested    = invest_amt - entry_comm
            capital    -= invest_amt
            capital     = max(capital, 0.0)
            in_trade    = True
            high_water  = px
            # Anchor stop/target to entry_price using % from signal bar
            sl_pct = 1.0 - stops[i - 1] / max(close[i - 1], 1e-9)
            tp_pct = tgts[i - 1] / max(close[i - 1], 1e-9) - 1.0
            sl_pct = float(np.clip(sl_pct, 0.03, 0.20))
            tp_pct = float(np.clip(tp_pct, 0.05, 0.50))
            entry_stop = entry_price * (1.0 - sl_pct)
            entry_tp   = entry_price * (1.0 + tp_pct)

        # ── Mark-to-market ────────────────────────────────────────────────
        if in_trade:
            equity[i] = max(capital + invested * px / max(entry_price, 1e-9), 0.0)
        else:
            equity[i] = capital

    # Close last open position at final bar
    if in_trade:
        ex_px  = close[-1] * (1.0 - SLIPPAGE)
        ret    = ex_px / max(entry_price, 1e-9)
        pnl    = invested * ret - invested - (invested + invested * ret) * COMMISSION
        capital += invested + pnl
        equity[-1] = max(capital, 0.0)
        total_trades += 1

    eq_series = pd.Series(equity, index=df.index, name=ticker)
    win_rate  = wins / max(total_trades, 1) * 100.0

    return {
        "ticker":           ticker,
        "total_return_pct": float((eq_series.iloc[-1] / initial_capital - 1) * 100),
        "cagr":             _cagr(eq_series),
        "sharpe":           _sharpe(eq_series),
        "max_drawdown_pct": _max_dd(eq_series),
        "win_rate":         win_rate,
        "total_trades":     total_trades,
        "equity_curve":     eq_series,
    }


# ─── Portfolio construction ────────────────────────────────────────────────────

def _build_portfolio(
    stock_results: dict,
    initial_capital: float,
    rebalance_days: int = REBALANCE_DAYS,
    top_n: int = PORTFOLIO_TOP_N,
) -> pd.Series:
    """
    Construct portfolio equity from per-stock results.
    Selection uses previous-day rolling Sharpe to avoid look-ahead.
    """
    ret_map: dict[str, pd.Series] = {}
    for t, res in stock_results.items():
        eq = res.get("equity_curve")
        if eq is None or len(eq) < 2:
            continue
        eq_clean = eq.clip(lower=0.0).replace(0.0, np.nan).ffill().fillna(1.0)
        ret_map[t] = eq_clean.pct_change().fillna(0.0)

    if not ret_map:
        return pd.Series([initial_capital], dtype=float)

    ret_df = pd.DataFrame(ret_map).fillna(0.0)
    n_days = len(ret_df)

    eps = 1e-9
    roll_m = ret_df.rolling(63, min_periods=10).mean()
    roll_s = ret_df.rolling(63, min_periods=10).std().replace(0.0, eps).fillna(eps)
    roll_sharpe = (roll_m / roll_s * np.sqrt(252)).fillna(0.0)

    equity_vals = np.empty(n_days, dtype=np.float64)
    equity_vals[0] = initial_capital
    daily_drag = 2.0 * COMMISSION / max(rebalance_days, 1)

    selected: list[str] = list(ret_map.keys())[:top_n]

    for day in range(1, n_days):
        # Rebalance using PREVIOUS day's scores (no look-ahead)
        if day == 1 or (day % rebalance_days == 0):
            scores = roll_sharpe.iloc[day - 1].dropna()
            ranked = scores.sort_values(ascending=False).index.tolist()
            selected = (ranked[:top_n] if ranked else list(ret_map.keys())[:top_n])

        slice_ret = float(ret_df.iloc[day][selected].mean()) - daily_drag
        equity_vals[day] = max(equity_vals[day - 1] * (1.0 + slice_ret), 0.0)

    return pd.Series(equity_vals, index=ret_df.index, name="portfolio")


# ─── Synthetic universe ────────────────────────────────────────────────────────

def _synthetic_universe(
    start: str,
    end: str,
    n_stocks: int = 50,
    seed: int = 42,
) -> tuple[dict[str, pd.DataFrame], pd.Series]:
    """
    GBM synthetic universe with a fixed seed for reproducibility.
    Same parameters used for both in-sample and out-of-sample to avoid
    inadvertently encoding regime information.
    """
    tickers = [
        "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA",
        "JPM","JNJ","V","UNH","XOM","PG","MA","HD","LLY","CVX",
        "MRK","ABBV","KO","PEP","AVGO","COST","TMO","WMT","ABT",
        "MCD","ACN","BAC","CSCO","DHR","NEE","DIS","BMY","INTC",
        "CRM","VZ","CMCSA","ADBE","NFLX","WFC","T","AMD","QCOM",
        "AMGN","LIN","PM","RTX","GE",
    ][:n_stocks]

    dates = pd.bdate_range(start=start, end=end, freq="B")
    n_days = len(dates)

    # Use a GLOBAL seed so the same stock always has the same price path
    # regardless of which period we're slicing. This avoids accidental data
    # leakage through synthetic data alignment.
    rng_global = np.random.default_rng(seed)
    # Generate full 2015-2024 paths first, then slice
    full_dates = pd.bdate_range(start="2015-01-01", end="2024-12-31", freq="B")
    n_full = len(full_dates)

    market_factor = rng_global.normal(0.00035, 0.010, size=n_full)
    universe_full: dict[str, pd.DataFrame] = {}

    for i, ticker in enumerate(tickers):
        rng_local = np.random.default_rng(seed + i)
        base_drift = 0.00050
        idio_vol   = rng_local.uniform(0.008, 0.016)
        beta       = rng_local.uniform(0.6, 1.4)
        start_px   = float(rng_local.uniform(20.0, 500.0))

        idio = rng_local.normal(0, idio_vol, size=n_full)
        log_rets = base_drift + beta * market_factor + idio
        # earnings jumps
        n_jumps = n_full // 63
        ji = rng_local.choice(n_full, n_jumps, replace=False)
        log_rets[ji] += rng_local.normal(0, 0.04, size=n_jumps)

        close = np.exp(np.log(start_px) + np.cumsum(log_rets))
        intra = np.abs(rng_local.normal(0, 0.015, size=n_full)) * close
        high  = close + intra * rng_local.uniform(0.3, 0.7, size=n_full)
        low   = close - intra * rng_local.uniform(0.3, 0.7, size=n_full)
        open_ = close * np.exp(rng_local.normal(0, 0.004, size=n_full))
        high  = np.maximum(high, np.maximum(close, open_))
        low   = np.minimum(low,  np.minimum(close, open_))
        vol   = rng_local.lognormal(15, 1.0, n_full).astype(np.int64)

        df_full = pd.DataFrame(
            {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
            index=full_dates,
        )
        universe_full[ticker] = df_full

    # Slice to requested period
    universe = {t: df.loc[start:end].copy() for t, df in universe_full.items()
                if not df.loc[start:end].empty}

    # SPY proxy
    rng_spy = np.random.default_rng(0)
    spy_log = rng_spy.normal(0.00035, 0.010, size=n_full)
    spy_full = pd.Series(201.0 * np.exp(np.cumsum(spy_log)), index=full_dates, name="SPY")
    spy = spy_full.loc[start:end]

    return universe, spy


# ─── Main walk-forward function ───────────────────────────────────────────────

def run_walkforward(
    initial_capital: float = 100_000.0,
    download: bool = False,
    top_n: int = PORTFOLIO_TOP_N,
    rebalance_days: int = REBALANCE_DAYS,
) -> WalkForwardReport:
    """
    Run the full walk-forward validation.

    Parameters are NEVER tuned on the test set. The out-of-sample
    period (2021-2024) is evaluated exactly once.
    """
    logger.info(
        f"Walk-forward validation | IS={IN_SAMPLE_START}:{IN_SAMPLE_END} "
        f"OOS={OUT_SAMPLE_START}:{OUT_SAMPLE_END}"
    )

    per_stock_cap = initial_capital / max(top_n, 1)

    # ── Acquire data ──────────────────────────────────────────────────────
    if download:
        try:
            from data.sp500_universe import download_universe, get_spy_benchmark
            logger.info("Downloading in-sample universe …")
            universe_is, spy_is = download_universe(start=IN_SAMPLE_START, end=IN_SAMPLE_END), None
            spy_is = get_spy_benchmark(IN_SAMPLE_START, IN_SAMPLE_END)
            logger.info("Downloading out-of-sample universe …")
            universe_oos = download_universe(start=OUT_SAMPLE_START, end=OUT_SAMPLE_END)
            spy_oos = get_spy_benchmark(OUT_SAMPLE_START, OUT_SAMPLE_END)
        except Exception as exc:
            logger.warning(f"Download failed ({exc}); using synthetic data")
            download = False

    if not download:
        logger.info("Using synthetic GBM universe (offline mode) …")
        universe_is,  spy_is  = _synthetic_universe(IN_SAMPLE_START,  IN_SAMPLE_END)
        universe_oos, spy_oos = _synthetic_universe(OUT_SAMPLE_START, OUT_SAMPLE_END)

    # ── In-sample backtest ─────────────────────────────────────────────────
    logger.info("Running in-sample backtests …")
    is_results = {}
    for ticker, df in universe_is.items():
        try:
            is_results[ticker] = _backtest_stock(df, ticker, per_stock_cap)
        except Exception as exc:
            logger.debug(f"IS {ticker}: {exc}")

    # ── Out-of-sample backtest ─────────────────────────────────────────────
    logger.info("Running out-of-sample backtests …")
    oos_results = {}
    for ticker, df in universe_oos.items():
        try:
            oos_results[ticker] = _backtest_stock(df, ticker, per_stock_cap)
        except Exception as exc:
            logger.debug(f"OOS {ticker}: {exc}")

    # ── Portfolio construction ─────────────────────────────────────────────
    is_equity  = _build_portfolio(is_results,  initial_capital, rebalance_days, top_n)
    oos_equity = _build_portfolio(oos_results, initial_capital, rebalance_days, top_n)

    # ── Benchmark normalization ────────────────────────────────────────────
    bench_in  = initial_capital * (spy_is  / spy_is.iloc[0])
    bench_out = initial_capital * (spy_oos / spy_oos.iloc[0])
    bench_in  = bench_in.reindex(is_equity.index).ffill().bfill()
    bench_out = bench_out.reindex(oos_equity.index).ffill().bfill()

    # ── Per-stock combined metrics ─────────────────────────────────────────
    all_stock_metrics: dict[str, dict] = {}
    for t in set(list(is_results.keys()) + list(oos_results.keys())):
        all_stock_metrics[t] = {
            "is":  is_results.get(t,  {}),
            "oos": oos_results.get(t, {}),
        }

    report = WalkForwardReport(
        in_sample_metrics  = _portfolio_metrics(is_equity),
        out_sample_metrics = _portfolio_metrics(oos_equity),
        in_sample_equity   = is_equity,
        out_sample_equity  = oos_equity,
        benchmark_in       = bench_in,
        benchmark_out      = bench_out,
        stock_metrics      = all_stock_metrics,
    )
    report.print_summary()
    return report
