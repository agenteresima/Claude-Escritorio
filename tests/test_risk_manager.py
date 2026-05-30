"""
Edge-case tests for risk/manager.py.
Complements the coverage already in test_new_strategies.py.
"""
import pytest
import numpy as np
import pandas as pd

from risk.manager import RiskManager, TradeSignal


class TestRiskManager:
    @pytest.fixture
    def rm(self):
        return RiskManager(initial_capital=10_000)

    # ── Position sizing ───────────────────────────────────────────────────────

    def test_fixed_fraction_size(self, rm):
        size = rm.fixed_fraction_size(
            entry=40_000, stop=39_000, risk_pct=0.01
        )
        # 1% of 10k = $100 risk; stop gap = $1000/unit → 0.1 BTC
        assert size == pytest.approx(0.1, rel=0.05)

    def test_kelly_size_capped(self, rm):
        # Kelly formula: f = (win_rate * rr - loss_rate) / rr
        size = rm.kelly_size(
            win_rate=0.60, risk_reward=2.0,
            entry=40_000, stop=39_000, max_fraction=0.25
        )
        assert 0 < size <= 0.25 * 10_000 / 40_000

    def test_atr_size(self, rm):
        size = rm.atr_size(entry=40_000, atr=500, multiplier=1.5, risk_pct=0.01)
        # risk = 1% × 10k = 100; stop_gap = 750; size = 100/750
        assert size == pytest.approx(100 / 750, rel=0.05)

    def test_atr_stop_loss(self, rm):
        sl = rm.atr_stop_loss(entry=40_000, atr=500, direction="long", multiplier=1.5)
        assert sl == pytest.approx(40_000 - 1.5 * 500, rel=1e-6)

    def test_atr_stop_loss_short(self, rm):
        sl = rm.atr_stop_loss(entry=40_000, atr=500, direction="short", multiplier=1.5)
        assert sl == pytest.approx(40_000 + 1.5 * 500, rel=1e-6)

    def test_atr_take_profit_long(self, rm):
        tp = rm.atr_take_profit(entry=40_000, atr=500, direction="long", multiplier=3.0)
        assert tp == pytest.approx(40_000 + 3.0 * 500, rel=1e-6)

    # ── Signal validation ─────────────────────────────────────────────────────

    def test_valid_signal_passes(self, rm):
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=42_000,
            size=0.01,
            strategy="trend_ema",
            confidence=0.7,
        )
        valid, reason = rm.validate_signal(sig)
        assert valid is True

    def test_invalid_stop_above_entry_long(self, rm):
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=41_000,  # stop above entry — invalid
            take_profit=42_000,
            size=0.01,
            strategy="trend_ema",
            confidence=0.7,
        )
        valid, reason = rm.validate_signal(sig)
        assert valid is False

    def test_invalid_zero_size(self, rm):
        sig = TradeSignal(
            symbol="BTC/USDT",
            direction="long",
            entry_price=40_000,
            stop_loss=39_000,
            take_profit=42_000,
            size=0.0,
            strategy="trend_ema",
            confidence=0.7,
        )
        valid, reason = rm.validate_signal(sig)
        assert valid is False

    # ── Trailing stop ─────────────────────────────────────────────────────────

    def test_trailing_stop_rises_with_price(self, rm):
        stop1 = rm.update_trailing_stop(
            direction="long", current_price=41_000,
            current_stop=39_000, trailing_pct=0.03
        )
        stop2 = rm.update_trailing_stop(
            direction="long", current_price=42_000,
            current_stop=stop1, trailing_pct=0.03
        )
        assert stop2 > stop1

    def test_trailing_stop_never_decreases_long(self, rm):
        stops = [39_000.0]
        prices = [40_000, 41_000, 40_500, 42_000, 41_000]
        for p in prices:
            new_stop = rm.update_trailing_stop(
                direction="long", current_price=p,
                current_stop=stops[-1], trailing_pct=0.03
            )
            assert new_stop >= stops[-1]
            stops.append(new_stop)

    # ── Drawdown circuit-breaker ──────────────────────────────────────────────

    def test_circuit_breaker_triggers(self, rm):
        rm.update_equity(8_500)  # 15% drawdown from 10k
        assert rm.is_halted() is True

    def test_circuit_breaker_not_triggered_small_dd(self, rm):
        rm.update_equity(9_500)  # 5% drawdown — OK
        assert rm.is_halted() is False

    # ── Capital update ────────────────────────────────────────────────────────

    def test_capital_update(self, rm):
        rm.update_equity(11_000)
        assert rm.current_equity == pytest.approx(11_000)

    def test_peak_equity_tracked(self, rm):
        rm.update_equity(12_000)
        rm.update_equity(11_000)
        assert rm.peak_equity == pytest.approx(12_000)
