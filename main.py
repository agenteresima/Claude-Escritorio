"""
Main entry point — CLI interface for the professional trading bot.

Usage examples:
  python main.py backtest  --strategy trend_ema --pair BTC/USDT
  python main.py compare   --pair BTC/USDT
  python main.py portfolio --pairs BTC/USDT ETH/USDT SOL/USDT
  python main.py optimize  --strategy trend_ema --pair BTC/USDT
  python main.py train     --pair BTC/USDT
  python main.py sentiment
  python main.py live      --dry-run
  python main.py dashboard
"""
import sys
from pathlib import Path
import click
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
logger.add("logs/bot.log", rotation="10 MB", retention="30 days", level="DEBUG")
Path("logs").mkdir(exist_ok=True)


@click.group()
def cli():
    """Professional Trading Bot — multi-strategy, walk-forward optimised."""
    pass


@cli.command()
@click.option("--strategy", "-s", default="trend_ema",
              type=click.Choice(["trend_ema", "mean_reversion", "breakout", "hybrid_ml"]))
@click.option("--pair", "-p",     default="BTC/USDT")
@click.option("--start",          default="2021-01-01")
@click.option("--end",            default="2024-12-31")
@click.option("--capital",        default=10_000.0, type=float)
@click.option("--source",         default="ccxt", type=click.Choice(["ccxt", "yfinance"]))
def backtest(strategy, pair, start, end, capital, source):
    """Run a single-strategy backtest and print metrics."""
    from data.fetcher import fetch_ohlcv_ccxt, fetch_ohlcv_yfinance
    from risk.manager import RiskManager
    from backtesting.engine import BacktestEngine
    from strategies import STRATEGIES
    from config import CONFIG, BacktestConfig

    logger.info(f"Backtesting {strategy} on {pair} ({start} → {end})")

    if source == "ccxt":
        df = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start, end)
    else:
        df = fetch_ohlcv_yfinance(pair, CONFIG.timeframe, start, end)

    cfg      = BacktestConfig(start_date=start, end_date=end, initial_capital=capital)
    rm       = RiskManager(initial_capital=capital)
    strat    = STRATEGIES[strategy](rm)
    engine   = BacktestEngine(cfg, rm)

    sig_df   = strat.run(df)
    result   = engine.run(sig_df, symbol=pair)

    click.echo(result.summary())

    # Save equity curve + HTML report
    out = CONFIG.reports_dir / f"{pair.replace('/','_')}_{strategy}_equity.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    result.equity_curve.to_csv(out)
    click.echo(f"\nEquity curve saved to {out}")

    from reports.report_generator import generate_report
    report_path = generate_report(result, strategy, pair)
    click.echo(f"HTML report    : {report_path}")


@cli.command()
@click.option("--pair", "-p", default="BTC/USDT")
@click.option("--start",      default="2021-01-01")
@click.option("--end",        default="2024-12-31")
@click.option("--source",     default="ccxt")
def compare(pair, start, end, source):
    """Run all strategies on the same data and rank them."""
    from data.fetcher import fetch_ohlcv_ccxt, fetch_ohlcv_yfinance
    from backtesting.compare import compare_strategies
    from config import CONFIG

    if source == "ccxt":
        df = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start, end)
    else:
        df = fetch_ohlcv_yfinance(pair, CONFIG.timeframe, start, end)

    cmp = compare_strategies(df, symbol=pair)
    click.echo("\n" + cmp.to_string(index=False))
    click.echo(f"\nHTML comparison report saved in {CONFIG.reports_dir}")


@cli.command()
@click.option("--strategy", "-s", default="trend_ema",
              type=click.Choice(["trend_ema", "mean_reversion", "breakout"]))
