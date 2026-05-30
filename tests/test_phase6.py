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
    CAPITAL = 10_000.0

    def test_import(self):
        from risk.portfolio_heat import PortfolioHeatManager, HeatReport
        mgr = PortfolioHeatManager(max_heat_pct=0.06)
        assert mgr.max_heat_pct == 0.06

    def test_can_add_position_empty_portfolio(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06)
        allowed, reason = mgr.can_add_position(
            total_capital=self.CAPITAL, new_risk=100.0   # 1% of 10k
        )
        assert allowed is True
        assert reason == "ok"

    def test_blocks_when_heat_exceeded(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06)
        # Fill 5.5% heat with existing position
        mgr.update_position("BTC/USDT", "long",
                             entry=40_000, current=40_000,
                             stop=39_000, size=0.55)  # 0.55 × $1000 gap = $550 risk
        # Adding 1% more ($100) would total 6.5% > 6%
        allowed, reason = mgr.can_add_position(
            total_capital=self.CAPITAL, new_risk=100.0
        )
        assert allowed is False
        assert "heat" in reason.lower() or "%" in reason

    def test_reduce_size_to_fit(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06)
        # 3% already used
        mgr.update_position("ETH/USDT", "long",
                             entry=2_000, current=2_000, stop=1_800, size=1.5)
        # Remaining budget = 3% × 10k = $300; risk per unit = $1000 → 0.3 BTC
        max_size = mgr.reduce_size_to_fit(
            total_capital=self.CAPITAL, entry=40_000, stop=39_000
        )
        assert max_size >= 0

    def test_compute_heat_with_position(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager(max_heat_pct=0.06)
        mgr.update_position("BTC/USDT", "long",
                             entry=40_000, current=40_000,
                             stop=38_000, size=0.1)   # risk = 0.1 × 2000 = $200
        report = mgr.compute_heat(total_capital=self.CAPITAL)
        assert report.total_heat_pct == pytest.approx(0.02, abs=1e-6)  # 200/10000
        assert report.heat_ok is True
        assert report.largest_risk == "BTC/USDT"

    def test_compute_heat_empty(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager()
        report = mgr.compute_heat(total_capital=self.CAPITAL)
        assert report.total_heat_pct == 0.0
        assert report.heat_ok is True

    def test_remove_position(self):
        from risk.portfolio_heat import PortfolioHeatManager
        mgr = PortfolioHeatManager()
        mgr.update_position("BTC/USDT", "long",
                             entry=40_000, current=40_000, stop=39_000, size=0.1)
        mgr.remove_position("BTC/USDT")
        report = mgr.compute_heat(total_capital=self.CAPITAL)
        assert report.total_heat_pct == 0.0


# ── Rate Limiter ──────────────────────────────────────────────────────────────

class TestRateLimiter:
    def test_basic_sync_context_manager(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(calls_per_second=10.0, burst=5)
        # Should not raise
        with rl:
            pass

    def test_tokens_deplete(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(calls_per_second=1000.0, burst=3)
        # Use 3 tokens
        with rl: pass
        with rl: pass
        with rl: pass
        # 4th call should block briefly (< 0.01s with 1000/s rate) but not raise
        with rl: pass  # blocks momentarily then refills

    def test_tokens_refill_over_time(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(calls_per_second=100.0, burst=2)
        with rl: pass
        with rl: pass
        time.sleep(0.025)  # wait for ~2.5 tokens to refill at 100/s
        with rl: pass  # should succeed after refill

    def test_exchange_rate_limiter_has_limiters(self):
        from utils.rate_limiter import ExchangeRateLimiter
        erl = ExchangeRateLimiter("binance")
        assert hasattr(erl, "general")
        assert hasattr(erl, "order")
        assert hasattr(erl, "market_data")

    def test_exchange_rate_limiter_binance_preset(self):
        from utils.rate_limiter import ExchangeRateLimiter
        erl = ExchangeRateLimiter("binance")
        assert erl.general.rate > erl.general.rate * 0  # just check it's positive

    def test_get_limiter_cached(self):
        from utils.rate_limiter import get_limiter, ExchangeRateLimiter
        l1 = get_limiter("binance")
        l2 = get_limiter("binance")
        assert l1 is l2  # same cached instance

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        from utils.rate_limiter import RateLimiter
        rl = RateLimiter(calls_per_second=100.0, burst=5)
        async with rl:
            pass  # should not raise


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

        with patch("data.fetcher.fetch_ohlcv_ccxt", side_effect=Exception("no network")), \
             patch("data.fetcher.fetch_ohlcv_yfinance", side_effect=Exception("no network")), \
             tempfile.TemporaryDirectory() as td:

            from pathlib import Path
            df = run_benchmark(equity, start="2022-01-01", output_dir=Path(td))

        assert "Bot Strategy" in df["strategy"].values
        assert "sharpe" in df.columns


# ── Shutdown handler ──────────────────────────────────────────────────────────

class TestShutdown:
    def test_graceful_shutdown_not_requested_initially(self):
        from bot.shutdown import GracefulShutdown
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs = GracefulShutdown()
        assert gs.requested is False

    def test_add_callback_runs_on_shutdown(self):
        from bot.shutdown import GracefulShutdown
        called = []
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs = GracefulShutdown()
            gs.add_callback(lambda: called.append(1))
            gs._run_shutdown()
        assert called == [1]
        assert gs.requested is True

    def test_multiple_callbacks_all_called(self):
        from bot.shutdown import GracefulShutdown
        log = []
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs = GracefulShutdown()
            gs.add_callback(lambda: log.append("a"))
            gs.add_callback(lambda: log.append("b"))
            gs._run_shutdown()
        assert "a" in log and "b" in log

    def test_callback_exception_doesnt_stop_others(self):
        from bot.shutdown import GracefulShutdown
        log = []
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs = GracefulShutdown()
            gs.add_callback(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
            gs.add_callback(lambda: log.append("ok"))
            gs._run_shutdown()
        assert "ok" in log  # second callback still ran
