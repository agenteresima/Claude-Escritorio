# Professional Trading Bot — CLAUDE.md

This file documents the codebase for AI assistants working on this project.

## Project layout

```
config/       BotConfig (Pydantic), config.yaml, .env via python-dotenv
data/         OHLCV fetcher (CCXT + yfinance), SQLite DB, WebSocket feed, backup
utils/        Indicators (pandas-ta), candle patterns, sentiment, events filter,
              order book, correlation filter, rate limiter, performance metrics
strategies/   15 strategy classes (all extend BaseStrategy)
risk/         RiskManager (sizing, stops, circuit-breaker), PortfolioHeatManager
backtesting/  Engine, comparator, optimizer, walk-forward, portfolio, Monte Carlo, Optuna
bot/          LiveTrader (sync), AsyncLiveTrader, FastAPI, Telegram, webhook,
              position manager, notifier, auto-compound, strategy monitor, shutdown
reports/      Dash dashboard, HTML report generator, benchmark, weekly report
tests/        pytest test suite (unit + integration, ~300 test cases)
main.py       Click CLI (20 commands)
Makefile      25+ targets
install.sh    One-command setup
```

## Development commands

```bash
# Setup
bash install.sh
source .venv/bin/activate

# Tests (fast)
make test-fast          # skips slow/integration/ml tests

# Backtest
make backtest STRATEGY=trend_ema PAIR=BTC/USDT

# Format / lint
black . --line-length 100
isort .
flake8 strategies/ risk/ bot/ utils/ data/ --max-line-length=100 --ignore=E501,W503

# Docker
docker-compose up -d --build
docker-compose --profile production up -d  # includes nginx
```

## Key design decisions

- All strategies extend `strategies/base.py:BaseStrategy` — `prepare()` + `generate_signals()`
- `STRATEGIES` dict in `strategies/__init__.py` is the single source of truth — add new strategies there
- All live trades persisted to SQLite immediately (survives crashes)
- `RiskManager.validate_signal()` is the last gate before order placement
- `PortfolioHeatManager` caps total risk at 6% of capital across all open positions
- Async trader and sync trader share the same strategy classes and DB
- Entry filters are layered: events → sentiment → order book → candle pattern → correlation

## Adding a new strategy

1. Create `strategies/my_strategy.py` extending `BaseStrategy`
2. Register it in `strategies/__init__.py` under `STRATEGIES`
3. Add param space to `backtesting/optuna_optimizer.py:PARAM_SPACES`
4. Add tests in `tests/`

## Environment variables

See `.env.example` for full list. Minimum required for live trading:
```
EXCHANGE_API_KEY
EXCHANGE_API_SECRET
EXCHANGE_SANDBOX=false  # only when ready for real trading
DRY_RUN=false           # only when ready for real trading
```

## Database schema

SQLite at `data/bot.db`:
- `trades` — all open and closed positions
- `equity_snapshots` — periodic equity curve
- `bot_state` — key/value persistent state (paused, active_strategy, etc.)
- `signal_log` — recent signal history for debugging

## Important: never trade real money without

1. Running `make backtest` and `make compare` first
2. Paper trading (`DRY_RUN=true`) for at least 2 weeks
3. Setting `MAX_DRAWDOWN_PCT=0.10` (conservative) initially
4. Monitoring the Dash dashboard daily
