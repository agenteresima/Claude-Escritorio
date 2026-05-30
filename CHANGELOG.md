# Changelog

## [1.0.0] — 2026-05-30

### Added
- **15 trading strategies**: trend_ema, mean_reversion, breakout, supertrend, vwap_bounce,
  ichimoku, mtf, hybrid_ml, regime_adaptive, ensemble, grid_trading, dca, macd_divergence,
  heikin_ashi, volume_profile
- **Backtesting engine** with commission, slippage, trailing stops, walk-forward optimization
- **Bayesian optimization** via Optuna (TPE sampler, 200 trials default)
- **Monte Carlo** simulation (1000 shuffles, P(ruin) and statistical significance)
- **Portfolio backtester** across multiple pairs simultaneously
- **Benchmark comparison** vs BTC/ETH buy-and-hold and S&P 500 (SPY/QQQ)
- **Machine learning**: XGBoost with Lopez de Prado triple-barrier labels, SHAP feature importance
- **Async live trader**: asyncio + WebSocket feed (ccxtpro / REST fallback)
- **5 entry filters**: macro events, sentiment (Fear & Greed), order book imbalance,
  candle patterns, correlation filter
- **Risk management**: Kelly criterion, ATR sizing, drawdown circuit-breaker, portfolio heat (6%)
- **REST API** (FastAPI, port 8000) with API key auth — 10 endpoints
- **Dash dashboard** (port 8050) with equity curve, drawdown heatmap, strategy selector
- **Telegram bot** with 8 command handlers (/status, /pause, /resume, /stats, /close, /strategy, /events, /help)
- **TradingView webhook** (port 8001) with HMAC verification
- **Weekly HTML + Telegram report** scheduler (every Monday 09:00 UTC)
- **SQLite persistence** with backup/restore and Excel/CSV export
- **Docker Compose** 5-service stack (trader, api, dashboard, webhook, telegram)
- **Nginx reverse proxy** config with HTTPS, rate limiting, and WebSocket support
- **GitHub Actions CI** — tests on Python 3.10/3.11/3.12, lint, Docker build
- **Makefile** with 25+ targets
- **One-command install** via `install.sh`
- **pyproject.toml** for proper packaging
- **Comprehensive test suite**: 200+ test cases across all modules
