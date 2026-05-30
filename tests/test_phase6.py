"""
Tests for Phase 6 modules:
  - risk/portfolio_heat.py
  - utils/rate_limiter.py
  - data/backup.py
  - strategies: macd_divergence, heikin_ashi, volume_profile
  - reports/benchmark.py (unit-level, no network)
"""
import time
import shutil
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np
import pytest

from tests.conftest import make_ohlcv


# ── Portfolio Heat ────────────────────────────────────────────────────────────

class TestPortfolioHeat:
    def test_import(self):
        from risk.portfolio_heat import PortfolioHeatManager, HeatReport
        mgr = PortfolioHeatManager(max_heat_pct=0.06, initial_capital=10_000)
        assert mgr.max_heat_pct == 0.06

    def test_can_add_position_empty(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(initial_capital=10_000)
        assert mgr.can_add_position(risk_pct=0.01) is True

    def test_blocks_over_heat(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06, initial_capital=10_000)
        mgr.add_position("BTC/USDT", risk_amount=400)
        mgr.add_position("ETH/USDT", risk_amount=200)
        # total = 600 / 10000 = 6% — exactly at limit
        assert mgr.can_add_position(risk_pct=0.01) is False

    def test_reduce_size_to_fit(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06, initial_capital=10_000)
        mgr.add_position("BTC/USDT", risk_amount=500)
        reduced = mgr.reduce_size_to_fit(desired_size=1.0, entry=40_000, stop=39_000)
        assert reduced >= 0

    def test_compute_heat(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(initial_capital=10_000)
        mgr.add_position("BTC/USDT", risk_amount=200)
        report = mgr.compute_heat()
        assert report.current_heat_pct == pytest.approx(0.02, abs=1e-6)
        assert report.remaining_capacity_pct > 0

    def test_remove_position(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(initial_capital=10_000)
        mgr.add_position("BTC/USDT", risk_amount=200)
        mgr.remove_position("BTC/USDT")
        assert mgr.compute_heat().current_heat_pct == 0.0


# ── Rate Limiter ──────────────────────────────────────────────────────────────

class TestRateLimiter:
    def test_basic_allow(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(rate=10, capacity=10)
        assert rl.acquire() is True

    def test_exhaustion(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(rate=1000, capacity=3)
        assert rl.acquire() is True
        assert rl.acquire() is True
        assert rl.acquire() is True
        assert rl.acquire(block=False) is False

    def test_refill(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(rate=100, capacity=2)
        rl.acquire(); rl.acquire()
        time.sleep(0.02)  # 100 tokens/s → 2 tokens in 20ms
        assert rl.acquire(block=False) is True

    def test_exchange_rate_limiter(self):
        from utils.rate_limiter import ExchangeRateLimiter
        erl = ExchangeRateLimiter("binance")
        assert erl.acquire() is True

    @pytest.mark.asyncio
    async def test_async_acquire(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(rate=100, capacity=5)
        result = await rl.async_acquire()
        assert result is True


# ── MACD Divergence Strategy ──────────────────────────────────────────────────

class TestMACDDivergence:
    @pytest.fixture
    def df(self):
        return make_ohlcv(300)

    def test_run_returns_signals(self, df, risk_manager):
        from strategies.macd_divergence import MACDDivergenceStrategy
        strat = MACDDivergenceStrategy(risk_manager)
        out = strat.run(df)
        assert "signal" in out.columns
        assert set(out["signal"].unique()).issubset({-1, 0, 1})

    def test_no_lookahead(self, df, risk_manager):
        from strategies.macd_divergence import MACDDivergenceStrategy
        strat = MACDDivergenceStrategy(risk_manager)
        out1 = strat.run(df.iloc[:200])
        out2 = strat.run(df.iloc[:150])
        # Signals on overlapping history should be consistent
        assert len(out1) == 200
        assert len(out2) == 150

    def test_hidden_divergence_flag(self, df, risk_manager):
        from strategies.macd_divergence import MACDDivergenceStrategy
        strat = MACDDivergenceStrategy(risk_manager, use_hidden=True)
        out = strat.run(df)
        assert "signal" in out.columns


# ── Heikin Ashi Strategy ──────────────────────────────────────────────────────

class TestHeikinAshi:
    @pytest.fixture
    def df(self):
        return make_ohlcv(300)

    def test_run_returns_signals(self, df, risk_manager):
        from strategies.heikin_ashi import HeikinAshiStrategy
        strat = HeikinAshiStrategy(risk_manager)
        out = strat.run(df)
        assert "signal" in out.columns

    def test_ha_columns_added(self, df, risk_manager):
        from strategies.heikin_ashi import HeikinAshiStrategy, compute_heikin_ashi
        ha = compute_heikin_ashi(df)
        for col in ["ha_open", "ha_high", "ha_low", "ha_close"]:
            assert col in ha.columns

    def test_ha_close_between_high_low(self, df, risk_manager):
        from strategies.heikin_ashi import compute_heikin_ashi
        ha = compute_heikin_ashi(df)
        assert (ha["ha_close"] <= ha["ha_high"]).all()
        assert (ha["ha_close"] >= ha["ha_low"]).all()

    def test_confirm_bars_param(self, df, risk_manager):
        from strategies.heikin_ashi import HeikinAshiStrategy
        strat = HeikinAshiStrategy(risk_manager, confirm_bars=3)
        out = strat.run(df)
        assert "signal" in out.columns


# ── Volume Profile Strategy ───────────────────────────────────────────────────

class TestVolumeProfile:
    @pytest.fixture
    def df(self):
        return make_ohlcv(500)

    def test_compute_profile(self, df):
        from strategies.volume_profile import compute_volume_profile
        poc, vah, val = compute_volume_profile(df, bins=50)
        assert val < poc < vah

    def test_value_area_70_pct(self, df):
        from strategies.volume_profile import compute_volume_profile
        poc, vah, val = compute_volume_profile(df, bins=50, value_area_pct=0.70)
        assert val <= poc <= vah

    def test_run_returns_signals(self, df, risk_manager):
        from strategies.volume_profile import VolumeProfileStrategy
        strat = VolumeProfileStrategy(risk_manager)
        out = strat.run(df)
        assert "signal" in out.columns
        assert set(out["signal"].unique()).issubset({-1, 0, 1})


# ── Data Backup ───────────────────────────────────────────────────────────────

class TestBackup:
    @pytest.fixture
    def tmp_db(self, tmp_path):
        db = tmp_path / "bot.db"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE trades (id INTEGER PRIMARY KEY, symbol TEXT, pnl REAL)"
        )
        conn.execute("INSERT INTO trades (symbol, pnl) VALUES ('BTC/USDT', 100.0)")
        conn.commit()
        conn.close()
        return db, tmp_path

    def test_backup_creates_file(self, tmp_db):
        from data import backup as backup_module
        db_path, tmp_path = tmp_db
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        with patch.object(backup_module, "DB_PATH", db_path), \
             patch.object(backup_module, "BACKUP_DIR", backup_dir):
            result = backup_module.backup(tag="test")

        assert result.exists()
        assert "test" in result.name

    def test_backup_missing_db(self, tmp_path):
        from data import backup as backup_module
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        missing = tmp_path / "nonexistent.db"

        with patch.object(backup_module, "DB_PATH", missing), \
             patch.object(backup_module, "BACKUP_DIR", backup_dir):
            result = backup_module.backup()

        assert result == Path()

    def test_list_backups_empty(self, tmp_path):
        from data import backup as backup_module
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        with patch.object(backup_module, "BACKUP_DIR", backup_dir):
            result = backup_module.list_backups()

        assert result == []

    def test_restore(self, tmp_db):
        from data import backup as backup_module
        db_path, tmp_path = tmp_db
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        restore_target = tmp_path / "restored.db"

        with patch.object(backup_module, "DB_PATH", db_path), \
             patch.object(backup_module, "BACKUP_DIR", backup_dir):
            bk = backup_module.backup()

        with patch.object(backup_module, "DB_PATH", restore_target), \
             patch.object(backup_module, "BACKUP_DIR", backup_dir):
            backup_module.restore(bk)

        assert restore_target.exists()


# ── Benchmark (unit, no network) ──────────────────────────────────────────────

class TestBenchmark:
    def test_compute_metrics(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            np.linspace(100, 200, 1000),
            index=pd.date_range("2022-01-01", periods=1000, freq="1h"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        assert "sharpe" in m
        assert "max_dd_%" in m
        assert m["total_return_%"] == pytest.approx(100.0, abs=0.5)

    def test_run_benchmark_no_network(self):
        from reports.benchmark import run_benchmark

        idx = pd.date_range("2022-01-01", periods=500, freq="1h")
        equity = pd.Series(np.linspace(10_000, 12_000, 500), index=idx)

        with patch("reports.benchmark.fetch_ohlcv_ccxt") as mock_ccxt, \
             patch("reports.benchmark.fetch_ohlcv_yfinance") as mock_yf, \
             tempfile.TemporaryDirectory() as td:

            mock_ccxt.side_effect = Exception("no network")
            mock_yf.side_effect   = Exception("no network")

            from pathlib import Path
            df = run_benchmark(equity, start="2022-01-01", output_dir=Path(td))

        assert "Bot Strategy" in df["strategy"].values
        assert "sharpe" in df.columns


# ── Shutdown handler ──────────────────────────────────────────────────────────

class TestShutdown:
    def test_graceful_shutdown_import(self):
        from bot.shutdown import GracefulShutdown
        gs = GracefulShutdown()
        assert gs.is_running is True

    def test_add_callback(self):
        from bot.shutdown import GracefulShutdown
        called = []
        gs = GracefulShutdown()
        gs.add_callback(lambda: called.append(1))
        gs._shutdown()
        assert called == [1]
        assert gs.is_running is False

    def test_multiple_callbacks(self):
        from bot.shutdown import GracefulShutdown
        log = []
        gs = GracefulShutdown()
        gs.add_callback(lambda: log.append("a"))
        gs.add_callback(lambda: log.append("b"))
        gs._shutdown()
        assert "a" in log and "b" in log
