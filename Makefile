# Professional Trading Bot — Makefile
# Usage: make <target>

PYTHON     := python
PIP        := pip
PAIR       ?= BTC/USDT
STRATEGY   ?= regime_adaptive
START      ?= 2021-01-01

.PHONY: help install test backtest compare optimize train live dashboard api benchmark backup lint

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
	@echo "    make lint          Check code style"
	@echo "    make weekly        Send weekly performance report now"
	@echo ""

install:
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

test:
	pytest tests/ -v --tb=short -q

test-fast:
	pytest tests/ -v --tb=short -q -m "not slow"

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
	$(PYTHON) reports/weekly_report.py --now

backup:
	@$(PYTHON) -c "from data.backup import backup; p=backup(); print(f'Backup: {p}')"

export:
	@$(PYTHON) -c "from data.backup import export_trades_excel; p=export_trades_excel(); print(f'Excel: {p}')"

lint:
	@$(PYTHON) -m flake8 strategies/ risk/ bot/ utils/ data/ --max-line-length=100 --ignore=E501,W503 2>/dev/null || echo "Install flake8: pip install flake8"

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f trader

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	echo "Cleaned"
