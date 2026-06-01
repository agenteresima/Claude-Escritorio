"""
10-year S&P 500 portfolio backtest — Version 2 enhancement.
Runs daily-bar backtests across the full S&P 500 universe with portfolio construction.

Features:
  - 10-year backtest (2015-2024) across 50 S&P 500 stocks
  - Fully offline-capable via GBM synthetic data (no network required)
  - Dynamic portfolio construction: rank by trailing Sharpe, hold top-N
  - Equal-weight rebalancing every `rebalance_days` (default 21 trading days)
  - SPY buy-and-hold benchmark for alpha measurement
  - Sector-level aggregated performance metrics
  - Commission modelling (round-trip)
  - rich-formatted summary table

Usage:
    from backtesting.sp500_backtest import run_sp500_backtest
    result = run_sp500_backtest(download=False)   # offline, synthetic data
    result = run_sp500_backtest(download=True)    # real data via yfinance
"""

import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from loguru import logger

# Rich is available (used in portfolio_backtest.py)
try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:  # pragma: no cover
    _RICH = False

from utils.indicators import add_all_indicators

# ---------------------------------------------------------------------------
# Sector drift adjustments (annualised excess over base GBM drift)
# Keeps synthetic universe sector-realistic
# ---------------------------------------------------------------------------
_SECTOR_DRIFT: dict[str, float] = {
    "Technology":              0.0004,   # +~10 % annualised extra drift
    "Consumer Discretionary":  0.0002,
    "Communication Services":  0.0001,
    "Financials":              0.0000,
    "Healthcare":              0.0001,
    "Energy":                 -0.0001,
    "Consumer Staples":        0.0000,
    "Materials":               0.0000,
    "Industrials":             0.0001,
    "Utilities":              -0.0001,
}

# Sector map imported lazily (avoids hard import of data module at package load)
def _get_sector_map() -> dict[str, str]:
    try:
        from data.sp500_universe import SECTOR_MAP
        return SECTOR_MAP
    except Exception:
        return {}


def _get_sp500_tickers() -> list[str]:
    try:
        from data.sp500_universe import SP500_TICKERS
        return SP500_TICKERS
    except Exception:
        return [
            "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
            "JPM", "JNJ", "V", "UNH", "XOM", "PG", "MA", "HD", "LLY", "CVX",
            "MRK", "ABBV", "KO", "PEP", "AVGO", "COST", "TMO", "WMT", "ABT",
            "MCD", "ACN", "BAC", "CSCO", "DHR", "NEE", "DIS", "BMY", "INTC",
            "CRM", "VZ", "CMCSA", "ADBE", "NFLX", "WFC", "T", "AMD", "QCOM",
            "AMGN", "LIN", "PM", "RTX", "GE",
        ]


# ---------------------------------------------------------------------------
# Metric helpers (daily-bar aware — annualise with sqrt(252))
# ---------------------------------------------------------------------------

def _sharpe_from_equity(equity: pd.Series) -> float:
    """Annualised Sharpe from a daily equity curve (252 trading days)."""
    if len(equity) < 2:
        return 0.0
    rets = equity.pct_change().dropna()
    std = rets.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float((rets.mean() / std) * np.sqrt(252))


def _cagr_from_equity(equity: pd.Series) -> float:
    """CAGR (%) from a daily equity series."""
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return 0.0
    n_years = len(equity) / 252.0
    return float(((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / max(n_years, 1e-6)) - 1) * 100)


def _max_drawdown_from_equity(equity: pd.Series) -> float:
    """Maximum drawdown (%) — returned as a negative number."""
    if len(equity) < 2:
        return 0.0
    roll_max = equity.cummax()
    dd = (equity - roll_max) / roll_max.replace(0, np.nan)
    return float(dd.min() * 100)


def _compute_stock_metrics(
    ticker: str,
    equity: pd.Series,
    signals: pd.Series,
    initial_capital: float,
) -> dict:
    """Summarise a per-stock vectorised backtest into a metrics dict."""
    total_return = float((equity.iloc[-1] / initial_capital - 1) * 100)
    cagr = _cagr_from_equity(equity)
    sharpe = _sharpe_from_equity(equity)
    max_dd = _max_drawdown_from_equity(equity)

    # Trade-level stats from signal series
    signal_changes = signals.diff().fillna(0)
    entries = (signal_changes == 1).sum()
    exits = (signal_changes == -1).sum()
    total_trades = int(min(entries, exits))

    # Approximate win-rate from positive return sub-sequences
    rets = equity.pct_change().fillna(0)
    in_trade = signals == 1
    trade_rets = rets[in_trade]
    if len(trade_rets) > 0:
        win_rate = float((trade_rets > 0).mean() * 100)
    else:
        win_rate = 0.0

    return {
        "ticker": ticker,
        "total_return_pct": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown_pct": max_dd,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "equity_curve": equity,
    }


