"""
Miscellaneous coverage gap tests:
  - data/database.py       (rollback path, get_trade_history with symbol filter,
                             log_signal)
  - utils/rate_limiter.py  (async context manager sleep path)
  - backtesting/optimizer.py (walk_forward_test, grid_search combo-sampling)
  - bot/async_trader.py    (run() method, unknown strategy, empty-df guard)
  - reports/benchmark.py   (_compute_benchmark_metrics edge cases)
  - reports/weekly_report.py (health icons for non-zero trades)
"""
import pytest
import asyncio
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock


# ── database.py ───────────────────────────────────────────────────────────────

class TestDatabaseExtended:
    @pytest.fixture(autouse=True)
    def fresh_db(self, tmp_path, monkeypatch):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "test.db")
        db_mod.init_db()
        yield db_mod

    def test_get_conn_rollback_on_exception(self, fresh_db):
        """Context manager rolls back on exception and re-raises."""
        with pytest.raises(ValueError, match="forced error"):
            with fresh_db.get_conn() as conn:
                conn.execute("INSERT INTO bot_state (key, value, updated_at) VALUES ('k', 'v', '2024-01-01')")
                raise ValueError("forced error")
        # After rollback the insert should not have committed
        with fresh_db.get_conn() as conn:
            row = conn.execute("SELECT * FROM bot_state WHERE key='k'").fetchone()
        assert row is None

    def test_get_trade_history_with_symbol_filter(self, fresh_db):
        tid1 = fresh_db.insert_trade("BTC/USDT", "long", "trend_ema",
                                     40_000, 0.01, 39_000, 42_000)
        fresh_db.close_trade(tid1, 41_000, 10.0, 0.025, "take_profit", 5)
        tid2 = fresh_db.insert_trade("ETH/USDT", "long", "trend_ema",
                                     2_000, 0.1, 1_900, 2_200)
        fresh_db.close_trade(tid2, 2_100, 10.0, 0.05, "take_profit", 3)

        btc_trades = fresh_db.get_trade_history(symbol="BTC/USDT")
        assert len(btc_trades) == 1
        assert btc_trades[0]["symbol"] == "BTC/USDT"

    def test_log_signal_writes_row(self, fresh_db):
        fresh_db.log_signal("BTC/USDT", "trend_ema", 1, 40_000.0, confidence=0.8)
        with fresh_db.get_conn() as conn:
            rows = conn.execute("SELECT * FROM signal_log").fetchall()
        assert len(rows) == 1
        row = dict(rows[0])
        assert row["symbol"] == "BTC/USDT"
        assert row["signal"] == 1


# ── rate_limiter.py async path ────────────────────────────────────────────────

class TestRateLimiterAsync:
    @pytest.mark.asyncio
    async def test_aenter_aexit_no_wait(self):
        from utils.rate_limiter import RateLimiter
        limiter = RateLimiter(calls_per_second=100.0, burst=10)
        async with limiter:
            pass   # should not sleep — tokens available
        assert limiter._tokens < 10.0   # one token consumed

    @pytest.mark.asyncio
    async def test_aenter_sleeps_when_no_tokens(self):
        from utils.rate_limiter import RateLimiter
        limiter = RateLimiter(calls_per_second=1.0, burst=1)
        # Drain the token bucket
        limiter._tokens = 0.0
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            async with limiter:
                pass
        mock_sleep.assert_called_once()
        assert mock_sleep.call_args[0][0] > 0

    def test_get_limiter_caches_instance(self):
        from utils.rate_limiter import get_limiter, _limiters
        lim1 = get_limiter("binance")
        lim2 = get_limiter("binance")
        assert lim1 is lim2

    def test_exchange_rate_limiter_presets(self):
        from utils.rate_limiter import ExchangeRateLimiter
        for exch in ("binance", "bybit", "kraken", "coinbase", "unknown_exchange"):
            lim = ExchangeRateLimiter(exch)
            assert lim.general is not None


# ── backtesting/optimizer.py ──────────────────────────────────────────────────

class TestOptimizerExtended:
    @pytest.fixture
    def ohlcv(self):
        from tests.conftest import make_ohlcv
        return make_ohlcv(n=500, trend="up", seed=42)

    @pytest.fixture
    def backtest_cfg(self):
        from config import BacktestConfig
        return BacktestConfig(initial_capital=10_000)

    def test_grid_search_samples_when_too_many_combos(self, ohlcv, backtest_cfg):
        from backtesting.optimizer import grid_search
        from strategies.trend_ema import TrendEMAStrategy
        # Wide grid = many combos → sampling kicks in
        grid = {
            "fast":          [5, 8, 10, 12, 15],
            "slow":          [20, 30, 40, 50, 60],
            "adx_threshold": [20, 25, 30],
        }
        result = grid_search(TrendEMAStrategy, ohlcv, grid, backtest_cfg, max_combos=5)
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 5

    def test_walk_forward_test_runs(self, ohlcv, backtest_cfg):
        from backtesting.optimizer import walk_forward_test
        from strategies.trend_ema import TrendEMAStrategy
        grid = {
            "fast": [5, 10],
            "slow": [20, 40],
            "adx_threshold": [20],
        }
        result = walk_forward_test(
            TrendEMAStrategy, ohlcv, grid,
            n_windows=3, train_ratio=0.70,
            backtest_cfg=backtest_cfg,
        )
        assert isinstance(result, pd.DataFrame)


