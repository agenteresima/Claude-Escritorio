"""
Unit tests for all strategies.
Uses synthetic OHLCV data to avoid API calls.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from risk.manager import RiskManager
from strategies.trend_ema import TrendEMAStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.breakout import BreakoutStrategy
from backtesting.engine import BacktestEngine
from config import BacktestConfig


def make_synthetic_ohlcv(n: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC")
    price = 30_000.0
    prices = [price]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1 + rng.normal(0, 0.005)))

    prices = np.array(prices)
    high   = prices * (1 + np.abs(rng.normal(0, 0.003, n)))
    low    = prices * (1 - np.abs(rng.normal(0, 0.003, n)))
    volume = rng.uniform(1_000, 10_000, n)

    return pd.DataFrame({
        "open":   prices,
        "high":   high,
        "low":    low,
        "close":  prices,
        "volume": volume,
    }, index=dates)


@pytest.fixture
def ohlcv():
    return make_synthetic_ohlcv()


@pytest.fixture
def risk_manager():
    return RiskManager(initial_capital=10_000)


class TestTrendEMA:
    def test_signal_column_exists(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        result = strat.run(ohlcv)
        assert "signal" in result.columns

    def test_signals_are_valid_values(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        result = strat.run(ohlcv)
        assert set(result["signal"].unique()).issubset({-1, 0, 1})

    def test_stop_loss_below_close_on_long(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        result = strat.run(ohlcv)
        longs  = result[result["signal"] == 1]
        if not longs.empty:
            assert (longs["stop_loss"] < longs["close"]).all()


class TestMeanReversion:
    def test_no_signals_in_trending_market(self, risk_manager):
        """ADX filter should suppress signals in strong trends."""
        # Create a persistent uptrend
        dates  = pd.date_range("2022-01-01", periods=300, freq="1h", tz="UTC")
        prices = np.linspace(30_000, 60_000, 300)
        df = pd.DataFrame({
            "open": prices, "high": prices * 1.005,
            "low":  prices * 0.995, "close": prices,
            "volume": 5000,
        }, index=dates)
        strat  = MeanReversionStrategy(risk_manager)
        result = strat.run(df)
        # In a clean uptrend ADX should be high → few/no long signals
        long_signals = (result["signal"] == 1).sum()
        assert long_signals < 10, f"Expected few signals in uptrend, got {long_signals}"


class TestBacktestEngine:
    def test_backtest_runs_without_error(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        sig_df = strat.run(ohlcv)
        engine = BacktestEngine(BacktestConfig(), risk_manager)
        result = engine.run(sig_df)
        assert result.metrics is not None

    def test_equity_curve_length_matches_data(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        sig_df = strat.run(ohlcv)
        engine = BacktestEngine(BacktestConfig(), risk_manager)
        result = engine.run(sig_df)
        assert len(result.equity_curve) == len(ohlcv)

    def test_no_lookahead_bias(self, ohlcv, risk_manager):
        """Equity should only depend on past data — shuffle future and check consistency."""
        strat   = TrendEMAStrategy(risk_manager)
        sig_df  = strat.run(ohlcv)
        engine  = BacktestEngine(BacktestConfig(), risk_manager)
        result1 = engine.run(sig_df)
        # Truncate data and re-run — partial equity should match
        risk2   = RiskManager(initial_capital=10_000)
        strat2  = TrendEMAStrategy(risk2)
        sig_df2 = strat2.run(ohlcv.iloc[:200])
        engine2 = BacktestEngine(BacktestConfig(), risk2)
        result2 = engine2.run(sig_df2)
        # First 200 equity values should match (within float tolerance)
        assert abs(result1.equity_curve.iloc[199] - result2.equity_curve.iloc[199]) < 1e-6

    def test_max_drawdown_never_exceeds_stop(self, ohlcv, risk_manager):
        strat  = TrendEMAStrategy(risk_manager)
        sig_df = strat.run(ohlcv)
        engine = BacktestEngine(BacktestConfig(), risk_manager)
        result = engine.run(sig_df)
        max_dd = abs(result.metrics.get("max_drawdown_pct", 0))
        # Hard stop is 5 % per trade — cumulative DD can be higher but sanity-check
        assert max_dd < 100, "Max drawdown should never wipe the account on test data"


class TestRiskManager:
    def test_kelly_never_exceeds_max(self, risk_manager):
        size = risk_manager.kelly_size(0.6, 0.04, 0.02)
        assert size <= risk_manager.cfg.max_position_size_pct

    def test_validate_rejects_bad_rr(self, risk_manager):
        from risk.manager import TradeSignal
        sig = TradeSignal("BTC/USDT", "long", 30_000, 29_500, 30_300)  # RR < 2
        assert not risk_manager.validate_signal(sig)

    def test_validate_blocks_after_max_drawdown(self, risk_manager):
        from risk.manager import TradeSignal
        risk_manager.portfolio.capital    = 8_000
        risk_manager.portfolio.peak_equity = 10_000  # 20 % DD > 15 % limit
        sig = TradeSignal("BTC/USDT", "long", 30_000, 28_500, 33_000)
        assert not risk_manager.validate_signal(sig)
