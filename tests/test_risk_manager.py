"""
Tests for risk/manager.py — matches the actual RiskManager interface.
"""
import pytest
import numpy as np

from risk.manager import RiskManager, TradeSignal, PortfolioState


class TestPortfolioState:
    def test_initial_drawdown_zero(self):
        ps = PortfolioState(capital=10_000)
        ps.peak_equity = 10_000
        assert ps.current_drawdown() == 0.0

    def test_drawdown_computed(self):
        ps = PortfolioState(capital=8_500)
        ps.peak_equity = 10_000
        assert ps.current_drawdown() == pytest.approx(0.15, rel=1e-4)

    def test_update_tracks_peak(self):
        ps = PortfolioState(capital=10_000)
        ps.peak_equity = 10_000
        ps.update(12_000)
        assert ps.peak_equity == pytest.approx(12_000)
        ps.update(11_000)
        assert ps.peak_equity == pytest.approx(12_000)  # doesn't go down

    def test_equity_curve_appended(self):
        ps = PortfolioState(capital=10_000)
        ps.peak_equity = 10_000
        ps.update(10_500)
        ps.update(11_000)
        assert len(ps.equity_curve) == 2


class TestRiskManager:
    @pytest.fixture
    def rm(self):
        return RiskManager(initial_capital=10_000)

    # ── Position sizing ───────────────────────────────────────────────────────

    def test_fixed_fraction_size_basic(self, rm):
        # 2% of 10k = $200 risk; stop gap = $1000 → 0.2 BTC
        size = rm.fixed_fraction_size(entry=40_000, stop=39_000)
        assert size == pytest.approx(200 / 1_000, rel=0.05)

    def test_fixed_fraction_zero_risk_gap(self, rm):
        size = rm.fixed_fraction_size(entry=40_000, stop=40_000)
        assert size == 0.0

    def test_atr_size_returns_positive(self, rm):
        size = rm.atr_size(entry=40_000, atr=500, multiplier=1.5)
        assert size > 0

    def test_kelly_size_capped(self, rm):
        # High win_rate, high avg_win should still be capped by max_position_size_pct
        size = rm.kelly_size(win_rate=0.70, avg_win=200, avg_loss=80)
        assert 0 <= size <= rm.cfg.max_position_size_pct

    def test_kelly_size_zero_avg_loss(self, rm):
        size = rm.kelly_size(win_rate=0.6, avg_win=100, avg_loss=0)
        assert size == rm.cfg.stake_amount_pct

    # ── ATR stops ────────────────────────────────────────────────────────────

    def test_atr_stop_loss_long(self, rm):
        sl = rm.atr_stop_loss(entry=40_000, atr=500, direction="long", multiplier=2.0)
        assert sl == pytest.approx(40_000 - 2.0 * 500)

    def test_atr_stop_loss_short(self, rm):
        sl = rm.atr_stop_loss(entry=40_000, atr=500, direction="short", multiplier=2.0)
        assert sl == pytest.approx(40_000 + 2.0 * 500)

    def test_atr_take_profit_long(self, rm):
        # RR = 2.0 (default), risk = entry - stop
        entry, stop = 40_000, 39_000
        tp = rm.atr_take_profit(entry=entry, stop=stop, direction="long")
        assert tp == pytest.approx(40_000 + 1_000 * rm.cfg.risk_reward_ratio)

    def test_atr_take_profit_short(self, rm):
        entry, stop = 40_000, 41_000
        tp = rm.atr_take_profit(entry=entry, stop=stop, direction="short")
        assert tp < entry

    def test_atr_take_profit_custom_rr(self, rm):
        tp = rm.atr_take_profit(entry=40_000, stop=39_000, direction="long", rr_ratio=3.0)
        assert tp == pytest.approx(40_000 + 1_000 * 3.0)

    # ── Signal validation ─────────────────────────────────────────────────────

    def test_valid_signal_passes(self, rm):
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=42_000,   # 2:1 R/R — matches min rr=2.0
        )
        valid = rm.validate_signal(sig)
        assert valid is True

    def test_invalid_rr_below_minimum(self, rm):
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=40_500,   # only 0.5:1 R/R — below 2.0 minimum
        )
        valid = rm.validate_signal(sig)
        assert valid is False

    def test_halted_on_max_drawdown(self, rm):
        # Simulate 16% drawdown (exceeds 15% limit)
        rm.portfolio.capital = 8_400
        rm.portfolio.peak_equity = 10_000
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=42_000,
        )
        valid = rm.validate_signal(sig)
        assert valid is False

    def test_blocked_at_max_open_trades(self, rm):
        rm.portfolio.open_trades = rm.cfg.max_open_trades
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=42_000,
        )
        valid = rm.validate_signal(sig)
        assert valid is False

    # ── Trailing stop ─────────────────────────────────────────────────────────

    def test_trailing_stop_rises_long(self, rm):
        stop1 = rm.update_trailing_stop(
            current_price=41_000, entry=40_000,
            current_stop=39_000, direction="long"
        )
        stop2 = rm.update_trailing_stop(
            current_price=42_000, entry=40_000,
            current_stop=stop1, direction="long"
        )
        assert stop2 > stop1

    def test_trailing_stop_never_decreases_long(self, rm):
        stops = [39_000.0]
        prices = [40_000, 41_000, 40_500, 42_000, 41_000]
        for p in prices:
            new_stop = rm.update_trailing_stop(
                current_price=p, entry=40_000,
                current_stop=stops[-1], direction="long"
            )
            assert new_stop >= stops[-1]
            stops.append(new_stop)

    def test_trailing_stop_short_falls(self, rm):
        stop1 = rm.update_trailing_stop(
            current_price=39_000, entry=40_000,
            current_stop=41_000, direction="short"
        )
        stop2 = rm.update_trailing_stop(
            current_price=38_000, entry=40_000,
            current_stop=stop1, direction="short"
        )
        assert stop2 < stop1

    def test_trailing_stop_formula_long(self, rm):
        price = 42_000
        trail = rm.cfg.trailing_stop_pct
        expected = price * (1 - trail)
        new_stop = rm.update_trailing_stop(
            current_price=price, entry=40_000,
            current_stop=39_000, direction="long"
        )
        assert new_stop == pytest.approx(expected)