@click.option("--pair", "-p", default="BTC/USDT")
@click.option("--start",      default="2021-01-01")
@click.option("--windows",    default=5, type=int)
def optimize(strategy, pair, start, windows):
    """Walk-forward parameter optimisation."""
    from data.fetcher import fetch_ohlcv_ccxt
    from backtesting.optimizer import walk_forward_test, print_top_results, grid_search
    from strategies import STRATEGIES
    from config import CONFIG

    df = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start)

    # Default param grids per strategy
    grids = {
        "trend_ema":      {"fast": [7, 9, 12], "slow": [21, 26, 50], "adx_threshold": [20, 25, 30]},
        "mean_reversion": {"rsi_oversold": [25, 30], "rsi_overbought": [70, 75], "adx_max": [20, 25]},
        "breakout":       {"donchian_period": [15, 20, 25], "squeeze_bars": [3, 5, 8]},
    }

    logger.info(f"Walk-forward optimisation: {strategy} on {pair}")
    wf_results = walk_forward_test(STRATEGIES[strategy], df, grids[strategy], n_windows=windows)
    click.echo("\nWalk-Forward OOS Summary:")
    click.echo(wf_results.to_string(index=False))

    logger.info("Running full grid search on all data...")
    top = grid_search(STRATEGIES[strategy], df, grids[strategy])
    print_top_results(top, top_n=10)


@cli.command()
@click.option("--pair", "-p", default="BTC/USDT")
@click.option("--start",      default="2019-01-01")
def train(pair, start):
    """Train the ML model for the hybrid_ml strategy."""
    from data.fetcher import fetch_ohlcv_ccxt
    from risk.manager import RiskManager
    from strategies.hybrid_ml import HybridMLStrategy
    from config import CONFIG

    df     = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start)
    rm     = RiskManager()
    strat  = HybridMLStrategy(rm, retrain=True)
    df_ind = strat.prepare(df)
    report = strat.train(df_ind)
    if report:
        click.echo(f"\nML Training complete. Accuracy: {report.get('accuracy', 0):.2%}")


@cli.command()
@click.argument("pairs", nargs=-1)
@click.option("--strategy", "-s", default="regime_adaptive",
              type=click.Choice(list(__import__("strategies", fromlist=["STRATEGIES"]).STRATEGIES.keys())))
@click.option("--start",          default="2021-01-01")
@click.option("--capital",        default=10_000.0, type=float)
def portfolio(pairs, strategy, start, capital):
    """Portfolio backtest across multiple pairs simultaneously."""
    from data.fetcher import fetch_ohlcv_ccxt
    from backtesting.portfolio_backtest import PortfolioBacktester
    from strategies import STRATEGIES
    from config import CONFIG

    pair_list = list(pairs) or CONFIG.pairs
    click.echo(f"Portfolio backtest: {strategy} on {', '.join(pair_list)}")

    data = {}
    for p in pair_list:
        try:
            data[p] = fetch_ohlcv_ccxt(p, CONFIG.timeframe, start)
        except Exception as e:
            click.echo(f"  Skip {p}: {e}")

    bt      = PortfolioBacktester(CONFIG.backtest)
    result  = bt.run(data, STRATEGIES[strategy])
    result.summary()

    from reports.report_generator import generate_report
    for pair, res in result.pair_results.items():
        generate_report(res, strategy, pair)
    click.echo(f"\nReports saved to {CONFIG.reports_dir}")


@cli.command()
def sentiment():
    """Show current market sentiment (Fear & Greed + funding rates)."""
    from utils.sentiment import get_current_fng, get_funding_rate, sentiment_gate

    fng = get_current_fng()
    if fng:
        click.echo(f"Fear & Greed Index : {fng['value']} — {fng['classification']}")
        click.echo(f"Date               : {fng['timestamp'].strftime('%Y-%m-%d')}")
    else:
        click.echo("Fear & Greed       : unavailable")

    fr = get_funding_rate("BTC/USDT:USDT")
    if fr is not None:
        click.echo(f"BTC Funding Rate   : {fr:.6f} ({fr*100:.4f}%/8h)")

    gate = sentiment_gate(fng["value"] if fng else None, fr)
    click.echo(f"\nTrading Gate:")
    click.echo(f"  Allow longs  : {'✅' if gate['allow_long']  else '🚫'}")
    click.echo(f"  Allow shorts : {'✅' if gate['allow_short'] else '🚫'}")
    if gate["reason"] != "ok":
        click.echo(f"  Reason       : {gate['reason']}")


@cli.command()
@click.option("--strategy", "-s", default="trend_ema",
              type=click.Choice(["trend_ema", "mean_reversion", "breakout",
                                 "supertrend", "ichimoku", "regime_adaptive"]))