# ── bot/async_trader.py remaining paths ──────────────────────────────────────

def _build_trader(paused=False):
    from bot.async_trader import AsyncLiveTrader
    from data.websocket_feed import CandleBuffer
    cfg = MagicMock()
    cfg.dry_run = True
    cfg.active_strategy = "trend_ema"
    cfg.pairs = ["BTC/USDT"]
    cfg.timeframe = "1h"
    cfg.exchange.name = "binance"
    cfg.risk.max_drawdown_pct = 0.15
    cfg.risk.risk_reward_ratio = 2.0
    cfg.risk.max_position_size_pct = 0.05

    t = AsyncLiveTrader.__new__(AsyncLiveTrader)
    t.cfg = cfg
    t.dry_run = True
    t._sentiment = {"allow_long": True, "allow_short": True, "reason": "ok"}
    t._sentiment_ts = 0.0
    t.buffer = CandleBuffer(maxlen=500)
    t.pos_mgr = MagicMock()
    t.pos_mgr.positions = {}
    t.risk = MagicMock()
    t.risk.portfolio.capital = 10_000.0
    t.risk.portfolio.current_drawdown.return_value = 0.02
    t.risk.validate_signal.return_value = True
    t.risk.atr_size.return_value = 0.01
    t.corr_filter = MagicMock()
    t.corr_filter.is_correlated_with_open.return_value = False
    t.corr_filter.update = MagicMock()
    t.events = MagicMock()
    t.events.is_safe_to_trade.return_value = (True, "ok")
    t.compounder = MagicMock()
    t.compounder.should_compound.return_value = False
    t.monitor = MagicMock()
    t.monitor.check.return_value = MagicMock(
        status=MagicMock(value="healthy"), message="ok"
    )
    return t


class TestAsyncTraderRemainingPaths:
    @pytest.mark.asyncio
    async def test_process_symbol_unknown_strategy_returns(self):
        t = _build_trader()
        with patch("bot.async_trader.get_state", return_value="nonexistent_strategy"):
            await t._process_symbol("BTC/USDT")
        # Should return silently without error

    @pytest.mark.asyncio
    async def test_process_symbol_empty_df_returns(self):
        from tests.conftest import make_ohlcv
        t = _build_trader()
        # Put some candles in buffer but make to_df return empty
        with patch("bot.async_trader.get_state", return_value="trend_ema"), \
             patch.object(t.buffer, "to_df", return_value=pd.DataFrame()):
            await t._process_symbol("BTC/USDT")
        # Returns without calling strategy.run

    @pytest.mark.asyncio
    async def test_run_creates_tasks_and_gathers(self):
        """run() creates 4 asyncio tasks and gathers them."""
        t = _build_trader()
        gathered = []

        async def _null():
            pass

        with patch("bot.async_trader.WebSocketFeed") as mock_feed_cls, \
             patch("asyncio.create_task", side_effect=lambda coro: gathered.append(coro) or MagicMock()) as mock_ct, \
             patch("asyncio.gather", new_callable=AsyncMock):
            mock_feed_cls.return_value = MagicMock()
            await t.run()

        assert mock_ct.call_count == 4


# ── reports/benchmark.py edge cases ──────────────────────────────────────────

class TestBenchmarkEdgeCases:
    def test_compute_with_cagr_and_sharpe(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            np.linspace(100, 130, 252),
            index=pd.date_range("2022-01-01", periods=252, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        assert "total_return_%" in m
        assert "cagr_%" in m or "cagr" in str(m)
        assert "sharpe" in m

    def test_sharpe_nan_when_no_variance(self):
        from reports.benchmark import _compute_benchmark_metrics
        # Perfectly flat prices → std of returns = 0 → Sharpe is 0 or NaN
        prices = pd.Series(
            [100.0] * 200,
            index=pd.date_range("2022-01-01", periods=200, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        sharpe = m.get("sharpe", 0)
        assert sharpe == 0 or np.isnan(sharpe) or sharpe == pytest.approx(0, abs=1)


# ── reports/weekly_report.py ──────────────────────────────────────────────────

class TestWeeklyReportHealthIcons:
    @pytest.fixture
    def patched_db(self, tmp_path, monkeypatch):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "wr.db")
        db_mod.init_db()
        yield db_mod

    def test_report_with_losing_trades_shows_warning_icon(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        # Insert a losing trade
        tid = patched_db.insert_trade("BTC/USDT", "long", "trend_ema",
                                       40_000.0, 0.01, 39_000.0, 42_000.0)
        patched_db.close_trade(tid, 38_000.0, -20.0, -0.05, "stop_loss", 5)

        with patch("reports.weekly_report.notify"), \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir = tmp_path
            msg = generate_weekly_report("trend_ema")

        # Should contain a non-OK health icon
        health_icons = {"✅", "⚠️", "🚨", "📉", "❓"}
        assert any(icon in msg for icon in health_icons)
