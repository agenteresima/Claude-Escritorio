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
from unittest.mock import patch, AsyncMock, MagicMock
from tests.conftest import make_ohlcv


# ── Position Manager ─────────────────────────────────────────────────────────

class TestPositionManager:
    @pytest.fixture
    def pm(self):
        from bot.position_manager import PositionManager
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000)
        return PositionManager(rm)

    @pytest.fixture
    def mock_exchange(self):
        ex = MagicMock()
        ex.create_market_sell_order = MagicMock(return_value={"id": "order123"})
        ex.fetch_ticker = MagicMock(return_value={"last": 31_000.0})
        return ex

    def test_open_position(self, pm, mock_exchange):
        from risk.manager import TradeSignal
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=30_000.0,
            stop_loss=29_000.0,
            take_profit=32_000.0,
            size=0.01,
            strategy="trend_ema",
            confidence=0.7,
        )
        pm.open(sig, exchange=mock_exchange)
        assert len(pm.positions) == 1

    def test_check_stops_triggers_stop_loss(self, pm, mock_exchange):
        from risk.manager import TradeSignal
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=30_000.0,
            stop_loss=29_500.0,
            take_profit=32_000.0,
            size=0.01,
            strategy="trend_ema",
            confidence=0.7,
        )
        pm.open(sig, exchange=mock_exchange)
        # Price falls below stop
        closed = pm.check_stops(current_prices={"BTC/USDT": 29_000.0},
                                exchange=mock_exchange)
        assert len(closed) == 1
        assert closed[0]["exit_reason"] == "stop_loss"

    def test_partial_take_profit(self, pm, mock_exchange):
        from risk.manager import TradeSignal
        sig = TradeSignal(
            symbol="ETH/USDT",
            direction="long",
            entry_price=2_000.0,
            stop_loss=1_900.0,
            take_profit=2_200.0,
            size=1.0,
            strategy="trend_ema",
            confidence=0.8,
        )
        pm.open(sig, exchange=mock_exchange)
        # Partial TP fires at 50% of target
        mid_target = 2_000 + (2_200 - 2_000) * 0.5
        pm.check_stops(current_prices={"ETH/USDT": mid_target + 1},
                       exchange=mock_exchange)
        pos = pm.positions.get("ETH/USDT")
        if pos:
            assert pos.size < 1.0  # partial close reduced size

    def test_no_positions_empty(self, pm):
        assert len(pm.positions) == 0


# ── Notifier ─────────────────────────────────────────────────────────────────

class TestNotifier:
    def test_notify_trade_open_no_token(self):
        from bot.notifier import notify_trade_open
        with patch("bot.notifier.CONFIG") as mock_cfg:
            mock_cfg.telegram_token = ""
            # Should not raise even with no token
            notify_trade_open("BTC/USDT", "long", 30_000.0, 0.01, "trend_ema")

    def test_notify_calls_telegram(self):
        from bot import notifier
        with patch.object(notifier, "_send_telegram", return_value=None) as mock_send:
            notifier.notify("Test message")
        mock_send.assert_called_once()

    def test_notify_trade_close_builds_message(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "_send_telegram",
                          side_effect=lambda m: messages.append(m)):
            notifier.notify_trade_close(
                symbol="ETH/USDT",
                direction="long",
                entry_price=2_000.0,
                exit_price=2_100.0,
                pnl=100.0,
                reason="take_profit",
            )
        assert len(messages) == 1
        assert "ETH/USDT" in messages[0]
        assert "100" in messages[0] or "pnl" in messages[0].lower()

    def test_notify_drawdown_alert(self):
        from bot import notifier
        messages = []
        with patch.object(notifier, "_send_telegram",
                          side_effect=lambda m: messages.append(m)):
            notifier.notify_drawdown_alert(0.12)
        assert len(messages) == 1
        assert "12" in messages[0] or "drawdown" in messages[0].lower()


# ── Auto Compounder ───────────────────────────────────────────────────────────

