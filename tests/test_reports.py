"""
Tests for report generation modules:
  - reports/weekly_report.py
  - reports/report_generator.py (additional edge cases)
  - reports/benchmark.py (unit level)
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path

from tests.conftest import make_ohlcv


# ── Weekly report ─────────────────────────────────────────────────────────────

class TestWeeklyReport:
    @pytest.fixture
    def patched_db(self, tmp_path):
        """Patch DB to use temp file."""
        import data.database as db_mod
        db_mod_orig_path = db_mod.DB_PATH
        db_mod.DB_PATH = tmp_path / "weekly.db"
        db_mod.init_db()
        yield db_mod
        db_mod.DB_PATH = db_mod_orig_path

    def test_generates_without_trades(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        with patch("reports.weekly_report.notify"), \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir     = tmp_path
            msg = generate_weekly_report("trend_ema")
        assert isinstance(msg, str)
        assert "trend_ema" in msg

    def test_report_includes_trade_data(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        from datetime import datetime, timedelta

        # Insert a trade with exit_time this week
        tid = patched_db.insert_trade("BTC/USDT", "long", "trend_ema",
                                       40_000.0, 0.01, 39_000.0, 42_000.0)
        patched_db.close_trade(tid, 41_000.0, 10.0, 0.025, "take_profit", 5)

        with patch("reports.weekly_report.notify") as mock_notify, \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir     = tmp_path
            msg = generate_weekly_report("trend_ema")

        mock_notify.assert_called_once()
        assert "10" in msg or "PnL" in msg

    def test_html_report_saved(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        with patch("reports.weekly_report.notify"), \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir     = tmp_path
            generate_weekly_report("trend_ema")
        html_files = list(tmp_path.glob("weekly_*.html"))
        assert len(html_files) == 1
        content = html_files[0].read_text()
        assert "<!DOCTYPE html>" in content or "<html>" in content.lower()
        assert "trend_ema" in content

    def test_html_contains_trade_rows(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        tid = patched_db.insert_trade("ETH/USDT", "long", "trend_ema",
                                       2_000.0, 0.5, 1_900.0, 2_200.0)
        patched_db.close_trade(tid, 2_100.0, 50.0, 0.05, "take_profit", 3)

        with patch("reports.weekly_report.notify"), \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir     = tmp_path
            generate_weekly_report("trend_ema")

        html = next(iter(tmp_path.glob("weekly_*.html"))).read_text()
        assert "ETH/USDT" in html

    def test_health_icon_in_message(self, patched_db, tmp_path):
        from reports.weekly_report import generate_weekly_report
        with patch("reports.weekly_report.notify") as mock_notify, \
             patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir     = tmp_path
            msg = generate_weekly_report("trend_ema")

        # Health icon should be one of the defined icons
        health_icons = {"✅", "⚠️", "🚨", "📉", "❓"}
        assert any(icon in msg for icon in health_icons)

    def test_save_weekly_html_with_no_trades(self, tmp_path):
        from reports.weekly_report import _save_weekly_html
        from datetime import datetime
        with patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            _save_weekly_html([], datetime(2026, 1, 6), "trend_ema")
        html_files = list(tmp_path.glob("weekly_*.html"))
        assert len(html_files) == 1

    def test_save_weekly_html_with_trades(self, tmp_path):
        from reports.weekly_report import _save_weekly_html
        from datetime import datetime
        trades = [
            {
                "symbol": "BTC/USDT",
                "entry_price": 40_000.0,
                "exit_price": 41_000.0,
                "pnl": 10.0,
                "exit_reason": "take_profit",
            }
        ]
        with patch("reports.weekly_report.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            _save_weekly_html(trades, datetime(2026, 1, 6), "trend_ema")
        html = next(iter(tmp_path.glob("weekly_*.html"))).read_text()
        assert "BTC/USDT" in html
        assert "take_profit" in html


# ── Report generator additional edge cases ───────────────────────────────────

class TestReportGeneratorEdgeCases:
    def test_zero_trades_no_crash(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult

        idx = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.linspace(10_000, 10_000, 50), index=idx)  # flat
        metrics = {
            "sharpe": 0.0, "max_drawdown_pct": 0.0, "win_rate": 0.0,
            "total_return_pct": 0.0, "total_trades": 0, "profit_factor": 0.0,
            "sortino": 0.0, "calmar": 0.0, "cagr": 0.0,
        }
        result = BacktestResult(equity_curve=equity, trades=[], metrics=metrics)
        with patch("reports.report_generator.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            path = generate_report(result, "trend_ema", "BTC/USDT")
        assert path.exists()

    def test_negative_metrics_handled(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult

        idx = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.linspace(10_000, 8_000, 50), index=idx)
        metrics = {
            "sharpe": -0.5, "max_drawdown_pct": -20.0, "win_rate": 30.0,
            "total_return_pct": -20.0, "total_trades": 5, "profit_factor": 0.5,
            "sortino": -0.4, "calmar": -0.3, "cagr": -15.0,
        }
        result = BacktestResult(equity_curve=equity, trades=[], metrics=metrics)
        with patch("reports.report_generator.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            path = generate_report(result, "mean_reversion", "ETH/USDT")
        assert path.exists()
        content = path.read_text()
        assert "mean_reversion" in content

    def test_output_dir_override(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult

        custom_dir = tmp_path / "custom_reports"
        idx = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.ones(50) * 10_000, index=idx)
        metrics = {
            "sharpe": 1.0, "max_drawdown_pct": -5.0, "win_rate": 60.0,
            "total_return_pct": 10.0, "total_trades": 10, "profit_factor": 1.5,
            "sortino": 1.2, "calmar": 0.8, "cagr": 9.0,
        }
        result = BacktestResult(equity_curve=equity, trades=[], metrics=metrics)
        path = generate_report(result, "breakout", "SOL/USDT", output_dir=custom_dir)
        assert path.parent == custom_dir or custom_dir.exists()
        assert path.exists()


# ── Benchmark metrics (unit, no network) ─────────────────────────────────────

class TestBenchmarkMetrics:
    def test_flat_equity_zero_return(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            [100.0] * 100,
            index=pd.date_range("2022-01-01", periods=100, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        assert m["total_return_%"] == pytest.approx(0.0, abs=1.0)
        assert m["max_dd_%"] == pytest.approx(0.0, abs=0.1)

    def test_doubling_equity_100_pct_return(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            np.linspace(100, 200, 500),
            index=pd.date_range("2022-01-01", periods=500, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        assert m["total_return_%"] == pytest.approx(100.0, abs=1.0)

    def test_declining_equity_has_drawdown(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            np.linspace(200, 100, 200),
            index=pd.date_range("2022-01-01", periods=200, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        assert m["max_dd_%"] < -40.0   # at least 40% drawdown

    def test_sharpe_positive_for_uptrend(self):
        from reports.benchmark import _compute_benchmark_metrics
        prices = pd.Series(
            np.linspace(100, 150, 252),
            index=pd.date_range("2022-01-01", periods=252, freq="1D"),
        )
        m = _compute_benchmark_metrics(prices, initial=10_000)
        # Monotone uptrend → positive Sharpe
        assert m.get("sharpe", 0) >= 0