@click.option("--pair",  "-p", default="BTC/USDT")
@click.option("--start",       default="2021-01-01")
@click.option("--sims",        default=1000, type=int)
def montecarlo(strategy, pair, start, sims):
    """Monte Carlo robustness test — is the strategy statistically significant?"""
    from data.fetcher import fetch_ohlcv_ccxt
    from risk.manager import RiskManager
    from backtesting.engine import BacktestEngine
    from backtesting.monte_carlo import run_monte_carlo
    from strategies import STRATEGIES
    from config import CONFIG

    df      = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start)
    rm      = RiskManager()
    strat   = STRATEGIES[strategy](rm)
    sig_df  = strat.run(df)
    engine  = BacktestEngine(CONFIG.backtest, rm)
    result  = engine.run(sig_df, symbol=pair)

    click.echo(f"\nReal strategy: {result.summary()}")
    mc = run_monte_carlo(result, n_simulations=sims, strategy_name=f"{strategy}_{pair.replace('/','_')}")
    mc.summary()


@cli.command()
@click.option("--strategy", "-s", default="trend_ema")
def feature_importance(strategy):
    """Show which features drive the ML model."""
    from utils.feature_importance import plot_feature_importance
    from config import CONFIG
    imps = plot_feature_importance()
    if imps:
        click.echo("\nTop 10 features by gain:")
        for i, (feat, val) in enumerate(list(imps.items())[:10], 1):
            click.echo(f"  {i:2}. {feat:<25} {val:.4f}")
        click.echo(f"\nFull chart: {CONFIG.reports_dir}/feature_importance.html")
    else:
        click.echo("No trained model found. Run: python main.py train")


@cli.command()
def events():
    """Show upcoming high-impact macro events."""
    from utils.events_filter import EventsFilter
    ef = EventsFilter()
    safe, reason = ef.is_safe_to_trade()
    status = "SAFE" if safe else f"BLOCKED — {reason}"
    click.echo(f"Trading status : {status}")
    upcoming = ef.upcoming_events(hours_ahead=48)
    if upcoming:
        click.echo(f"\nUpcoming events (next 48h):")
        for ev in upcoming:
            click.echo(f"  {ev['datetime'].strftime('%Y-%m-%d %H:%M UTC')}  {ev['title']}")
    else:
        click.echo("No high-impact events in the next 48h.")


@cli.command()
def api():
    """Start the REST control API (FastAPI)."""
    import uvicorn
    click.echo("API running at http://localhost:8000/docs")
    uvicorn.run("bot.api:app", host="0.0.0.0", port=8000, reload=False)


@cli.command()
def stats():
    """Show live trade statistics from the database."""
    from data.database import trade_stats, get_open_trades
    from rich.console import Console
    from rich.table import Table
    console = Console()
    s = trade_stats()
    if not s:
        click.echo("No closed trades in database yet.")
    else:
        console.print(f"\n[bold cyan]Trade Statistics[/bold cyan]")
        console.print(f"  Total trades : {s['total_trades']}")
        console.print(f"  Win rate     : [green]{s['win_rate']:.1f}%[/green]")
        console.print(f"  Total PnL    : {'[green]' if s['total_pnl'] >= 0 else '[red]'}{s['total_pnl']:+.2f}[/]")
        console.print(f"  Avg trade    : {s['avg_pnl']:+.2f}")
        console.print(f"  Best trade   : [green]{s['best_trade']:+.2f}[/green]")
        console.print(f"  Worst trade  : [red]{s['worst_trade']:+.2f}[/red]")
    open_ = get_open_trades()
    console.print(f"\n  Open positions: {len(open_)}")
    for p in open_:
        console.print(f"    {p['symbol']} {p['direction']} @ {p['entry_price']:.4f}")