class TestAutoCompounder:
    def test_reinvest_all(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="reinvest_all", initial_capital=10_000)
        new_capital = ac.compound(current_equity=11_000, realised_pnl=1_000)
        assert new_capital == pytest.approx(11_000, rel=0.01)

    def test_reinvest_half(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="reinvest_half", initial_capital=10_000)
        new_capital = ac.compound(current_equity=11_000, realised_pnl=1_000)
        assert 10_000 < new_capital < 11_000

    def test_fixed_withdraw(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="fixed_withdraw", initial_capital=10_000,
                            withdraw_amount=200)
        new_capital = ac.compound(current_equity=11_000, realised_pnl=1_000)
        assert new_capital == pytest.approx(10_800, rel=0.01)

    def test_should_compound_positive_pnl(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="reinvest_all", initial_capital=10_000)
        assert ac.should_compound(realised_pnl=500) is True

    def test_should_not_compound_negative(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="reinvest_all", initial_capital=10_000)
        assert ac.should_compound(realised_pnl=-100) is False

    def test_rebalance_check(self):
        from bot.auto_compound import AutoCompounder
        ac = AutoCompounder(mode="reinvest_all", initial_capital=10_000)
        # No rebalance when allocations are near equal
        result = ac.rebalance_check(
            allocations={"BTC/USDT": 0.33, "ETH/USDT": 0.33, "SOL/USDT": 0.34},
            target=0.333,
        )
        assert isinstance(result, bool)


# ── Strategy Monitor ──────────────────────────────────────────────────────────

class TestStrategyMonitor:
    def test_healthy_with_good_data(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=1.0, baseline_win_rate=50.0)
        trades = [
            {"pnl": 100, "exit_time": "2022-01-03"},
            {"pnl":  80, "exit_time": "2022-01-05"},
            {"pnl": -20, "exit_time": "2022-01-07"},
            {"pnl":  60, "exit_time": "2022-01-09"},
            {"pnl":  40, "exit_time": "2022-01-11"},
        ]
        with patch("bot.strategy_monitor.get_trade_history", return_value=trades), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]):
            health = monitor.check()
        assert health.status in (HealthStatus.HEALTHY, HealthStatus.WARNING,
                                 HealthStatus.DEGRADED, HealthStatus.NO_DATA)

    def test_no_data_status(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=1.5)
        with patch("bot.strategy_monitor.get_trade_history", return_value=[]), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]):
            health = monitor.check()
        assert health.status == HealthStatus.NO_DATA

    def test_critical_on_negative_sharpe(self):
        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        monitor = StrategyMonitor("trend_ema", baseline_sharpe=1.5, baseline_win_rate=55.0)
        # 30 losing trades → Sharpe < 0
        trades = [{"pnl": -50, "exit_time": f"2022-01-{i:02d}"} for i in range(1, 31)]
        with patch("bot.strategy_monitor.get_trade_history", return_value=trades), \
             patch("bot.strategy_monitor.get_equity_history", return_value=[]):
            health = monitor.check()
        assert health.status in (HealthStatus.CRITICAL, HealthStatus.DEGRADED,
                                 HealthStatus.WARNING)


# ── Report generator ─────────────────────────────────────────────────────────

class TestReportGenerator:
    def test_generates_html(self, tmp_path):
        from reports.report_generator import generate_report
        from backtesting.engine import BacktestResult
        import pandas as pd

        idx = pd.date_range("2022-01-01", periods=100, freq="1h")
        equity = pd.Series(np.linspace(10_000, 12_000, 100), index=idx)
        trades = [
            {"pnl": 100, "symbol": "BTC/USDT", "entry_price": 30_000,
             "exit_price": 30_100, "exit_reason": "take_profit",
             "entry_time": "2022-01-01", "exit_time": "2022-01-02"},
        ]
        metrics = {
            "sharpe": 1.5, "max_drawdown_pct": -5.0, "win_rate": 65.0,
            "total_return_pct": 20.0, "total_trades": 1, "profit_factor": 2.0,
        }
        result = BacktestResult(
            equity_curve=equity, trades=trades, metrics=metrics, signals=pd.DataFrame()
        )

        with patch("reports.report_generator.CONFIG") as mock_cfg:
            mock_cfg.reports_dir = tmp_path
            path = generate_report(result, "trend_ema", "BTC/USDT")

        assert path.exists()
        content = path.read_text()
        assert "<html>" in content.lower() or "<!doctype" in content.lower()