# ---------------------------------------------------------------------------
# Dataclass for results
# ---------------------------------------------------------------------------

@dataclass
class SP500BacktestResult:
    """
    Container for a completed S&P 500 portfolio backtest.

    Fields
    ------
    portfolio_equity    : daily portfolio equity curve (pd.Series, DatetimeIndex)
    stock_results       : per-stock metrics dict keyed by ticker
    sector_performance  : sector-level aggregated metrics (pd.DataFrame)
    benchmark_equity    : SPY buy-and-hold equity curve
    portfolio_metrics   : overall portfolio-level scalar metrics dict
    best_stocks         : top-10 tickers by Sharpe ratio
    worst_stocks        : bottom-10 tickers by Sharpe ratio
    """

    portfolio_equity:   pd.Series
    stock_results:      dict[str, dict]
    sector_performance: pd.DataFrame
    benchmark_equity:   pd.Series
    portfolio_metrics:  dict
    best_stocks:        list[str] = field(default_factory=list)
    worst_stocks:       list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    def summary(self) -> str:
        """Return (and print) a formatted summary table."""
        lines: list[str] = []

        sep  = "=" * 65
        sep2 = "-" * 65

        pm = self.portfolio_metrics
        bm_ret = float(
            (self.benchmark_equity.iloc[-1] / self.benchmark_equity.iloc[0] - 1) * 100
        ) if len(self.benchmark_equity) > 1 else 0.0
        bm_sharpe = _sharpe_from_equity(self.benchmark_equity)
        bm_dd = _max_drawdown_from_equity(self.benchmark_equity)

        lines += [
            sep,
            "  S&P 500 10-YEAR PORTFOLIO BACKTEST RESULTS",
            sep,
            f"  {'Metric':<28}{'Portfolio':>12}{'Benchmark':>12}",
            sep2,
            f"  {'Total Return':<28}{pm.get('total_return_pct', 0):>11.2f}%{bm_ret:>11.2f}%",
            f"  {'CAGR':<28}{pm.get('cagr', 0):>11.2f}%{_cagr_from_equity(self.benchmark_equity):>11.2f}%",
            f"  {'Sharpe Ratio':<28}{pm.get('sharpe', 0):>12.2f}{bm_sharpe:>12.2f}",
            f"  {'Max Drawdown':<28}{pm.get('max_drawdown_pct', 0):>11.2f}%{bm_dd:>11.2f}%",
            f"  {'Calmar Ratio':<28}{pm.get('calmar', 0):>12.2f}{'':>12}",
            f"  {'Avg Stock Win Rate':<28}{pm.get('avg_win_rate', 0):>11.2f}%{'':>12}",
            f"  {'Stocks in Universe':<28}{pm.get('n_stocks', 0):>12}{'':>12}",
            sep2,
        ]

        # Best stocks
        lines.append("  TOP-10 STOCKS (by Sharpe)")
        lines.append(f"  {'Ticker':<10}{'Sharpe':>8}{'CAGR':>9}{'MaxDD':>10}{'Trades':>8}")
        lines.append("  " + "-" * 45)
        for t in self.best_stocks[:10]:
            m = self.stock_results.get(t, {})
            lines.append(
                f"  {t:<10}{m.get('sharpe', 0):>8.2f}"
                f"{m.get('cagr', 0):>8.1f}%"
                f"{m.get('max_drawdown_pct', 0):>9.1f}%"
                f"{m.get('total_trades', 0):>8}"
            )

        lines.append(sep2)

        # Worst stocks
        lines.append("  BOTTOM-10 STOCKS (by Sharpe)")
        lines.append(f"  {'Ticker':<10}{'Sharpe':>8}{'CAGR':>9}{'MaxDD':>10}{'Trades':>8}")
        lines.append("  " + "-" * 45)
        for t in self.worst_stocks[:10]:
            m = self.stock_results.get(t, {})
            lines.append(
                f"  {t:<10}{m.get('sharpe', 0):>8.2f}"
                f"{m.get('cagr', 0):>8.1f}%"
                f"{m.get('max_drawdown_pct', 0):>9.1f}%"
                f"{m.get('total_trades', 0):>8}"
            )

        lines.append(sep2)

        # Sector performance
        if not self.sector_performance.empty:
            lines.append("  SECTOR PERFORMANCE")
            lines.append(f"  {'Sector':<28}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Stocks':>7}")
            lines.append("  " + "-" * 60)
            for _, row in self.sector_performance.iterrows():
                lines.append(
                    f"  {row['sector']:<28}"
                    f"{row.get('cagr', 0):>7.1f}%"
                    f"{row.get('sharpe', 0):>8.2f}"
                    f"{row.get('max_drawdown_pct', 0):>8.1f}%"
                    f"{int(row.get('n_stocks', 0)):>7}"
                )

        lines.append(sep)
        text = "\n".join(lines)
        print(text)
        return text


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

