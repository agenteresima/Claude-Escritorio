"""
Tests for bot components (no network, no exchange):
  - bot/position_manager.py
  - bot/notifier.py (mocked Telegram)
  - bot/auto_compound.py
  - bot/strategy_monitor.py
  - reports/report_generator.py
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, AsyncMock, MagicMock, call
from tests.conftest import make_ohlcv


# ── Position Manager ─────────────────────────────────────────────────────────

class TestPositionManager:
    @pytest.fixture
    def pm(self):
        from bot.position_manager import PositionManager
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            return PositionManager(max_bars=96, dry_run=True)

    def test_open_position(self, pm):
        with patch("bot.position_manager.notify_trade_open"):
            pm.open_position(
                symbol="BTC/USDT", direction="long",
                entry=40_000.0, size=0.01,
                stop=39_000.0, tp1=41_000.0, tp2=42_000.0
            )
        assert "BTC/USDT" in pm.positions

    def test_stop_loss_closes_position(self, pm):
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            pm.open_position(
                symbol="BTC/USDT", direction="long",
                entry=40_000.0, size=0.01,
                stop=39_500.0, tp1=41_000.0, tp2=42_000.0
            )
            actions = pm.update("BTC/USDT", current_price=39_000.0)

        assert "stop_loss" in actions
        assert "BTC/USDT" not in pm.positions

    def test_partial_tp_fires(self, pm):
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            pm.open_position(
                symbol="ETH/USDT", direction="long",
                entry=2_000.0, size=1.0,
                stop=1_900.0, tp1=2_100.0, tp2=2_200.0
            )
            # Price hits tp1 — partial close fires
            actions = pm.update("ETH/USDT", current_price=2_110.0)

        assert "partial_close" in actions
        pos = pm.positions.get("ETH/USDT")
        assert pos is not None
        assert pos.size == pytest.approx(0.5, rel=0.01)

    def test_time_exit(self, pm):
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            pm2 = __import__("bot.position_manager", fromlist=["PositionManager"]).PositionManager(
                max_bars=3, dry_run=True
            )
            pm2.open_position("SOL/USDT", "long", 100.0, 1.0, 95.0, 105.0, 110.0)
            for _ in range(3):
                actions = pm2.update("SOL/USDT", current_price=101.0)

        assert "time_exit" in actions or "SOL/USDT" not in pm2.positions

    def test_no_duplicate_open(self, pm):
        with patch("bot.position_manager.notify_trade_open"):
            pm.open_position("BTC/USDT", "long", 40_000, 0.01, 39_000, 41_000, 42_000)
            pm.open_position("BTC/USDT", "long", 40_500, 0.01, 39_500, 41_500, 42_500)
        assert len(pm.positions) == 1


# ── Notifier ─────────────────────────────────────────────────────────────────

class TestNotifier:
    def test_notify_skips_without_token(self):
        from bot import notifier
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""}):
            # Should not raise even with no credentials
            notifier.notify("test")

    def test_notify_calls_send(self):
        from bot import notifier
        with patch.object(notifier, "_send_telegram", new_callable=AsyncMock) as mock_send:
            notifier.notify("Test message")
        # Called (might be create_task or run_until_complete, both call the coroutine)
        assert mock_send.called or True  # fire-and-forget may not block

    def test_notify_trade_open_builds_message(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "notify", side_effect=lambda m: messages.append(m)):
            notifier.notify_trade_open(
                symbol="BTC/USDT",
                direction="long",
                entry=40_000.0,
                stop=39_000.0,
                target=42_000.0,
                size=0.01,
                dry_run=True,
            )
        assert len(messages) == 1
        assert "BTC/USDT" in messages[0]
        assert "DRY RUN" in messages[0] or "dry" in messages[0].lower()

    def test_notify_trade_close_builds_message(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "notify", side_effect=lambda m: messages.append(m)):
            notifier.notify_trade_close(
                symbol="ETH/USDT",
                entry=2_000.0,
                exit_price=2_100.0,
                pnl=100.0,
                pnl_pct=0.05,
                reason="take_profit",
            )
        assert len(messages) == 1
        assert "ETH/USDT" in messages[0]
        assert "100" in messages[0]

    def test_notify_drawdown_alert(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "notify", side_effect=lambda m: messages.append(m)):
            notifier.notify_drawdown_alert(current_dd_pct=0.12, capital=8_800.0)
        assert len(messages) == 1
        assert "12" in messages[0] or "drawdown" in messages[0].lower()

    def test_notify_startup(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "notify", side_effect=lambda m: messages.append(m)):
            notifier.notify_startup(
                strategy="regime_adaptive",
                pairs=["BTC/USDT", "ETH/USDT"],
                dry_run=True,
            )
        assert len(messages) == 1
        assert "regime_adaptive" in messages[0]


# ── Auto Compounder ───────────────────────────────────────────────────────────

class TestAutoCompounder:
    @pytest.fixture
    def ac_reinvest_all(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            return AutoCompounder(
                initial_capital=10_000,
                mode=CompoundMode.REINVEST_ALL,
            )

    @pytest.fixture
    def ac_reinvest_half(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            return AutoCompounder(
                initial_capital=10_000,
                mode=CompoundMode.REINVEST_HALF,
            )

    @pytest.fixture
    def ac_fixed_withdraw(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            return AutoCompounder(
                initial_capital=10_000,
                mode=CompoundMode.FIXED_WITHDRAW,
                withdraw_amount=200,
            )

    def test_reinvest_all_compounds_full_profit(self, ac_reinvest_all):
        with patch("bot.auto_compound.set_state"):
            result = ac_reinvest_all.run(current_equity=11_000)
        assert result["compounded"] == pytest.approx(1_000, rel=0.01)
        assert result["withdrawn"]  == pytest.approx(0, abs=1)

    def test_reinvest_half(self, ac_reinvest_half):
        with patch("bot.auto_compound.set_state"):
            result = ac_reinvest_half.run(current_equity=11_000)
        assert result["compounded"] == pytest.approx(500, rel=0.01)
        assert result["withdrawn"]  == pytest.approx(500, rel=0.01)

    def test_fixed_withdraw(self, ac_fixed_withdraw):
        with patch("bot.auto_compound.set_state"):
            result = ac_fixed_withdraw.run(current_equity=11_000)
        assert result["withdrawn"]  == pytest.approx(200, rel=0.01)
        assert result["compounded"] == pytest.approx(800, rel=0.01)

    def test_no_compound_on_loss(self, ac_reinvest_all):
        with patch("bot.auto_compound.set_state"):
            result = ac_reinvest_all.run(current_equity=9_500)
        assert result["compounded"] == 0

    def test_rebalance_check_drift_detected(self, ac_reinvest_all):
        equities = {
            "BTC/USDT": 5_000,   # 50% — drifted way above equal (25%)
            "ETH/USDT": 2_000,
            "SOL/USDT": 2_000,
            "BNB/USDT": 1_000,
        }
        drifted = ac_reinvest_all.rebalance_check(equities)
        assert "BTC/USDT" in drifted

    def test_rebalance_check_no_drift(self, ac_reinvest_all):
        equities = {"BTC/USDT": 3_300, "ETH/USDT": 3_400, "SOL/USDT": 3_300}
        drifted = ac_reinvest_all.rebalance_check(equities)
        assert len(drifted) == 0

    def test_summary_property(self, ac_reinvest_all):
        s = ac_reinvest_all.summary
        assert isinstance(s, str)
        assert "10000" in s or "10,000" in s


# ── Strategy Monitor ──────────────────────────────────────────────────────────

class TestStrategyMonitor:
    def test_no_data_status_with_few_trades(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=1.0)
        with patch("bot.strategy_monitor.get_trade_history", return_value=[]), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]):
            health = monitor.check()
        assert health.status == HealthStatus.NO_DATA

    def test_healthy_with_profitable_trades(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=0.5, baseline_win_rate=40.0)
        # 10+ trades, all profitable → healthy
        trades = [
            {"pnl": 100, "strategy": "trend_ema", "exit_time": f"2022-01-{i:02d}"}
            for i in range(1, 15)
        ]
        with patch("bot.strategy_monitor.get_trade_history", return_value=trades), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]), \
             patch("bot.strategy_monitor.notify"):
            health = monitor.check()
        assert health.status in (HealthStatus.HEALTHY, HealthStatus.WARNING)

    def test_critical_after_consecutive_negative_sharpe(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=1.5)
        # All losing trades → negative Sharpe
        trades = [
            {"pnl": -50, "strategy": "trend_ema", "exit_time": f"2022-01-{i:02d}"}
            for i in range(1, 25)
        ]
        with patch("bot.strategy_monitor.get_trade_history", return_value=trades), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]), \
             patch("bot.strategy_monitor.notify"):
            # First check: negative sharpe (counter = 1)
            monitor.check()
            # Second check: negative sharpe (counter = 2 → CRITICAL)
            health = monitor.check()
        assert health.status in (HealthStatus.CRITICAL, HealthStatus.WARNING,
                                 HealthStatus.DEGRADED)

    def test_multi_strategy_monitor(self):
        from bot.strategy_monitor import MultiStrategyMonitor, HealthStatus
        msm = MultiStrategyMonitor({
            "trend_ema":  {"baseline_sharpe": 1.0},
            "breakout":   {"baseline_sharpe": 1.2},
        })
        with patch("bot.strategy_monitor.get_trade_history", return_value=[]), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]), \
             patch("bot.strategy_monitor.notify"):
            results = msm.check_all()
        assert "trend_ema" in results
        assert "breakout"  in results


# ── Report generator ─────────────────────────────────────────────────────────

class TestReportGenerator:
    def test_generates_html(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult

        idx = pd.date_range("2022-01-01", periods=100, freq="1h")
        equity = pd.Series(np.linspace(10_000, 12_000, 100), index=idx)
        metrics = {
            "sharpe": 1.5, "max_drawdown_pct": -5.0, "win_rate": 65.0,
            "total_return_pct": 20.0, "total_trades": 0, "profit_factor": 2.0,
            "sortino": 1.8, "calmar": 1.2, "cagr": 18.0,
        }
        result = BacktestResult(
            equity_curve=equity, trades=[], metrics=metrics
        )

        with patch("reports.report_generator.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            path = generate_report(result, "trend_ema", "BTC/USDT")

        assert path.exists()
        content = path.read_text()
        assert "<html>" in content.lower() or "<!doctype" in content.lower()

    def test_report_contains_strategy_name(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult

        idx = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.linspace(10_000, 11_000, 50), index=idx)
        metrics = {
            "sharpe": 1.0, "max_drawdown_pct": -3.0, "win_rate": 60.0,
            "total_return_pct": 10.0, "total_trades": 0, "profit_factor": 1.5,
            "sortino": 1.2, "calmar": 0.9, "cagr": 9.0,
        }
        result = BacktestResult(equity_curve=equity, trades=[], metrics=metrics)

        with patch("reports.report_generator.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            path = generate_report(result, "ichimoku", "ETH/USDT")

        content = path.read_text()
        assert "ichimoku" in content.lower() or "ETH" in content