@cli.command()
@click.option("--strategy", "-s", default=None)
@click.option("--pair",     "-p", default="BTC/USDT")
@click.option("--start",          default="2021-01-01")
@click.option("--trials",         default=100, type=int)
def bayesian_optimize(strategy, pair, start, trials):
    """Bayesian hyperparameter optimization (Optuna) — smarter than grid search."""
    from data.fetcher import fetch_ohlcv_ccxt
    from backtesting.optuna_optimizer import optimize, PARAM_SPACES
    from strategies import STRATEGIES
    from config import CONFIG

    available = list(PARAM_SPACES.keys())
    if strategy is None or strategy not in available:
        click.echo(f"Available strategies for Optuna: {', '.join(available)}")
        if strategy is not None:
            click.echo(f"'{strategy}' not supported yet.")
        return

    df   = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start)
    result = optimize(STRATEGIES[strategy], df, strategy_name=strategy, n_trials=trials)

    click.echo(f"\nBest params : {result['best_params']}")
    click.echo(f"In-sample score : {result['in_sample_score']:.4f}")
    m = result["oos_metrics"]
    click.echo(f"OOS Sharpe  : {m.get('sharpe',0):.2f}")
    click.echo(f"OOS Return  : {m.get('total_return_pct',0):.1f}%")
    click.echo(f"OOS Max DD  : {m.get('max_drawdown_pct',0):.1f}%")


@cli.command()
@click.option("--dry-run/--async-live", default=True)
def live(dry_run):
    """Start the live trading loop (async WebSocket mode by default)."""
    import asyncio
    from config import CONFIG

    if not dry_run:
        click.confirm(
            "WARNING: This will place REAL orders. Are you sure?", abort=True
        )

    CONFIG.dry_run = dry_run

    if dry_run:
        # Sync fallback for paper trading
        from bot.live_trader import LiveTrader
        trader = LiveTrader(CONFIG)
        trader.run()
    else:
        # Full async mode for live trading
        from bot.async_trader import run_all_services
        click.echo("Starting async trader + API (8000) + Webhook (8001)...")
        asyncio.run(run_all_services(CONFIG))


@cli.command()
def dashboard():
    """Launch the interactive monitoring dashboard."""
    from reports.dashboard import app
    click.echo("Dashboard running at http://localhost:8050")
    app.run(debug=False, port=8050)


@cli.command()
@click.option("--strategy", "-s", default=None)
@click.option("--pair",     "-p", default="BTC/USDT")
@click.option("--start",          default="2021-01-01")
@click.option("--end",            default="2024-12-31")
@click.option("--capital",        default=10_000.0, type=float)
def benchmark(strategy, pair, start, end, capital):
    """Compare bot performance vs BTC/ETH buy-and-hold and S&P 500."""
    from data.fetcher import fetch_ohlcv_ccxt
    from risk.manager import RiskManager
    from backtesting.engine import BacktestEngine
    from reports.benchmark import run_benchmark
    from strategies import STRATEGIES
    from config import CONFIG

    strat_name = strategy or CONFIG.active_strategy
    if strat_name not in STRATEGIES:
        click.echo(f"Unknown strategy '{strat_name}'. Available: {', '.join(STRATEGIES)}")
        return

    df      = fetch_ohlcv_ccxt(pair, CONFIG.timeframe, start, end)
    rm      = RiskManager(initial_capital=capital)
    strat   = STRATEGIES[strat_name](rm)
    sig_df  = strat.run(df)
    engine  = BacktestEngine(CONFIG.backtest, rm)
    result  = engine.run(sig_df, symbol=pair)

    cmp = run_benchmark(result.equity_curve, start=start, end=end, initial=capital)
    click.echo("\n" + cmp.to_string(index=False))
    click.echo(f"\nBenchmark chart saved to {CONFIG.reports_dir}/benchmark_comparison.html")


@cli.command()
@click.option("--tag", default="", help="Optional tag appended to backup filename")
def backup(tag):
    """Backup the trading database."""
    from data.backup import backup as do_backup
    path = do_backup(tag=tag)
    if path and path.exists():
        click.echo(f"Backup created: {path}")
    else:
        click.echo("No database to backup yet (no trades recorded).")


@cli.command()
@click.option("--list-backups", "list_", is_flag=True, help="List available backups")
@click.option("--from-file",    default=None, help="Restore from specific backup file path")
def restore(list_, from_file):
    """List or restore from a database backup."""
    from data.backup import list_backups, restore as do_restore
    from pathlib import Path

    if list_:
        backups = list_backups()
        if not backups:
            click.echo("No backups found.")
            return
        click.echo(f"\n{'File':<35} {'Size':>8}  Modified")
        click.echo("-" * 65)
        for b in backups:
            click.echo(f"{b['file']:<35} {b['size_kb']:>6.1f} KB  {b['modified']}")
        return

    if from_file:
        do_restore(Path(from_file))
        click.echo(f"Database restored from {from_file}")
    else:
        click.echo("Use --list-backups to see available backups or --from-file PATH to restore.")