class SP500BacktestEngine:
    """
    10-year S&P 500 portfolio backtester.

    Parameters
    ----------
    initial_capital : float
        Starting portfolio value (default 100 000 USD).
    top_n : int
        Number of stocks to hold simultaneously (equal-weight).
    rebalance_days : int
        Number of trading days between portfolio rebalances.
    commission : float
        One-way commission rate (0.001 = 0.1 % per leg).
    start : str
        ISO date string for backtest start.
    end : str
        ISO date string for backtest end.
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        top_n: int = 20,
        rebalance_days: int = 21,
        commission: float = 0.001,
        start: str = "2015-01-01",
        end: str = "2024-12-31",
    ) -> None:
        self.initial_capital = float(initial_capital)
        self.top_n = int(top_n)
        self.rebalance_days = int(rebalance_days)
        self.commission = float(commission)
        self.start = start
        self.end = end
        self._sector_map: dict[str, str] = _get_sector_map()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(
        self,
        strategy_name: str = "momentum_factor",
        tickers: Optional[list[str]] = None,
        download: bool = True,
    ) -> SP500BacktestResult:
        """
        Execute the full 10-year portfolio backtest.

        Parameters
        ----------
        strategy_name : str
            Key from ``strategies.STRATEGIES`` dict (e.g. ``"momentum_factor"``).
        tickers : list[str] | None
            Explicit ticker list.  ``None`` uses the default SP500_TICKERS.
        download : bool
            If True, attempt to download real OHLCV data via yfinance.
            If False (or download fails), fall back to synthetic GBM data.

        Returns
        -------
        SP500BacktestResult
        """
        tickers = tickers or _get_sp500_tickers()
        logger.info(
            f"SP500BacktestEngine.run | strategy={strategy_name} "
            f"tickers={len(tickers)} download={download} "
            f"period={self.start}:{self.end}"
        )

        # ---- 1. Data acquisition ----------------------------------------
        universe: dict[str, pd.DataFrame] = {}
        spy_prices: Optional[pd.Series] = None

        if download:
            universe, spy_prices = self._try_download(tickers)

        if not universe:
            logger.info("Falling back to synthetic GBM universe (offline mode)")
            universe = self._generate_synthetic_universe(n_stocks=len(tickers), tickers=tickers)
            spy_prices = None  # will synthesise below

        if spy_prices is None or spy_prices.empty:
            spy_prices = self._generate_synthetic_spy(list(universe.values())[0].index)

        logger.info(f"Universe size after data load: {len(universe)} tickers")

        # ---- 2. Per-stock backtests -------------------------------------
        stock_results: dict[str, dict] = {}
        for ticker, df in universe.items():
            try:
                res = self._run_stock_strategy(df.copy(), ticker, strategy_name)
                stock_results[ticker] = res
            except Exception as exc:
                logger.warning(f"Stock backtest failed for {ticker}: {exc}")

        if not stock_results:
            raise RuntimeError("All per-stock backtests failed — cannot build portfolio.")

        logger.info(f"Completed per-stock backtests: {len(stock_results)} stocks")

        # ---- 3. Portfolio equity curve ----------------------------------
        portfolio_equity = self._compute_portfolio_equity(stock_results, self.rebalance_days)

        # ---- 4. Benchmark equity curve ----------------------------------
        # Align SPY to the common trading calendar
        common_idx = portfolio_equity.index
        spy_aligned = spy_prices.reindex(common_idx).ffill().bfill()
        benchmark_equity = self.initial_capital * (spy_aligned / spy_aligned.iloc[0])
        benchmark_equity.name = "SPY_benchmark"

        # ---- 5. Portfolio-level metrics ---------------------------------
        portfolio_metrics = self._compute_portfolio_metrics(
            portfolio_equity, stock_results
        )

        # ---- 6. Sector-level aggregation --------------------------------
        sector_performance = self._compute_sector_performance(stock_results)

        # ---- 7. Best / worst stocks by Sharpe ---------------------------
        sharpe_rank = sorted(
            stock_results.keys(),
            key=lambda t: stock_results[t].get("sharpe", 0.0),
            reverse=True,
        )
        best_stocks  = sharpe_rank[:10]
        worst_stocks = sharpe_rank[-10:][::-1]  # ascending order of worst

        return SP500BacktestResult(
            portfolio_equity=portfolio_equity,
            stock_results=stock_results,
            sector_performance=sector_performance,
            benchmark_equity=benchmark_equity,
            portfolio_metrics=portfolio_metrics,
            best_stocks=best_stocks,
            worst_stocks=worst_stocks,
        )

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _try_download(
        self, tickers: list[str]
    ) -> tuple[dict[str, pd.DataFrame], Optional[pd.Series]]:
        """Attempt yfinance download; return empty dict on any failure."""
        try:
            from data.sp500_universe import download_universe, get_spy_benchmark
            universe = download_universe(tickers, self.start, self.end)
            spy = get_spy_benchmark(self.start, self.end)
            return universe, spy
        except Exception as exc:
            logger.warning(f"Universe download failed ({exc}); using synthetic data")
            return {}, None

    # ------------------------------------------------------------------
    # Synthetic data generation (GBM)
    # ------------------------------------------------------------------

    def _generate_synthetic_universe(
        self,
        n_stocks: int = 50,
        tickers: Optional[list[str]] = None,
    ) -> dict[str, pd.DataFrame]:
        """
        Generate realistic synthetic daily OHLCV for *n_stocks* over the
        configured date range.

        Model: Geometric Brownian Motion
          drift = 0.0003 / day  (~7.5 % annualised)
          vol   = 0.015  / day  (~24 % annualised)

        Sector-specific drift adjustments are applied so that Technology
        names outperform while Energy names lag — matching the 2015-2024
        decade.

        Returns
        -------
        dict[str, pd.DataFrame]  — keys are ticker strings, values are
        DataFrames with columns [open, high, low, close, volume] and a
        DatetimeIndex of trading days.
        """
        rng = np.random.default_rng(42)

        # Build trading-day calendar
        dates = pd.bdate_range(start=self.start, end=self.end, freq="B")
        n_days = len(dates)

        tickers = tickers or _get_sp500_tickers()
        ticker_list = list(tickers)[:n_stocks]

        # Pad if requested more than provided
        while len(ticker_list) < n_stocks:
            ticker_list.append(f"SYN{len(ticker_list):03d}")

        universe: dict[str, pd.DataFrame] = {}

        # Shared market factor — positive drift so index rises ~9% annually (2015-2024 S&P mean)
        market_mean = 0.00035   # +9% annual market drift
        market_factor = rng.normal(market_mean, 0.010, size=n_days)

        for i, ticker in enumerate(ticker_list):
            sector = self._sector_map.get(ticker, "Technology")
            sector_drift_adj = _SECTOR_DRIFT.get(sector, 0.0)

            # Base drift ~13% annual — matches 2015-2024 S&P 500 average (including dividends)
            base_drift = 0.00050 + sector_drift_adj
            # Idiosyncratic volatility per stock
            idio_vol = rng.uniform(0.008, 0.016)
            # Stock-specific starting price between $20 and $500
            rng_local = np.random.default_rng(42 + i)
            start_price = float(rng_local.uniform(20.0, 500.0))

            # Log-returns = market_factor * beta + idio_shock + drift
            beta = rng.uniform(0.6, 1.4)
            idio_shocks = rng.normal(0, idio_vol, size=n_days)
            daily_log_returns = base_drift + beta * market_factor + idio_shocks

            # Occasional earnings jumps (4 per year)
            n_jumps = int(n_days / 63)
            jump_idx = rng.choice(n_days, size=n_jumps, replace=False)
            daily_log_returns[jump_idx] += rng.normal(0, 0.04, size=n_jumps)

            # Price path via cumulative sum of log-returns
            log_prices = np.log(start_price) + np.cumsum(daily_log_returns)
            close_prices = np.exp(log_prices)

            # OHLC: intra-day range ~1-3 % of close
            intraday_range = np.abs(rng.normal(0, 0.015, size=n_days)) * close_prices
            high_prices  = close_prices + intraday_range * rng.uniform(0.3, 0.7, size=n_days)
            low_prices   = close_prices - intraday_range * rng.uniform(0.3, 0.7, size=n_days)
            open_prices  = close_prices * np.exp(rng.normal(0, 0.005, size=n_days))
            # Ensure OHLC consistency
            high_prices  = np.maximum(high_prices, np.maximum(close_prices, open_prices))
            low_prices   = np.minimum(low_prices,  np.minimum(close_prices, open_prices))

            # Volume: log-normal, higher on large-move days
            base_volume = rng_local.lognormal(15, 1.0, size=n_days).astype(np.int64)
            vol_boost = 1.0 + 3.0 * np.abs(daily_log_returns) / 0.02
            volume = (base_volume * vol_boost).astype(np.int64)

            df = pd.DataFrame(
                {
                    "open":   open_prices,
                    "high":   high_prices,
                    "low":    low_prices,
                    "close":  close_prices,
                    "volume": volume,
                },
                index=dates,
            )
            universe[ticker] = df

        logger.info(f"Synthetic universe generated: {len(universe)} stocks x {n_days} days")
        return universe

    def _generate_synthetic_spy(self, index: pd.DatetimeIndex) -> pd.Series:
        """
        Synthetic SPY price series over the given trading-day index.
        Uses the same GBM parameterisation but with lower volatility
        (index diversification effect: vol ~ 15 %).
        """
        rng = np.random.default_rng(0)  # separate seed from universe
        n = len(index)
        drift = 0.00035  # ~9 % annual (S&P historical mean 2015-2024)
        vol = 0.010      # ~16 % annual
        log_rets = rng.normal(drift, vol, size=n)
        prices = 201.0 * np.exp(np.cumsum(log_rets))  # SPY closed at $201 on 2015-01-02
        return pd.Series(prices, index=index, name="SPY")

    # ------------------------------------------------------------------
    # Per-stock vectorised backtest
    # ------------------------------------------------------------------

    def _run_stock_strategy(
        self,
        df: pd.DataFrame,
        ticker: str,
        strategy_name: str,
    ) -> dict:
        """
        Run a single-stock vectorised daily backtest.

        1. Applies ``add_all_indicators`` to the OHLCV DataFrame.
        2. Loads the named strategy from ``strategies.STRATEGIES`` and calls
           ``generate_signals(df)`` to get signal / stop_loss / take_profit columns.
        3. Simulates trades bar-by-bar (long-only, one position at a time).
        4. Returns a metrics dict including the per-stock equity curve.

        Falls back gracefully: if strategy import or signal generation fails,
        a simple SMA-crossover signal is used instead.
        """
        if len(df) < 60:
            raise ValueError(f"{ticker}: insufficient data ({len(df)} rows)")

        # --- Indicators ---
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                df = add_all_indicators(df)
            except Exception as exc:
                logger.debug(f"{ticker}: add_all_indicators partial failure ({exc}); continuing")

        # --- Signals ---
        try:
            from strategies import STRATEGIES
            strategy_cls = STRATEGIES.get(strategy_name)
            if strategy_cls is None:
                raise KeyError(f"Strategy '{strategy_name}' not found in STRATEGIES registry")
            # Minimal RiskManager — we don't use its validation in the vectorised path
            from risk.manager import RiskManager
            rm = RiskManager(initial_capital=self.initial_capital / max(self.top_n, 1))
            strat = strategy_cls(rm)
            df = strat.generate_signals(df)
        except Exception as exc:
            logger.debug(f"{ticker}: strategy signal generation failed ({exc}); using SMA fallback")
            df = self._sma_crossover_signals(df)

        # Ensure signal column exists and is clean
        if "signal" not in df.columns:
            df["signal"] = 0
        df["signal"] = df["signal"].fillna(0).astype(int).clip(-1, 1)

        # --- Vectorised simulation (long-only, fractional shares) ---
        # We simulate using *fractional share value* rather than integer shares
        # to avoid integer-rounding capital leakage that leads to negative equity.
        close = df["close"].values
        signals = df["signal"].values
        stop_loss_col = (
            df["stop_loss"].values if "stop_loss" in df.columns else close * 0.93
        )
        take_profit_col = (
            df["take_profit"].values if "take_profit" in df.columns else close * 1.25
        )

        # Each stock is assessed with the full initial capital so that individual
        # metrics (Sharpe, CAGR, drawdown) are meaningful on their own.
        # The portfolio equity is computed separately in _compute_portfolio_equity.
        per_stock_capital = self.initial_capital / max(self.top_n, 1)
        capital = per_stock_capital
        equity_vals = np.empty(len(df), dtype=np.float64)
        equity_vals[0] = capital

        in_trade = False
        entry_price = 0.0
        invested_value = 0.0   # dollar amount invested (fractional)
        entry_stop = 0.0
        entry_tp = 0.0
        high_water = 0.0       # high of close since entry for trailing stop
        wins = 0
        losses = 0
        total_trades = 0

        # Use open prices for next-bar execution if available, else fall back to close.
        # This eliminates same-bar entry look-ahead bias: signal at close[i-1] →
        # execute at open[i] (or close[i] if no open column).
        open_prices = df["open"].values if "open" in df.columns else close

        for i in range(1, len(df)):
            price = close[i]   # mark-to-market and stop/TP checks always use close

            if in_trade:
                # Update trailing stop from high-water close
                high_water = max(high_water, price)
                trailing = high_water * 0.92
                entry_stop = max(entry_stop, trailing)

                # Exit conditions — stop/TP checked against today's close;
                # strategy exit signal from the *previous* bar (next-bar execution).
                hit_sl = price <= entry_stop
                hit_tp = price >= entry_tp
                exit_signal = signals[i - 1] == -1  # FIX: previous bar's exit signal

                if hit_sl or hit_tp or exit_signal:
                    exit_price = price * (1.0 - 0.0005)  # half-tick slippage
                    ret = exit_price / max(entry_price, 1e-9)
                    proceeds = invested_value * ret
                    cost = (invested_value + proceeds) * self.commission  # round-trip
                    pnl = proceeds - invested_value - cost
                    capital += invested_value + pnl
                    capital = max(capital, 0.0)
                    if pnl > 0:
                        wins += 1
                    else:
                        losses += 1
                    total_trades += 1
                    in_trade = False
                    invested_value = 0.0
                    entry_price = 0.0

            # FIX: next-bar execution — use signal from previous bar (i-1) and
            # enter at today's open (bar i), not at the signal bar's close.
            if (not in_trade) and signals[i - 1] == 1 and capital > 1.0:
                entry_price = open_prices[i] * (1.0 + 0.0005)  # open + slippage
                invested_value = capital * 0.95
                commission_cost = invested_value * self.commission
                invested_value -= commission_cost
                capital -= invested_value + commission_cost
                capital = max(capital, 0.0)
                in_trade = True
                high_water = price
                # Stop/TP derived from signal bar (i-1) levels, adjusted to entry_price
                raw_sl = float(stop_loss_col[i - 1])
                raw_tp = float(take_profit_col[i - 1])
                # Re-anchor stop to entry_price so level is consistent
                sl_pct = 1.0 - (raw_sl / max(close[i - 1], 1e-9)) if raw_sl > 0 else 0.07
                tp_pct = (raw_tp / max(close[i - 1], 1e-9)) - 1.0 if raw_tp > 0 else 0.25
                sl_pct = max(min(sl_pct, 0.20), 0.02)  # clamp: 2%–20% stop distance
                tp_pct = max(min(tp_pct, 0.50), 0.05)  # clamp: 5%–50% target
                entry_stop = entry_price * (1.0 - sl_pct)
                entry_tp   = entry_price * (1.0 + tp_pct)

            # Mark-to-market equity
            if in_trade:
                mtm = invested_value * (price / max(entry_price, 1e-9))
                equity_vals[i] = max(capital + mtm, 0.0)
            else:
                equity_vals[i] = capital

        # Close any remaining position at last bar
        if in_trade:
            last_price = close[-1]
            exit_price = last_price * (1.0 - 0.0005)
            ret = exit_price / max(entry_price, 1e-9)
            proceeds = invested_value * ret
            cost = (invested_value + proceeds) * self.commission
            pnl = proceeds - invested_value - cost
            capital += invested_value + pnl
            capital = max(capital, 0.0)
            equity_vals[-1] = capital
            total_trades += 1

        equity = pd.Series(equity_vals, index=df.index, name=ticker)
        equity = equity.clip(lower=0.0)  # ensure no sub-zero values

        win_rate = (wins / max(total_trades, 1)) * 100.0

        return {
            "ticker": ticker,
            "total_return_pct": float((equity.iloc[-1] / per_stock_capital - 1) * 100),
            "cagr": _cagr_from_equity(equity),
            "sharpe": _sharpe_from_equity(equity),
            "max_drawdown_pct": _max_drawdown_from_equity(equity),
            "win_rate": win_rate,
            "total_trades": total_trades,
            "equity_curve": equity,
        }

    @staticmethod
    def _sma_crossover_signals(df: pd.DataFrame) -> pd.DataFrame:
        """SMA(50/200) crossover fallback — generates periodic entry/exit signals."""
        df = df.copy()
        sma_fast = df["close"].rolling(50, min_periods=50).mean()
        sma_slow = df["close"].rolling(200, min_periods=200).mean()

        above = sma_fast > sma_slow

        df["signal"] = 0
        # Entry on cross-up; exit on cross-down
        df.loc[above & ~above.shift(1).fillna(False),  "signal"] = 1
        df.loc[~above & above.shift(1).fillna(False),  "signal"] = -1
        df["stop_loss"]   = df["close"] * 0.93
        df["take_profit"] = df["close"] * 1.25
        return df

    # ------------------------------------------------------------------
    # Portfolio construction
    # ------------------------------------------------------------------

    def _compute_portfolio_equity(
        self,
        stock_results: dict[str, dict],
        rebalance_days: int,
    ) -> pd.Series:
        """
        Build a daily portfolio equity curve from individual stock equity curves.

        Algorithm (returns-based, avoids capital-allocation rounding bugs)
        ---------
        1. Compute daily returns from each stock's equity curve.
        2. Align all return series to a common DatetimeIndex (0 for missing bars).
        3. Pre-compute rolling 63-day Sharpe for every stock.
        4. Every ``rebalance_days`` trading days, re-rank and select top-N stocks.
        5. Portfolio daily return = equal-weighted mean of selected stocks' returns
           minus amortised round-trip commission.
        6. Compound daily returns on ``initial_capital`` to produce equity curve.

        Returns
        -------
        pd.Series with DatetimeIndex, representing portfolio value each day.
        """
        if not stock_results:
            return pd.Series([self.initial_capital], dtype=float)

        # ---- 1. Build aligned daily-returns DataFrame -------------------
        return_series: dict[str, pd.Series] = {}
        for t, res in stock_results.items():
            eq = res.get("equity_curve")
            if eq is None or eq.empty or len(eq) < 2:
                continue
            # Clip equity at zero then replace zeros to avoid div-by-zero in pct_change
            eq_clean = eq.clip(lower=0.0).replace(0.0, np.nan).ffill().fillna(1.0)
            daily_ret = eq_clean.pct_change().fillna(0.0)
            return_series[t] = daily_ret

        if not return_series:
            return pd.Series([self.initial_capital], dtype=float)

        ret_df = pd.DataFrame(return_series).fillna(0.0)
        tickers = list(return_series.keys())
        common_idx = ret_df.index
        n_days = len(common_idx)

        # ---- 2. Rolling 63-day Sharpe matrix (vectorised) ---------------
        eps = 1e-9
        rolling_mean = ret_df.rolling(63, min_periods=5).mean()
        rolling_std  = ret_df.rolling(63, min_periods=5).std().replace(0.0, eps).fillna(eps)
        rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)
        rolling_sharpe = rolling_sharpe.fillna(0.0)

        # ---- 3. Simulate portfolio day by day ---------------------------
        portfolio_vals = np.empty(n_days, dtype=np.float64)
        portfolio_vals[0] = self.initial_capital

        # Round-trip commission amortised daily over holding period
        # (2 legs × commission rate / holding_days)
        daily_comm_drag = 2.0 * self.commission / max(rebalance_days, 1)

        current_selected: list[str] = tickers[: self.top_n]  # initial slice

        for day_i in range(1, n_days):
            # Rebalance on schedule — use PREVIOUS day's score to avoid look-ahead.
            # The portfolio selected at day_i uses information available at close of day_i-1.
            if day_i == 1 or (day_i % rebalance_days == 0):
                scores_row = rolling_sharpe.iloc[day_i - 1]  # FIX: prior day's Sharpe
                valid_scores = scores_row.dropna()
                ranked = valid_scores.sort_values(ascending=False).index.tolist()
                if ranked:
                    current_selected = ranked[: self.top_n]
                else:
                    current_selected = tickers[: self.top_n]

            n_held = max(len(current_selected), 1)
            slice_rets = ret_df.iloc[day_i][current_selected]
            port_daily_ret = float(slice_rets.mean()) - daily_comm_drag

            prev_val = portfolio_vals[day_i - 1]
            portfolio_vals[day_i] = max(prev_val * (1.0 + port_daily_ret), 0.0)

        port_series = pd.Series(portfolio_vals, index=common_idx, name="portfolio")
        logger.info(
            f"Portfolio equity computed: {n_days} days | "
            f"start={portfolio_vals[0]:,.0f} end={portfolio_vals[-1]:,.0f} | "
            f"top_n={self.top_n} rebalance={rebalance_days}d"
        )
        return port_series

    # ------------------------------------------------------------------
    # Sector aggregation
    # ------------------------------------------------------------------

    def _compute_sector_performance(
        self, stock_results: dict[str, dict]
    ) -> pd.DataFrame:
        """Aggregate per-stock metrics by GICS sector."""
        rows: list[dict] = []
        sector_buckets: dict[str, list[dict]] = {}

        for ticker, metrics in stock_results.items():
            sector = self._sector_map.get(ticker, "Unknown")
            sector_buckets.setdefault(sector, []).append(metrics)

        for sector, stocks in sorted(sector_buckets.items()):
            cagrs   = [s.get("cagr", 0) for s in stocks]
            sharpes = [s.get("sharpe", 0) for s in stocks]
            dds     = [s.get("max_drawdown_pct", 0) for s in stocks]
            wrs     = [s.get("win_rate", 0) for s in stocks]
            rows.append({
                "sector":           sector,
                "n_stocks":         len(stocks),
                "cagr":             float(np.mean(cagrs)),
                "sharpe":           float(np.mean(sharpes)),
                "max_drawdown_pct": float(np.mean(dds)),
                "avg_win_rate":     float(np.mean(wrs)),
            })

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows).sort_values("sharpe", ascending=False).reset_index(drop=True)
        return df

    # ------------------------------------------------------------------
    # Portfolio-level scalar metrics
    # ------------------------------------------------------------------

    def _compute_portfolio_metrics(
        self,
        portfolio_equity: pd.Series,
        stock_results: dict[str, dict],
    ) -> dict:
        """Compute summary scalars for the blended portfolio equity curve."""
        total_return = float((portfolio_equity.iloc[-1] / self.initial_capital - 1) * 100)
        cagr         = _cagr_from_equity(portfolio_equity)
        sharpe       = _sharpe_from_equity(portfolio_equity)
        max_dd       = _max_drawdown_from_equity(portfolio_equity)
        calmar       = cagr / max(abs(max_dd), 1e-9)

        # Portfolio Sortino
        rets     = portfolio_equity.pct_change().dropna()
        neg_rets = rets[rets < 0]
        sortino  = float((rets.mean() / (neg_rets.std() + 1e-9)) * np.sqrt(252))

        avg_win_rate = float(
            np.mean([v.get("win_rate", 0) for v in stock_results.values()])
        ) if stock_results else 0.0

        total_trades = int(sum(v.get("total_trades", 0) for v in stock_results.values()))

        return {
            "total_return_pct": total_return,
            "cagr":             cagr,
            "sharpe":           sharpe,
            "sortino":          sortino,
            "max_drawdown_pct": max_dd,
            "calmar":           calmar,
            "avg_win_rate":     avg_win_rate,
            "total_trades":     total_trades,
            "n_stocks":         len(stock_results),
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def run_sp500_backtest(
    strategy: str = "momentum_factor",
    start: str = "2015-01-01",
    end: str = "2024-12-31",
    initial_capital: float = 100_000.0,
    top_n: int = 20,
    rebalance_days: int = 21,
    commission: float = 0.001,
    download: bool = True,
    tickers: Optional[list[str]] = None,
) -> SP500BacktestResult:
    """
    Run the 10-year S&P 500 portfolio backtest and print a summary.

    Parameters
    ----------
    strategy : str
        Strategy name as registered in ``strategies.STRATEGIES``.
        Default ``"momentum_factor"`` uses 12-1 cross-sectional momentum.
    start : str
        Backtest start date (ISO-8601).
    end : str
        Backtest end date (ISO-8601).
    initial_capital : float
        Portfolio starting value in USD.
    top_n : int
        Number of stocks held in the portfolio at any rebalance.
    rebalance_days : int
        Number of trading days between portfolio rebalances (default 21 ~ 1 month).
    commission : float
        One-way commission per trade (0.001 = 0.1 %).
    download : bool
        If True, attempt real data download.  Set False for offline/CI runs.
    tickers : list[str] | None
        Override ticker universe.  None = use default SP500_TICKERS (50 names).

    Returns
    -------
    SP500BacktestResult
        Full result object including equity curves, per-stock metrics,
        sector performance, and benchmark comparison.

    Examples
    --------
    >>> result = run_sp500_backtest(download=False)
    >>> result = run_sp500_backtest(strategy="trend_ema", top_n=15, download=True)
    """
    engine = SP500BacktestEngine(
        initial_capital=initial_capital,
        top_n=top_n,
        rebalance_days=rebalance_days,
        commission=commission,
        start=start,
        end=end,
    )
    result = engine.run(strategy_name=strategy, tickers=tickers, download=download)
    result.summary()
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    _dl = "--no-download" not in sys.argv
    _strat = "momentum_factor"
    for arg in sys.argv[1:]:
        if arg.startswith("--strategy="):
            _strat = arg.split("=", 1)[1]

    logger.info(f"Running SP500 backtest | strategy={_strat} | download={_dl}")
    _result = run_sp500_backtest(strategy=_strat, download=_dl)
    logger.success(
        f"Done | portfolio_return={_result.portfolio_metrics.get('total_return_pct', 0):.1f}% "
        f"sharpe={_result.portfolio_metrics.get('sharpe', 0):.2f}"
    )
