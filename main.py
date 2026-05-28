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
@click.option("--dry-run/--live", default=True)
def live(dry_run):
    """Start the live trading loop."""
    from bot.live_trader import LiveTrader
    from config import CONFIG

    if not dry_run:
        click.confirm(
            "WARNING: This will place REAL orders. Are you sure?", abort=True
        )

    CONFIG.dry_run = dry_run
    trader = LiveTrader(CONFIG)
    trader.run()


@cli.command()
def dashboard():
    """Launch the interactive monitoring dashboard."""
    from reports.dashboard import app
    click.echo("Dashboard running at http://localhost:8050")
    app.run(debug=False, port=8050)


if __name__ == "__main__":
    cli()