@cli.command()
@click.option("--format", "fmt", default="excel",
              type=click.Choice(["excel", "csv"]), help="Export format")
@click.option("--output", "-o", default=None, help="Output file path (optional)")
def export(fmt, output):
    """Export trade history to Excel or CSV."""
    from pathlib import Path
    output_path = Path(output) if output else None

    if fmt == "excel":
        from data.backup import export_trades_excel
        path = export_trades_excel(output_path)
    else:
        from data.backup import export_trades_csv
        path = export_trades_csv(output_path)

    click.echo(f"Trades exported to: {path}")


@cli.command("weekly-report")
@click.option("--strategy", "-s", default=None)
def weekly_report(strategy):
    """Generate and send the weekly performance report now."""
    from reports.weekly_report import generate_weekly_report
    msg = generate_weekly_report(strategy=strategy)
    click.echo("\nReport sent via Telegram:")
    click.echo(msg)


@cli.command("scheduler")
def scheduler():
    """Start the weekly report scheduler (runs every Monday 09:00 UTC)."""
    from reports.weekly_report import start_scheduler
    click.echo("Weekly report scheduler started (Monday 09:00 UTC). Press Ctrl+C to stop.")
    start_scheduler()


# ─── Version 2: S&P 500 commands ──────────────────────────────────────────────

@cli.command("sp500-backtest")
@click.option("--strategy", "-s", default="momentum_factor",
              type=click.Choice(["momentum_factor", "sector_rotation", "equity_mean_reversion",
                                 "trend_ema", "mean_reversion", "breakout"]),
              help="Strategy to use for stock selection")
@click.option("--start",   default="2015-01-01", help="Backtest start date")
@click.option("--end",     default="2024-12-31", help="Backtest end date")
@click.option("--capital", default=100_000.0, type=float, help="Initial capital (USD)")
@click.option("--top-n",   default=20, type=int,  help="Number of stocks to hold at once")
@click.option("--rebal",   default=21, type=int,  help="Rebalancing frequency (trading days)")
@click.option("--download/--no-download", default=False,
              help="Download real data from Yahoo Finance (requires internet)")
@click.option("--report/--no-report", default=True, help="Generate interactive HTML report")
def sp500_backtest(strategy, start, end, capital, top_n, rebal, download, report):
    """10-year S&P 500 portfolio backtest with MPT portfolio construction (v2)."""
    from backtesting.sp500_backtest import run_sp500_backtest
    from reports.sp500_report import generate_sp500_report
    from pathlib import Path

    click.echo(f"\n{'='*60}")
    click.echo(f"  S&P 500 Backtest — Version 2")
    click.echo(f"  Strategy : {strategy}")
    click.echo(f"  Period   : {start} → {end}")
    click.echo(f"  Capital  : ${capital:,.0f}")
    click.echo(f"  Top-N    : {top_n} stocks | Rebal every {rebal} days")
    click.echo(f"{'='*60}\n")

    result = run_sp500_backtest(
        strategy=strategy,
        start=start,
        end=end,
        initial_capital=capital,
        top_n=top_n,
        rebalance_days=rebal,
        download=download,
    )

    if report:
        out = Path("reports/sp500_backtest_report.html")
        generate_sp500_report(result, out)
        click.echo(f"\nInteractive report: {out.resolve()}")


@cli.command("portfolio-optimize")
@click.option("--method", default="risk_parity",
              type=click.Choice(["min_variance", "max_sharpe", "risk_parity"]),
              help="Portfolio optimization method")
