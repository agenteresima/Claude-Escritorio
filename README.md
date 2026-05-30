# Professional Trading Bot

A production-ready algorithmic trading system combining the best techniques from Freqtrade, Jesse, Backtrader, vectorbt, QuantConnect, and Lopez de Prado's research.

## Features

- **15 strategies** covering all market regimes: trend, mean-reversion, breakout, ML meta-labelling, regime-adaptive, ensemble, grid, DCA, MACD divergence, Heikin Ashi, Volume Profile
- **Walk-forward optimization** and Bayesian hyperparameter search (Optuna)
- **Monte Carlo** robustness testing
- **Portfolio backtest** across multiple pairs simultaneously
- **Benchmark comparison** vs BTC/ETH buy-and-hold and S&P 500
- **Async live trading** via WebSocket + REST fallback
- **5 entry filters**: macro events, sentiment (Fear & Greed), order book imbalance, candle patterns, correlation filter
- **Risk management**: Kelly criterion, ATR-based sizing, drawdown circuit-breaker, portfolio heat
- **Monitoring**: Dash dashboard, REST API, Telegram bot, weekly HTML report
- **Persistence**: SQLite with backup/restore and Excel export

---

## Quick Start

```bash
bash install.sh
```

Edit `.env` with your API keys, then:

```bash
make backtest       # backtest default strategy on BTC/USDT
make compare        # rank all 15 strategies
make live           # paper trade (dry run)
make dashboard      # open browser dashboard
```

---

## Installation

### Requirements
- Python 3.10+
- (Optional) TA-Lib C library for faster indicator computation

```bash
# Clone and install
git clone https://github.com/agenteresima/Claude-Escritorio.git
cd Claude-Escritorio
bash install.sh
```

### Docker

```bash
docker-compose up -d --build
```

This starts 5 services: trader, api (port 8000), dashboard (port 8050), webhook (port 8001), telegram.

---

## Configuration

Copy `.env.example` to `.env` and fill in:

```env
EXCHANGE_API_KEY=your_key
EXCHANGE_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

All parameters can also be tuned in `config/config.yaml`.

---

## Strategies

| Name | Style | Key Signals |
|------|-------|-------------|
| `trend_ema` | Trend | EMA crossover + ADX + RSI + vol ratio |
| `mean_reversion` | Mean-rev | RSI + Bollinger Bands, ADX < 25 |
| `breakout` | Breakout | Donchian + TTM Squeeze |
| `supertrend` | Trend | SuperTrend flip + ADX + ATR |
| `vwap_bounce` | Intraday | VWAP deviation + MFI |
| `ichimoku` | Trend | Kumo breakout + TK cross + Chikou |
| `mtf` | Multi-TF | 1h + 4h trend alignment |
| `hybrid_ml` | ML | XGBoost triple-barrier meta-labels |
| `regime_adaptive` | Adaptive | Detects regime → routes sub-strategy |
| `ensemble` | Ensemble | Majority voting across 5 strategies |
| `grid_trading` | Grid | N levels, range-only filter |
| `dca` | DCA | Safety orders with volume scale |
| `macd_divergence` | Divergence | Regular + hidden MACD divergences |
| `heikin_ashi` | Trend | HA candle flip with confirmation bars |
| `volume_profile` | Volume | POC/VAH/VAL bounce and breakout |

---

## CLI Commands

```bash
# Backtesting
python main.py backtest  --strategy trend_ema --pair BTC/USDT --start 2021-01-01
python main.py compare   --pair BTC/USDT
python main.py portfolio BTC/USDT ETH/USDT SOL/USDT --strategy regime_adaptive
python main.py optimize  --strategy trend_ema --pair BTC/USDT --windows 5
python main.py bayesian-optimize --strategy trend_ema --pair BTC/USDT --trials 200
python main.py montecarlo --strategy trend_ema --pair BTC/USDT --sims 1000
python main.py benchmark  --strategy regime_adaptive --pair BTC/USDT

# ML
python main.py train            --pair BTC/USDT --start 2019-01-01
python main.py feature-importance

# Live
python main.py live             # paper trade (sync)
python main.py live --async-live  # async WebSocket + API + webhook
python main.py api              # REST API only
python main.py dashboard        # monitoring UI

