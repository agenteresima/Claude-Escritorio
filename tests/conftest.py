"""
Shared pytest fixtures and helpers.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path


def make_ohlcv(n: int = 500, trend: str = "random", seed: int = 42,
               start: str = "2022-01-01") -> pd.DataFrame:
    rng    = np.random.default_rng(seed)
    dates  = pd.date_range(start, periods=n, freq="1h", tz="UTC")
    price  = 30_000.0
    prices = [price]
    for _ in range(n - 1):
        drift = {"up": 0.0008, "down": -0.0008}.get(trend, 0.0)
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
def ohlcv_uptrend():
    return make_ohlcv(trend="up")


@pytest.fixture
def ohlcv_downtrend():
    return make_ohlcv(trend="down")


@pytest.fixture
def risk_manager():
    from risk.manager import RiskManager
    return RiskManager(initial_capital=10_000)


@pytest.fixture
def backtest_config():
    from config import BacktestConfig
    return BacktestConfig(initial_capital=10_000)


@pytest.fixture(scope="session")
def tmp_reports(tmp_path_factory):
    return tmp_path_factory.mktemp("reports")