@click.option("--start",    default="2015-01-01")
@click.option("--end",      default="2024-12-31")
@click.option("--lookback", default=252, type=int, help="Rolling lookback window (days)")
@click.option("--rebal",    default=21, type=int,  help="Rebalancing frequency (days)")
@click.option("--download/--no-download", default=False)
def portfolio_optimize(method, start, end, lookback, rebal, download):
    """Run portfolio optimization on S&P 500 universe and show equity curve (v2)."""
    from utils.portfolio_optimization import rolling_rebalance, compute_portfolio_metrics
    import numpy as np
    import pandas as pd

    click.echo(f"\nPortfolio Optimization — {method.replace('_',' ').title()}")
    click.echo(f"Period: {start} → {end} | Lookback: {lookback}d | Rebal: {rebal}d\n")

    if download:
        from data.sp500_universe import download_universe, compute_returns_matrix
        universe = download_universe(start=start, end=end)
        returns  = compute_returns_matrix(universe)
    else:
        click.echo("(Using synthetic returns — pass --download for real data)")
        np.random.seed(42)
        n_days  = (pd.to_datetime(end) - pd.to_datetime(start)).days
        dates   = pd.date_range(start, periods=n_days, freq="B")
        tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
                   "JPM", "JNJ", "XOM", "PG", "MA", "HD", "KO", "PEP"]
        returns = pd.DataFrame(
            np.random.normal(0.0004, 0.015, (len(dates), len(tickers))),
            index=dates, columns=tickers
        )

    equity = rolling_rebalance(returns, method=method, lookback=lookback, rebal_freq=rebal)

    # Compute vs equal-weight benchmark
    ew_equity = rolling_rebalance(returns, method="risk_parity", lookback=lookback, rebal_freq=rebal)
    bench_ret = returns.mean(axis=1)

    equal_weights = pd.Series(1.0 / len(returns.columns), index=returns.columns)
    pm = compute_portfolio_metrics(equal_weights, returns, benchmark_returns=bench_ret)

    click.echo(f"{'─'*40}")
    click.echo(f"  Final Equity     : ${equity.iloc[-1]:,.0f}")
    click.echo(f"  Total Return     : {(equity.iloc[-1]/10000-1)*100:+.1f}%")
    click.echo(f"  Annual Return    : {pm.get('annual_return',0)*100:+.1f}%")
    click.echo(f"  Annual Vol       : {pm.get('annual_vol',0)*100:.1f}%")
    click.echo(f"  Sharpe Ratio     : {pm.get('sharpe',0):.2f}")
    click.echo(f"  Max Drawdown     : {pm.get('max_drawdown',0)*100:.1f}%")
    click.echo(f"  Calmar Ratio     : {pm.get('calmar',0):.2f}")
    click.echo(f"{'─'*40}")


@cli.command("walkforward")
@click.option("--capital",  default=100_000.0, type=float)
@click.option("--top-n",    default=15, type=int)
@click.option("--rebal",    default=21, type=int)
@click.option("--download/--no-download", default=False)
def walkforward(capital, top_n, rebal, download):
    """Walk-forward validation: in-sample 2015-2020 → out-of-sample 2021-2024 (v2)."""
    from backtesting.walkforward_sp500 import run_walkforward
    run_walkforward(initial_capital=capital, download=download, top_n=top_n, rebalance_days=rebal)


@cli.command("sp500-download")
@click.option("--start", default="2015-01-01")
@click.option("--end",   default="2024-12-31")
@click.option("--tickers", multiple=True, help="Specific tickers (default: full 50-stock universe)")
def sp500_download(start, end, tickers):
    """Download and cache 10 years of S&P 500 daily OHLCV data (v2)."""
    from data.sp500_universe import download_universe, SP500_TICKERS
    tickers_list = list(tickers) if tickers else SP500_TICKERS
    click.echo(f"Downloading {len(tickers_list)} tickers ({start} → {end})...")
    universe = download_universe(tickers_list, start=start, end=end)
    click.echo(f"\nDownloaded {len(universe)} tickers successfully.")
    for ticker, df in list(universe.items())[:5]:
        click.echo(f"  {ticker}: {len(df)} bars ({df.index[0].date()} → {df.index[-1].date()})")
    if len(universe) > 5:
        click.echo(f"  ... and {len(universe)-5} more")


# ─────────────────────────────────────────────────────────────────────
# Prediction markets / macro filter commands
# ─────────────────────────────────────────────────────────────────────

@cli.command("polymarket")
@click.option("--ticker", "-t", default=None,
              help="Optional ticker to check WSB overcrowding (e.g. BTC, NVDA)")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output raw JSON instead of formatted table")