# Data & Reports
python main.py stats
python main.py events
python main.py sentiment
python main.py backup
python main.py export           --format excel
python main.py weekly-report
python main.py scheduler        # block, send every Monday 09:00 UTC

# Or use make
make backtest STRATEGY=ichimoku PAIR=ETH/USDT
make compare
make optimize STRATEGY=breakout
make bayesian STRATEGY=trend_ema TRIALS=200
make montecarlo
make benchmark
make live
make dashboard
make api
make backup
make export
make weekly
make train
make features
```

---

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make install` | Install Python dependencies |
| `make test` | Run all tests |
| `make backtest` | Backtest (PAIR, STRATEGY, START vars) |
| `make compare` | Compare all strategies |
| `make optimize` | Walk-forward grid search |
| `make bayesian` | Optuna Bayesian optimization |
| `make montecarlo` | Monte Carlo simulation |
| `make benchmark` | Compare vs buy-and-hold benchmarks |
| `make portfolio` | Multi-pair portfolio backtest |
| `make train` | Train ML model |
| `make features` | XGBoost feature importance |
| `make live` | Paper trading |
| `make dashboard` | Dash monitoring UI |
| `make api` | FastAPI control server |
| `make backup` | Backup database |
| `make export` | Export trades to Excel |
| `make weekly` | Send weekly report now |
| `make lint` | Flake8 code style check |

---

## Architecture

```
├── config/          Pydantic settings + YAML config
├── data/            OHLCV fetcher, SQLite DB, WebSocket feed, backup
├── utils/           Indicators, candle patterns, sentiment, events, orderbook, rate limiter
├── strategies/      15 strategy classes
├── risk/            Position sizing, ATR stops, portfolio heat
├── backtesting/     Engine, comparator, optimizer, portfolio BT, Monte Carlo, Optuna
├── bot/             Live trader (sync + async), API, Telegram, notifier, position manager
├── reports/         Dash dashboard, HTML reports, benchmark, weekly report
├── tests/           pytest test suite
├── main.py          CLI entry point (20 commands)
├── Makefile         25+ make targets
├── install.sh       One-command setup
├── Dockerfile       Python 3.11-slim + TA-Lib
└── docker-compose.yml  5-service stack
```

### Live Trading Flow

```
WebSocketFeed ──► CandleBuffer
                       │
              AsyncLiveTrader
               ├── EventsFilter     (macro blackout)
               ├── SentimentGate    (Fear & Greed)
               ├── OrderBookFilter  (imbalance)
               ├── CandlePatterns   (confirmation)
               ├── CorrelationFilter (diversification)
               └── Strategy.run()
                       │
              RiskManager (sizing + stops)
                       │
              PortfolioHeatManager  (aggregate risk)
                       │
              Exchange.create_order()
                       │
              Database (SQLite)
                       │
              Notifier (Telegram)
```

---

## Risk Management

All position sizes go through layered validation:

1. **ATR-based stop** — stop placed 1.5× ATR below entry
2. **Fixed-fraction sizing** — default 1% of capital per trade
3. **Kelly criterion** — optional; capped at 25%
4. **Portfolio heat** — max 6% of capital at risk across all open positions
5. **Drawdown circuit-breaker** — halts trading if DD exceeds 15%
6. **Correlation filter** — blocks new positions correlated > 0.80 with existing

---

## Testing

```bash
make test                        # all tests
pytest tests/ -m "not slow"      # skip slow integration tests
pytest tests/test_phase6.py -v   # Phase 6 modules only
```

---

## API Endpoints

The REST API runs on port 8000 (authenticated with `x-api-key` header):

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Bot state, equity, open positions |
| GET | `/trades` | Recent closed trades |
| GET | `/equity` | Equity curve data |
| GET | `/metrics` | Performance metrics |
| GET | `/signals` | Recent signal log |
| POST | `/strategy` | Hot-swap active strategy |
| POST | `/pause` | Pause trading |
| POST | `/resume` | Resume trading |
| POST | `/close/{symbol}` | Force-close a position |

---

## Disclaimer

This software is for educational and research purposes. Past backtest performance does not guarantee future results. Never trade with money you cannot afford to lose. Always start with paper trading.
