"""
CLI tests for main.py using click.testing.CliRunner.
Covers all 20 commands to push main.py coverage from 0% toward 90%+.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock
from click.testing import CliRunner
from tests.conftest import make_ohlcv


# ── helper ────────────────────────────────────────────────────────────────────

def _runner():
    return CliRunner()


def _cli():
    from main import cli
    return cli


def _fake_df(n=300):
    return make_ohlcv(n=n, trend="up", seed=42)


# ── backtest ──────────────────────────────────────────────────────────────────

class TestBacktestCommand:
    def test_backtest_ccxt_source(self, tmp_path):
        df = _fake_df()
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("reports.report_generator.generate_report", return_value=tmp_path / "r.html"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), [
                "backtest", "--strategy", "trend_ema", "--pair", "BTC/USDT",
                "--capital", "10000",
            ])
        assert result.exit_code == 0, result.output

    def test_backtest_yfinance_source(self, tmp_path):
        df = _fake_df()
        with patch("data.fetcher.fetch_ohlcv_yfinance", return_value=df), \
             patch("reports.report_generator.generate_report", return_value=tmp_path / "r.html"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), [
                "backtest", "--strategy", "trend_ema", "--pair", "BTC/USDT",
                "--source", "yfinance",
            ])
        assert result.exit_code == 0, result.output


# ── compare ───────────────────────────────────────────────────────────────────

class TestCompareCommand:
    def test_compare_runs(self, tmp_path):
        df = _fake_df()
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("backtesting.compare._save_html_report"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["compare", "--pair", "BTC/USDT"])
        assert result.exit_code == 0

    def test_compare_yfinance(self, tmp_path):
        df = _fake_df()
        with patch("data.fetcher.fetch_ohlcv_yfinance", return_value=df), \
             patch("backtesting.compare._save_html_report"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), [
                "compare", "--pair", "BTC/USDT", "--source", "yfinance"
            ])
        assert result.exit_code == 0


# ── optimize ──────────────────────────────────────────────────────────────────

class TestOptimizeCommand:
    def test_optimize_trend_ema(self, tmp_path):
        df = _fake_df(n=500)
        mock_print = MagicMock()
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("backtesting.optimizer.print_top_results", mock_print), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), [
                "optimize", "--strategy", "trend_ema", "--pair", "BTC/USDT", "--windows", "2"
            ])
        assert result.exit_code == 0


# ── train ─────────────────────────────────────────────────────────────────────

class TestTrainCommand:
    def test_train_runs(self, tmp_path):
        df = _fake_df(n=500)
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("strategies.hybrid_ml.HybridMLStrategy.train",
                   return_value={"accuracy": 0.65}), \
             patch("config.CONFIG.models_dir", tmp_path), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["train", "--pair", "BTC/USDT"])
        assert result.exit_code == 0


# ── portfolio ─────────────────────────────────────────────────────────────────

class TestPortfolioCommand:
    def test_portfolio_with_explicit_pairs(self, tmp_path):
        df = _fake_df()
        mock_result = MagicMock()
        mock_result.pair_results = {"BTC/USDT": MagicMock()}  # non-empty → covers line 177
        mock_result.summary = MagicMock()
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("backtesting.portfolio_backtest.PortfolioBacktester.run",
                   return_value=mock_result), \
             patch("reports.report_generator.generate_report", return_value=tmp_path / "r.html"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), [
                "portfolio", "BTC/USDT", "--strategy", "trend_ema"
            ])
        assert result.exit_code == 0

    def test_portfolio_fetch_exception_continues(self, tmp_path):
        mock_result = MagicMock()
        mock_result.pair_results = {}
        mock_result.summary = MagicMock()
        with patch("data.fetcher.fetch_ohlcv_ccxt", side_effect=Exception("no data")), \
             patch("backtesting.portfolio_backtest.PortfolioBacktester.run",
                   return_value=mock_result), \
             patch("config.CONFIG.pairs", ["BTC/USDT"]), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["portfolio"])
        assert result.exit_code == 0
        assert "Skip" in result.output


# ── sentiment ─────────────────────────────────────────────────────────────────

class TestSentimentCommand:
    def test_sentiment_with_data(self):
        from datetime import datetime
        mock_fng = {"value": 60, "classification": "Greed", "timestamp": datetime.now()}
        mock_gate = {"allow_long": True, "allow_short": True, "reason": "ok"}
        with patch("utils.sentiment.get_current_fng", return_value=mock_fng), \
             patch("utils.sentiment.get_funding_rate", return_value=0.0001), \
             patch("utils.sentiment.sentiment_gate", return_value=mock_gate):
            result = _runner().invoke(_cli(), ["sentiment"])
        assert result.exit_code == 0
        assert "Fear & Greed" in result.output

    def test_sentiment_unavailable(self):
        mock_gate = {"allow_long": True, "allow_short": False, "reason": "fear"}
        with patch("utils.sentiment.get_current_fng", return_value=None), \
             patch("utils.sentiment.get_funding_rate", return_value=None), \
             patch("utils.sentiment.sentiment_gate", return_value=mock_gate):
            result = _runner().invoke(_cli(), ["sentiment"])
        assert result.exit_code == 0
        assert "unavailable" in result.output


# ── montecarlo ────────────────────────────────────────────────────────────────

class TestMonteCarloCLI:
    def test_montecarlo_runs(self, tmp_path):
        df = _fake_df(n=500)
        mock_mc = MagicMock()
        mock_mc.summary = MagicMock()
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("backtesting.monte_carlo.run_monte_carlo", return_value=mock_mc):
            result = _runner().invoke(_cli(), [
                "montecarlo", "--strategy", "trend_ema", "--pair", "BTC/USDT", "--sims", "10"
            ])
        assert result.exit_code == 0


# ── feature_importance ────────────────────────────────────────────────────────

class TestFeatureImportanceCLI:
    def test_feature_importance_no_model(self):
        with patch("utils.feature_importance.plot_feature_importance", return_value={}):
            result = _runner().invoke(_cli(), ["feature-importance"])
        assert result.exit_code == 0
        assert "No trained model" in result.output

    def test_feature_importance_with_results(self, tmp_path):
        imp = {"rsi_14": 0.5, "ema_9": 0.3, "adx": 0.2}
        with patch("utils.feature_importance.plot_feature_importance", return_value=imp), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["feature-importance"])
        assert result.exit_code == 0
        assert "rsi_14" in result.output


# ── events ────────────────────────────────────────────────────────────────────

class TestEventsCLI:
    def test_events_safe_no_upcoming(self):
        from utils.events_filter import EventsFilter
        with patch.object(EventsFilter, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(EventsFilter, "upcoming_events", return_value=[]):
            result = _runner().invoke(_cli(), ["events"])
        assert result.exit_code == 0
        assert "SAFE" in result.output

    def test_events_blocked_with_upcoming(self):
        from datetime import datetime, timezone
        from utils.events_filter import EventsFilter
        upcoming = [{"datetime": datetime.now(timezone.utc), "title": "CPI"}]
        with patch.object(EventsFilter, "is_safe_to_trade", return_value=(False, "CPI")), \
             patch.object(EventsFilter, "upcoming_events", return_value=upcoming):
            result = _runner().invoke(_cli(), ["events"])
        assert result.exit_code == 0
        assert "BLOCKED" in result.output


# ── api ───────────────────────────────────────────────────────────────────────

class TestApiCLI:
    def test_api_starts_uvicorn(self):
        mock_uv = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uv}):
            result = _runner().invoke(_cli(), ["api"])
        assert result.exit_code == 0
        mock_uv.run.assert_called_once()


# ── stats ─────────────────────────────────────────────────────────────────────

class TestStatsCLI:
    def test_stats_no_trades(self):
        with patch("data.database.trade_stats", return_value=None), \
             patch("data.database.get_open_trades", return_value=[]):
            result = _runner().invoke(_cli(), ["stats"])
        assert result.exit_code == 0
        assert "No closed trades" in result.output

    def test_stats_with_trades(self):
        s = {
            "total_trades": 10, "win_rate": 60.0, "total_pnl": 500.0,
            "avg_pnl": 50.0, "best_trade": 200.0, "worst_trade": -100.0,
        }
        open_pos = [{"symbol": "BTC/USDT", "direction": "long", "entry_price": 40000.0}]
        with patch("data.database.trade_stats", return_value=s), \
             patch("data.database.get_open_trades", return_value=open_pos):
            result = _runner().invoke(_cli(), ["stats"])
        assert result.exit_code == 0


# ── bayesian_optimize ─────────────────────────────────────────────────────────

class TestBayesianOptimizeCLI:
    def test_bayesian_no_strategy_lists_available(self):
        result = _runner().invoke(_cli(), ["bayesian-optimize"])
        assert result.exit_code == 0
        assert "Available" in result.output

    def test_bayesian_unsupported_strategy_lists_and_returns(self):
        result = _runner().invoke(_cli(), ["bayesian-optimize", "--strategy", "unknown_xyz"])
        assert result.exit_code == 0
        assert "not supported" in result.output

    def test_bayesian_runs_trend_ema(self, tmp_path):
        df = _fake_df(n=400)
        mock_result = {
            "best_params": {"fast": 9, "slow": 21, "adx_threshold": 25},
            "in_sample_score": 1.5,
            "oos_metrics": {"sharpe": 1.2, "total_return_pct": 15.0, "max_drawdown_pct": -10.0},
        }
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("backtesting.optuna_optimizer.optimize", return_value=mock_result):
            result = _runner().invoke(_cli(), [
                "bayesian-optimize", "--strategy", "trend_ema", "--trials", "1"
            ])
        assert result.exit_code == 0
        assert "Best params" in result.output


# ── live ──────────────────────────────────────────────────────────────────────

class TestLiveCLI:
    def test_live_dry_run_sync(self):
        mock_trader = MagicMock()
        with patch("bot.live_trader.LiveTrader", return_value=mock_trader), \
             patch("config.CONFIG") as mock_cfg:
            mock_cfg.dry_run = True
            result = _runner().invoke(_cli(), ["live", "--dry-run"])
        assert result.exit_code == 0

    def test_live_async_with_confirm(self):
        """--async-live prompts for confirmation then runs run_all_services (lines 336, 349-351)."""
        import asyncio

        async def _noop(cfg):
            pass

        with patch("bot.async_trader.run_all_services", side_effect=_noop), \
             patch("config.CONFIG") as mock_cfg:
            mock_cfg.dry_run = False
            result = _runner().invoke(
                _cli(), ["live", "--async-live"],
                input="y\n",   # answer the click.confirm prompt
            )
        # exit code 0 means user confirmed and asyncio.run completed
        assert result.exit_code == 0


# ── dashboard ─────────────────────────────────────────────────────────────────

class TestDashboardCLI:
    def test_dashboard_command(self):
        mock_app = MagicMock()
        with patch("reports.dashboard.app", mock_app):
            result = _runner().invoke(_cli(), ["dashboard"])
        assert result.exit_code == 0
        mock_app.run.assert_called_once()


# ── benchmark ─────────────────────────────────────────────────────────────────

class TestBenchmarkCLI:
    def test_benchmark_runs(self, tmp_path):
        df = _fake_df()
        mock_cmp = pd.DataFrame({"benchmark": ["bot"], "total_return_%": [10.0]})
        with patch("data.fetcher.fetch_ohlcv_ccxt", return_value=df), \
             patch("reports.benchmark.run_benchmark", return_value=mock_cmp), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["benchmark", "--pair", "BTC/USDT"])
        assert result.exit_code == 0

    def test_benchmark_unknown_strategy(self, tmp_path):
        with patch("config.CONFIG.active_strategy", "unknown_strat"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["benchmark", "--strategy", "unknown_strat"])
        assert result.exit_code == 0
        assert "Unknown strategy" in result.output


# ── backup ────────────────────────────────────────────────────────────────────

class TestBackupCLI:
    def test_backup_with_existing_db(self, tmp_path):
        backup_path = tmp_path / "bot.db.bak"
        backup_path.touch()
        with patch("data.backup.backup", return_value=backup_path):
            result = _runner().invoke(_cli(), ["backup"])
        assert result.exit_code == 0
        assert "Backup created" in result.output

    def test_backup_no_db(self):
        with patch("data.backup.backup", return_value=None):
            result = _runner().invoke(_cli(), ["backup"])
        assert result.exit_code == 0
        assert "No database" in result.output


# ── restore ───────────────────────────────────────────────────────────────────

class TestRestoreCLI:
    def test_restore_list_no_backups(self):
        with patch("data.backup.list_backups", return_value=[]):
            result = _runner().invoke(_cli(), ["restore", "--list-backups"])
        assert result.exit_code == 0
        assert "No backups" in result.output

    def test_restore_list_with_backups(self):
        backups = [{"file": "bot_20240101.db", "size_kb": 100.0, "modified": "2024-01-01"}]
        with patch("data.backup.list_backups", return_value=backups):
            result = _runner().invoke(_cli(), ["restore", "--list-backups"])
        assert result.exit_code == 0
        assert "bot_20240101.db" in result.output

    def test_restore_from_file(self, tmp_path):
        f = tmp_path / "backup.db"
        f.touch()
        with patch("data.backup.restore") as mock_restore:
            result = _runner().invoke(_cli(), ["restore", f"--from-file={f}"])
        assert result.exit_code == 0
        mock_restore.assert_called_once()

    def test_restore_no_args(self):
        result = _runner().invoke(_cli(), ["restore"])
        assert result.exit_code == 0
        assert "Use --list-backups" in result.output


# ── export ────────────────────────────────────────────────────────────────────

class TestExportCLI:
    def test_export_excel(self, tmp_path):
        out = tmp_path / "trades.xlsx"
        with patch("data.backup.export_trades_excel", return_value=out):
            result = _runner().invoke(_cli(), ["export", "--format", "excel"])
        assert result.exit_code == 0
        assert "trades.xlsx" in result.output

    def test_export_csv(self, tmp_path):
        out = tmp_path / "trades.csv"
        with patch("data.backup.export_trades_csv", return_value=out):
            result = _runner().invoke(_cli(), ["export", "--format", "csv"])
        assert result.exit_code == 0


# ── weekly-report ─────────────────────────────────────────────────────────────

class TestWeeklyReportCLI:
    def test_weekly_report_generates(self, tmp_path, monkeypatch):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "wr.db")
        db_mod.init_db()
        with patch("bot.notifier.notify"), \
             patch("config.CONFIG.active_strategy", "trend_ema"), \
             patch("config.CONFIG.reports_dir", tmp_path):
            result = _runner().invoke(_cli(), ["weekly-report"])
        assert result.exit_code == 0


# ── scheduler ─────────────────────────────────────────────────────────────────

class TestSchedulerCLI:
    def test_scheduler_starts_and_stops(self):
        import reports.weekly_report as wr

        mock_time = MagicMock()
        mock_time.sleep.side_effect = StopIteration
        mock_sched = MagicMock()

        with patch.object(wr, "schedule", mock_sched), \
             patch.object(wr, "time", mock_time):
            result = CliRunner().invoke(_cli(), ["scheduler"], catch_exceptions=True)

        # CliRunner caught the StopIteration; verify one loop iteration ran
        assert isinstance(result.exception, StopIteration)
        mock_sched.run_pending.assert_called_once()
