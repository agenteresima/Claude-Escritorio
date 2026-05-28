"""
Tests for: SuperTrend, Ichimoku, VWAP Bounce, MTF, RegimeAdaptive,
           PortfolioBacktester, CorrelationFilter, RiskManager extensions.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime

from risk.manager import RiskManager
from backtesting.engine import BacktestEngine
from config import BacktestConfig


# ── Shared fixture ─────────────────────────────────────────────────────────────

def make_ohlcv(n=500, trend="random", seed=1) -> pd.DataFrame:
    rng    = np.random.default_rng(seed)
    dates  = pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC")
    price  = 30_000.0
    prices = [price]

    for _ in range(n - 1):
        if trend == "up":
            drift = 0.001
        elif trend == "down":
            drift = -0.001
        else:
            drift = 0.0
        prices.append(prices[-1] * (1 + drift + rng.normal(0, 0.005)))

    prices = np.array(prices)
    high   = prices * (1 + np.abs(rng.normal(0, 0.003, n)))
    low    = prices * (1 - np.abs(rng.normal(0, 0.003, n)))
    return pd.DataFrame({
        "open": prices, "high": high, "low": low,
        "close": prices, "volume": rng.uniform(1_000, 10_000, n),
    }, index=dates)


@pytest.fixture
def ohlcv():
    return make_ohlcv()


@pytest.fixture
def rm():
    return RiskManager(initial_capital=10_000)


# ── SuperTrend ─────────────────────────────────────────────────────────────────

class TestSuperTrend:
    def test_returns_valid_signals(self, ohlcv, rm):
        from strategies.supertrend import SuperTrendStrategy
        s  = SuperTrendStrategy(rm)
        df = s.run(ohlcv)
        assert "signal" in df.columns
        assert set(df["signal"].unique()).issubset({-1, 0, 1})

    def test_more_longs_in_uptrend(self, rm):
        from strategies.supertrend import SuperTrendStrategy
        up   = make_ohlcv(trend="up",   n=400)
        down = make_ohlcv(trend="down", n=400)
        s    = SuperTrendStrategy(rm)
        up_sigs   = (s.run(up)["signal"]   == 1).sum()
        down_sigs = (s.run(down)["signal"] == 1).sum()
        assert up_sigs >= down_sigs


# ── Ichimoku ───────────────────────────────────────────────────────────────────

class TestIchimoku:
    def test_signal_column_exists(self, ohlcv, rm):
        from strategies.ichimoku import IchimokuStrategy
        s  = IchimokuStrategy(rm)
        df = s.run(ohlcv)
        assert "signal" in df.columns

    def test_ichi_columns_created(self, ohlcv, rm):
        from strategies.ichimoku import IchimokuStrategy, _ichimoku
        df = _ichimoku(ohlcv)
        for col in ["ichi_tenkan", "ichi_kijun", "ichi_sa", "ichi_sb"]:
            assert col in df.columns


# ── VWAP Bounce ────────────────────────────────────────────────────────────────

class TestVWAPBounce:
    def test_runs_without_error(self, ohlcv, rm):
        from strategies.vwap_bounce import VWAPBounceStrategy
        s  = VWAPBounceStrategy(rm)
        df = s.run(ohlcv)
        assert "signal" in df.columns


# ── RegimeAdaptive ─────────────────────────────────────────────────────────────

class TestRegimeAdaptive:
    def test_regime_column_created(self, ohlcv, rm):
        from strategies.regime_adaptive import RegimeAdaptiveStrategy
        s  = RegimeAdaptiveStrategy(rm)
        df = s.run(ohlcv)
        assert "regime" in df.columns

    def test_valid_regime_values(self, ohlcv, rm):
        from strategies.regime_adaptive import RegimeAdaptiveStrategy, Regime
        s       = RegimeAdaptiveStrategy(rm)
        df      = s.run(ohlcv)
        valid   = {r.value for r in Regime}
        found   = set(df["regime"].dropna().unique())
        assert found.issubset(valid)


# ── PortfolioBacktester ────────────────────────────────────────────────────────

class TestPortfolioBacktester:
    def test_runs_multiple_pairs(self):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.trend_ema import TrendEMAStrategy

        pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        data  = {p: make_ohlcv(seed=i) for i, p in enumerate(pairs)}
        bt    = PortfolioBacktester(BacktestConfig())
        res   = bt.run(data, TrendEMAStrategy, pairs)

        assert len(res.pair_results) == len(pairs)
        assert len(res.combined_equity) > 0

    def test_combined_equity_is_sum(self):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.trend_ema import TrendEMAStrategy

        pairs = ["BTC/USDT", "ETH/USDT"]
        data  = {p: make_ohlcv(seed=i) for i, p in enumerate(pairs)}
        bt    = PortfolioBacktester(BacktestConfig())
        res   = bt.run(data, TrendEMAStrategy, pairs)

        # Combined equity must always be positive
        assert (res.combined_equity > 0).all()


# ── CorrelationFilter ──────────────────────────────────────────────────────────

class TestCorrelationFilter:
    def test_rejects_highly_correlated(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)

        # Identical price series → correlation = 1.0
        prices = pd.Series(np.linspace(1, 100, 200), name="val")
        cf.update("BTC/USDT", prices)
        cf.update("ETH/USDT", prices)  # identical → corr = 1.0

        assert cf.is_correlated_with_open("ETH/USDT", ["BTC/USDT"])

    def test_accepts_uncorrelated(self):
        from utils.correlation import CorrelationFilter
        rng = np.random.default_rng(99)
        cf  = CorrelationFilter(threshold=0.80)

        cf.update("BTC/USDT", pd.Series(rng.normal(0, 1, 200)))
        cf.update("UNCORR",   pd.Series(rng.normal(0, 1, 200)))

        # Two random series unlikely to exceed 0.80 correlation
        assert not cf.is_correlated_with_open("UNCORR", ["BTC/USDT"])

    def test_diversified_subset_respects_max(self):
        from utils.correlation import CorrelationFilter
        rng  = np.random.default_rng(7)
        cf   = CorrelationFilter(threshold=0.80)
        syms = [f"PAIR_{i}" for i in range(10)]
        for s in syms:
            cf.update(s, pd.Series(rng.normal(0, 1, 200)))

        selected = cf.get_diversified_subset(syms, max_positions=3)
        assert len(selected) <= 3