def polymarket_cmd(ticker, as_json):
    """Show Polymarket macro risk + Reddit WSB sentiment in real time."""
    import json as _json
    from utils.polymarket import get_macro_risk, search_markets
    from utils.wsb_sentiment import get_market_mood, get_ticker_signal
    from utils.macro_filter import get_macro_gate

    click.echo("\n⏳ Fetching Polymarket + Reddit WSB data…\n")

    gate   = get_macro_gate(ticker=ticker)
    mood   = gate  # already populated

    if as_json:
        out = {
            "macro_gate": {
                "allow_long":  gate.allow_long,
                "size_factor": gate.size_factor,
                "macro_score": gate.macro_score,
                "wsb_score":   gate.wsb_score,
                "wsb_mood":    gate.wsb_mood,
                "reason":      gate.reason,
            }
        }
        if gate.macro_report:
            out["macro_gate"]["polymarket"] = gate.macro_report.as_dict()
        if gate.ticker_signal and ticker:
            out["wsb_ticker"] = {
                "ticker":       gate.ticker_signal.ticker,
                "mentions":     gate.ticker_signal.mentions,
                "signal":       gate.ticker_signal.signal,
                "bias":         gate.ticker_signal.bias,
                "size_factor":  gate.ticker_signal.size_factor,
            }
        click.echo(_json.dumps(out, indent=2))
        return

    click.echo(gate.summary())
    click.echo()

    # Top Polymarket markets
    if gate.macro_report and gate.macro_report.top_markets:
        click.echo("📊 Top Polymarket Markets:")
        click.echo(f"  {'Question':<55} {'YES%':>6}  {'Volume':>10}")
        click.echo("  " + "─" * 76)
        for m in gate.macro_report.top_markets[:8]:
            click.echo(f"  {m.question[:55]:<55} {m.yes_prob*100:5.1f}%  ${m.volume:>10,.0f}")
        click.echo()

    # WSB ticker signal
    if ticker and gate.ticker_signal:
        sig = gate.ticker_signal
        icon = "🔴" if sig.signal == "overcrowded" else "🟢" if sig.signal == "momentum" else "⚪"
        click.echo(f"💬 WSB signal for {ticker}: {icon} {sig.signal.upper()}")
        click.echo(f"   Mentions in hot: {sig.mentions}  |  Bias: {sig.bias}  |  Size factor: {sig.size_factor:.0%}")
        click.echo()


@cli.command("wsb")
@click.option("--tickers", "-t", multiple=True,
              help="Tickers to check (repeatable, e.g. -t NVDA -t TSLA)")
@click.option("--top", default=20, show_default=True,
              help="Show top N most mentioned tickers")
def wsb_cmd(tickers, top):
    """Show Reddit WallStreetBets trending tickers and market mood."""
    from utils.wsb_sentiment import get_market_mood, get_ticker_mentions, get_ticker_signal

    click.echo("\n⏳ Fetching Reddit WSB data…\n")
    mood = get_market_mood()

    mood_icon = {"euphoric": "🚀", "bullish": "📈", "neutral": "⚖️",
                 "bearish": "📉", "fearful": "😱", "unknown": "❓"}.get(mood.mood, "❓")

    click.echo(f"╔══ Reddit WallStreetBets Sentiment ═════════════════╗")
    click.echo(f"║  Mood    : {mood_icon} {mood.mood.upper():<10}  (score: {mood.score}/100)")
    click.echo(f"║  Bullish keywords: {mood.bull_count:4}  |  Bearish: {mood.bear_count:4}")
    click.echo(f"╚════════════════════════════════════════════════════╝\n")

    # Specific tickers requested
    if tickers:
        click.echo(f"{'Ticker':<8} {'Mentions':>9} {'Signal':<14} {'Bias':<22} {'Size Factor':>12}")
        click.echo("─" * 70)
        for t in tickers:
            sig = get_ticker_signal(t)
            icon = "🔴" if sig.signal == "overcrowded" else "🟢" if sig.signal == "momentum" else "⚪"
            click.echo(f"{t:<8} {sig.mentions:>9}  {icon} {sig.signal:<12} {sig.bias:<22} {sig.size_factor*100:.0f}%")
        click.echo()

    # Top trending tickers
    click.echo(f"Top {top} Trending Tickers on WSB (hot feed):")
    click.echo(f"  {'#':<4} {'Ticker':<8} {'Mentions':>9}  Signal")
    click.echo("  " + "─" * 40)
    mentions = get_ticker_mentions()
    for i, (t, count) in enumerate(list(mentions.items())[:top], 1):
        sig  = "🔴 overcrowded" if count > 20 else "🟢 momentum" if count > 5 else "⚪ low"
        click.echo(f"  {i:<4} {t:<8} {count:>9}  {sig}")
    click.echo()


