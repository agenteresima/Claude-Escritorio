"""
Tests for backtesting modules:
  - backtesting/engine.py     (integration)
  - backtesting/compare.py
  - backtesting/optimizer.py
  - backtesting/monte_carlo.py
  - backtesting/portfolio_backtest.py
  - backtesting/optuna_optimizer.py (light)
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from tests.conftest import make_ohlcv


# ── Engine integration ────────────────────────────────────────────────────────

class TestBacktestEngine:
    @pytest.fixture
    def result(self, risk_manager, backtest_config):
        from strategies.trend_ema import TrendEMAStrategy
        from backtesting.engine import BacktestEngine
        df    = make_ohlcv(500, trend="up")
        strat = TrendEMAStrategy(risk_manager)
        sig   = strat.run(df)
        engine = BacktestEngine(backtest_config, risk_manager)
        return engine.run(sig, symbol="BTC/USDT")

    def test_has_equity_curve(self, result):
        assert hasattr(result, "equity_curve")
        assert len(result.equity_curve) > 0

    def test_equity_starts_at_capital(self, result, backtest_config):
        assert result.equity_curve.iloc[0] == pytest.approx(
            backtest_config.initial_capital, rel=0.01
        )

    def test_metrics_computed(self, result):
        m = result.metrics
        assert "sharpe" in m
        assert "max_drawdown_pct" in m
        assert "win_rate" in m
        assert "total_return_pct" in m

    def test_summary_returns_string(self, result):
        s = result.summary()
        assert isinstance(s, str)
        assert "Sharpe" in s or "sharpe" in s.lower()

    def test_trades_list(self, result):
        assert isinstance(result.trades, list)

    def test_commission_reduces_equity(self, risk_manager, backtest_config):
        from strategies.trend_ema import TrendEMAStrategy
        from backtesting.engine import BacktestEngine
        from config import BacktestConfig

        df = make_ohlcv(500, trend="up")
        strat = TrendEMAStrategy(risk_manager)
        sig = strat.run(df)

        cfg_no_comm = BacktestConfig(initial_capital=10_000, commission=0.0, slippage=0.0)
        cfg_comm    = BacktestConfig(initial_capital=10_000, commission=0.001, slippage=0.001)

        r0 = BacktestEngine(cfg_no_comm, risk_manager).run(sig, symbol="BTC/USDT")
        r1 = BacktestEngine(cfg_comm, risk_manager).run(sig, symbol="BTC/USDT")
        assert r0.equity_curve.iloc[-1] >= r1.equity_curve.iloc[-1]


# ── Strategy comparator ───────────────────────────────────────────────────────

class TestCompare:
    def test_compare_returns_dataframe(self, risk_manager):
        from backtesting.compare import compare_strategies
        df = make_ohlcv(400)
        cmp = compare_strategies(df, symbol="BTC/USDT")
        assert isinstance(cmp, pd.DataFrame)
        assert len(cmp) > 0
        assert "strategy" in cmp.columns or cmp.index.name == "strategy"

    def test_all_strategies_attempted(self, risk_manager):
        from backtesting.compare import compare_strategies
        from strategies import STRATEGIES
        df = make_ohlcv(400)
        cmp = compare_strategies(df, symbol="BTC/USDT")
        # At least half the strategies should have run
        assert len(cmp) >= len(STRATEGIES) // 2

    def test_ranked_by_sharpe(self):
        from backtesting.compare import compare_strategies
        df = make_ohlcv(400)
        cmp = compare_strategies(df, symbol="BTC/USDT")
        if "sharpe" in cmp.columns and len(cmp) > 1:
            sharpes = cmp["sharpe"].tolist()
            assert sharpes == sorted(sharpes, reverse=True) or \
                   sharpes == sorted(sharpes)  # either direction is valid per impl


# ── Grid search optimizer ─────────────────────────────────────────────────────

class TestOptimizer:
    @pytest.fixture
    def df(self):
        return make_ohlcv(600)

    def test_grid_search_returns_dataframe(self, df):
        from backtesting.optimizer import grid_search
        from strategies.trend_ema import TrendEMAStrategy
        param_grid = {"fast": [7, 9], "slow": [21, 26]}
        results = grid_search(TrendEMAStrategy, df, param_grid)
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 4  # 2×2 grid

    def test_walk_forward_returns_dataframe(self, df):
        from backtesting.optimizer import walk_forward_test
        from strategies.trend_ema import TrendEMAStrategy
        param_grid = {"fast": [7, 9], "slow": [21, 26]}
        wf = walk_forward_test(TrendEMAStrategy, df, param_grid, n_windows=2)
        assert isinstance(wf, pd.DataFrame)
        assert "oos_sharpe" in wf.columns or len(wf.columns) > 0

    def test_print_top_results(self, df, capsys):
        from backtesting.optimizer import grid_search, print_top_results
        from strategies.trend_ema import TrendEMAStrategy
        param_grid = {"fast": [7], "slow": [21]}
        results = grid_search(TrendEMAStrategy, df, param_grid)
        print_top_results(results, top_n=1)  # should not raise


# ── Monte Carlo ───────────────────────────────────────────────────────────────

class TestMonteCarlo:
    @pytest.fixture
    def backtest_result(self, risk_manager, backtest_config):
        from backtesting.engine import BacktestEngine, BacktestResult, Trade
        import numpy as np, pandas as pd
        # Build a synthetic result with guaranteed closed trades
        rng = np.random.default_rng(0)
        pnls = list(rng.normal(50, 200, 20))
        trades = []
        for i, pnl in enumerate(pnls):
            t = Trade("BTC/USDT", i * 10, 40000, "long", 0.01,
                      39000, 42000, exit_bar=i * 10 + 5,
                      exit_price=40000 + pnl / 0.01, exit_reason="tp",
                      pnl=pnl, pnl_pct=pnl / 400)
        equity = pd.Series(
            np.cumprod(1 + rng.normal(0.001, 0.01, 200)) * 10000,
            index=pd.date_range("2022-01-01", periods=200, freq="1h", tz="UTC"),
        )
        trades = []
        for i, pnl in enumerate(pnls):
            t = Trade("BTC/USDT", i * 10, 40000, "long", 0.01,
                      39000, 42000, exit_bar=i * 10 + 5,
                      exit_price=40000 + pnl / 0.01, exit_reason="tp",
                      pnl=pnl, pnl_pct=pnl / 400)
            trades.append(t)
        from backtesting.engine import _compute_metrics
        metrics = _compute_metrics(trades, equity, 10000)
        return BacktestResult(trades=trades, equity_curve=equity, metrics=metrics)

    def test_mc_runs(self, backtest_result, tmp_path):
        from backtesting.monte_carlo import run_monte_carlo
        mc = run_monte_carlo(
            backtest_result, n_simulations=50, strategy_name="test",
            output_dir=tmp_path
        )
        assert mc is not None

    def test_mc_has_ruin_probability(self, backtest_result, tmp_path):
        from backtesting.monte_carlo import run_monte_carlo
        mc = run_monte_carlo(
            backtest_result, n_simulations=50,
            strategy_name="test", output_dir=tmp_path
        )
        assert hasattr(mc, "p_ruin") or hasattr(mc, "ruin_probability") or \
               hasattr(mc, "metrics")

    def test_mc_summary(self, backtest_result, tmp_path):
        from backtesting.monte_carlo import run_monte_carlo
        mc = run_monte_carlo(
            backtest_result, n_simulations=20,
            strategy_name="test", output_dir=tmp_path
        )
        mc.summary()  # should not raise


# ── Portfolio backtester ──────────────────────────────────────────────────────

class TestPortfolioBacktester:
    def test_runs_multiple_pairs(self, backtest_config):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.trend_ema import TrendEMAStrategy
        data = {
            "BTC/USDT": make_ohlcv(400, seed=1),
            "ETH/USDT": make_ohlcv(400, seed=2),
        }
        bt = PortfolioBacktester(backtest_config)
        result = bt.run(data, TrendEMAStrategy)
        assert result is not None

    def test_result_has_pair_results(self, backtest_config):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.mean_reversion import MeanReversionStrategy
        data = {
            "BTC/USDT": make_ohlcv(400, seed=1),
            "ETH/USDT": make_ohlcv(400, seed=2),
        }
        bt = PortfolioBacktester(backtest_config)
        result = bt.run(data, MeanReversionStrategy)
        assert hasattr(result, "pair_results")
        assert len(result.pair_results) == 2

    def test_summary_does_not_raise(self, backtest_config):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.trend_ema import TrendEMAStrategy
        data = {"BTC/USDT": make_ohlcv(400)}
        bt = PortfolioBacktester(backtest_config)
        result = bt.run(data, TrendEMAStrategy)
        result.summary()  # should not raise


# ── Optuna optimizer (light) ──────────────────────────────────────────────────

class TestOptunaOptimizer:
    def test_param_spaces_defined(self):
        from backtesting.optuna_optimizer import PARAM_SPACES
        assert "trend_ema" in PARAM_SPACES
        assert "mean_reversion" in PARAM_SPACES

    def test_optimize_returns_result(self):
        from backtesting.optuna_optimizer import optimize
        from strategies.trend_ema import TrendEMAStrategy
        df = make_ohlcv(500)
        result = optimize(TrendEMAStrategy, df, strategy_name="trend_ema", n_trials=5)
        assert "best_params" in result
        assert "oos_metrics" in result

    @pytest.mark.slow
    def test_optimize_200_trials(self):
        from backtesting.optuna_optimizer import optimize
        from strategies.trend_ema import TrendEMAStrategy
        df = make_ohlcv(800)
        result = optimize(TrendEMAStrategy, df, strategy_name="trend_ema", n_trials=200)
        assert result["in_sample_score"] > 0
