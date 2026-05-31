# Professional Trading Bot — Makefile
# Usage: make <target>

PYTHON     := python
PIP        := pip
PAIR       ?= BTC/USDT
STRATEGY   ?= regime_adaptive
START      ?= 2021-01-01

.PHONY: help install test test-fast test-cov backtest compare optimize train live dashboard api benchmark backup restore export weekly lint clean sp500 sp500-download portfolio-optimize v2

help:
	@echo ""
	@echo "  Professional Trading Bot"
	@echo "  ========================"
	@echo ""
	@echo "  Setup:"
	@echo "    make install       Install all dependencies"
	@echo ""
	@echo "  Backtesting:"
	@echo "    make backtest      PAIR=BTC/USDT STRATEGY=trend_ema"
	@echo "    make compare       PAIR=BTC/USDT  (run all strategies)"
	@echo "    make optimize      PAIR=BTC/USDT STRATEGY=trend_ema"
	@echo "    make bayesian      PAIR=BTC/USDT STRATEGY=trend_ema"
	@echo "    make montecarlo    PAIR=BTC/USDT STRATEGY=trend_ema"
	@echo "    make benchmark     Compare vs BTC/ETH/S&P500"
	@echo "    make portfolio     Multi-pair portfolio backtest"
	@echo ""
	@echo "  Training:"
	@echo "    make train         Train ML model (hybrid_ml strategy)"
	@echo "    make features      Show XGBoost feature importance"
	@echo ""
	@echo "  Live trading:"
	@echo "    make live          Start paper trading (dry run)"
	@echo "    make dashboard     Launch monitoring dashboard"
	@echo "    make api           Start REST control API"
	@echo ""
	@echo "  Data:"
	@echo "    make backup        Backup database"
	@echo "    make export        Export trades to Excel"
	@echo ""
	@echo "  Dev:"
	@echo "    make test          Run all tests"
	@echo "    make test-fast     Skip slow/integration/ml tests"
	@echo "    make test-cov      Coverage report → htmlcov/index.html"
	@echo "    make lint          Check code style (flake8)"
	@echo "    make health        Quick API health check"
	@echo "    make weekly        Send weekly performance report"
	@echo ""
	@echo "  Version 2 — S&P 500:"
	@echo "    make sp500         10-year backtest (synthetic, offline)"
	@echo "    make sp500-live    10-year backtest (Yahoo Finance download)"
	@echo "    make sp500-download Download 50-stock universe data"
	@echo "    make portfolio-optimize  MPT portfolio optimization"
	@echo "    make v2            Show all v2 commands and options"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-up     Build and start all services"
	@echo "    make docker-down   Stop all services"
	@echo "    make docker-logs   Tail live trader logs"
	@echo ""

install:
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

test:
	pytest tests/ -v --tb=short -q

test-fast:
	pytest tests/ -v --tb=short -q -m "not slow and not integration and not ml"

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing \
	  -m "not slow and not integration and not ml" -q
	@echo "Coverage report: htmlcov/index.html"

backtest:
	$(PYTHON) main.py backtest --strategy $(STRATEGY) --pair "$(PAIR)" --start $(START)

compare:
	$(PYTHON) main.py compare --pair "$(PAIR)" --start $(START)

optimize:
	$(PYTHON) main.py optimize --strategy $(STRATEGY) --pair "$(PAIR)" --start $(START)

bayesian:
	$(PYTHON) main.py bayesian-optimize --strategy $(STRATEGY) --pair "$(PAIR)" --trials 200

montecarlo:
	$(PYTHON) main.py montecarlo --strategy $(STRATEGY) --pair "$(PAIR)" --sims 1000

portfolio:
	$(PYTHON) main.py portfolio BTC/USDT ETH/USDT SOL/USDT BNB/USDT --strategy $(STRATEGY)

train:
	$(PYTHON) main.py train --pair "$(PAIR)" --start 2019-01-01

features:
	$(PYTHON) main.py feature-importance

benchmark:
	@$(PYTHON) -c "                                           \
from data.fetcher import fetch_ohlcv_ccxt;                   \
from risk.manager import RiskManager;                        \
from strategies import STRATEGIES;                           \
from backtesting.engine import BacktestEngine;               \
from reports.benchmark import run_benchmark;                 \
from config import CONFIG;                                   \
df = fetch_ohlcv_ccxt('$(PAIR)', '1h', '$(START)');         \
rm = RiskManager();                                          \
strat = STRATEGIES['$(STRATEGY)'](rm);                      \
sig = strat.run(df);                                         \
res = BacktestEngine(CONFIG.backtest, rm).run(sig);          \
cmp = run_benchmark(res.equity_curve, '$(START)');           \
print(cmp.to_string(index=False))"

live:
	$(PYTHON) main.py live --dry-run

dashboard:
	$(PYTHON) main.py dashboard

api:
	$(PYTHON) main.py api

sentiment:
	$(PYTHON) main.py sentiment

events:
	$(PYTHON) main.py events

stats:
	$(PYTHON) main.py stats

weekly:
	$(PYTHON) main.py weekly-report

backup:
	$(PYTHON) main.py backup

restore:
	$(PYTHON) main.py restore --list-backups

export:
	$(PYTHON) main.py export --format excel

benchmark:
	$(PYTHON) main.py benchmark --strategy $(STRATEGY) --pair "$(PAIR)" --start $(START)

health:
	@bash scripts/health_check.sh

lint:
	@$(PYTHON) -m flake8 strategies/ risk/ bot/ utils/ data/ --max-line-length=100 --ignore=E501,W503 2>/dev/null || echo "Install flake8: pip install flake8"

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f trader

# ─── Version 2: S&P 500 ──────────────────────────────────────────────────────
SP500_STRATEGY ?= momentum_factor
SP500_START    ?= 2015-01-01
SP500_END      ?= 2024-12-31
SP500_CAPITAL  ?= 100000
SP500_TOPN     ?= 20

sp500:
	$(PYTHON) main.py sp500-backtest \
	  --strategy $(SP500_STRATEGY) \
	  --start $(SP500_START) \
	  --end $(SP500_END) \
	  --capital $(SP500_CAPITAL) \
	  --top-n $(SP500_TOPN) \
	  --no-download

sp500-live:
	$(PYTHON) main.py sp500-backtest \
	  --strategy $(SP500_STRATEGY) \
	  --start $(SP500_START) \
	  --end $(SP500_END) \
	  --capital $(SP500_CAPITAL) \
	  --top-n $(SP500_TOPN) \
	  --download

sp500-download:
	$(PYTHON) main.py sp500-download --start $(SP500_START) --end $(SP500_END)

portfolio-optimize:
	$(PYTHON) main.py portfolio-optimize --method $(or $(METHOD),risk_parity)

v2:
	@echo ""
	@echo "  Version 2 — S&P 500 Commands"
	@echo "  ============================="
	@echo "  make sp500                  10-year backtest (synthetic data, fast)"
	@echo "  make sp500-live             10-year backtest (real Yahoo Finance data)"
	@echo "  make sp500-download         Download & cache S&P 500 OHLCV data"
	@echo "  make portfolio-optimize     MPT portfolio optimization"
	@echo ""
	@echo "  Options:"
	@echo "    SP500_STRATEGY=momentum_factor|sector_rotation|equity_mean_reversion"
	@echo "    SP500_TOPN=20 (number of stocks to hold)"
	@echo "    METHOD=min_variance|max_sharpe|risk_parity"
	@echo ""

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	echo "Cleaned"