# ─────────────────────────────────────────────────────────────────────
# AI Trading Advisor
# ─────────────────────────────────────────────────────────────────────

@cli.command("advisor")
@click.option("--question", "-q", default=None,
              help="One-shot question (omit for interactive mode)")
@click.option("--watchlist", "-w", multiple=True,
              help="Pre-scan watchlist before starting (e.g. -w BTC/USDT -w ETH/USDT)")
def advisor_cmd(question, watchlist):
    """AI trading advisor — ask which assets are ready to enter, check filters, macro outlook.

    \b
    Examples:
      python main.py advisor -q "¿BTC pasa los filtros para invertir?"
      python main.py advisor -q "Which assets on my watchlist are ready?"
      python main.py advisor -w BTC/USDT -w ETH/USDT -w SOL/USDT
      python main.py advisor          # interactive REPL
    """
    import os
    from bot.trading_advisor import ask

    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.echo(
            "Error: ANTHROPIC_API_KEY not set.\n"
            "Add it to your .env file: ANTHROPIC_API_KEY=sk-ant-...",
            err=True,
        )
        raise SystemExit(1)

    # Pre-scan watchlist and inject as first question
    history = []
    if watchlist:
        wl_str = ", ".join(watchlist)
        click.echo(f"\nEscaneando watchlist: {wl_str} ...\n")
        _, history = ask(
            f"Scan this watchlist and tell me which ones are ready to enter: {wl_str}",
            history=history,
        )
        # Print the pre-scan result
        last_answer = next(
            (b.text for b in history[-1]["content"] if hasattr(b, "text")), ""
        ) if history and isinstance(history[-1].get("content"), list) else ""
        if last_answer:
            click.echo(f"Advisor: {last_answer}\n")

    # One-shot mode
    if question:
        answer, _ = ask(question, history=history)
        click.echo(f"\n{answer}\n")
        return

    # Interactive REPL
    click.echo(
        "\n┌─────────────────────────────────────────────────────────┐\n"
        "│  Trading Advisor — AI con acceso a datos en tiempo real  │\n"
        "│  Escribe 'exit' o Ctrl-C para salir                       │\n"
        "└─────────────────────────────────────────────────────────┘\n"
    )

    while True:
        try:
            q = click.prompt("Tú", prompt_suffix=" > ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nHasta luego.")
            break

        if q.strip().lower() in ("exit", "quit", "salir", "q", "bye"):
            click.echo("Hasta luego.")
            break
        if not q.strip():
            continue

        try:
            click.echo("\nAdvisor: ", nl=False)
            answer, history = ask(q, history=history)
            click.echo(answer + "\n")
        except Exception as e:
            click.echo(f"\nError: {e}\n", err=True)


@cli.command("ask")
@click.argument("question")
@click.option("--ticker", "-t", default=None, help="Specific asset to check (e.g. BTC/USDT)")
def ask_cmd(question, ticker):
    """Quick one-shot question to the trading advisor.

    \b
    Examples:
      python main.py ask "¿Cuál es el riesgo macro ahora mismo?"
      python main.py ask "Is NVDA a good entry?" --ticker NVDA
      python main.py ask "¿Qué dice el mercado de predicción sobre la recesión?"
    """
    import os
    from bot.trading_advisor import ask

    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.echo("Error: ANTHROPIC_API_KEY not set.", err=True)
        raise SystemExit(1)

    full_q = f"{question} (ticker: {ticker})" if ticker else question

    click.echo()
    answer, _ = ask(full_q)
    click.echo(answer)
    click.echo()


if __name__ == "__main__":
    cli()
