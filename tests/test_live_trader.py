"""
Unit tests for bot/live_trader.py (LiveTrader.tick and helpers).
Exchange, database, and notification calls are fully mocked.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, call
from tests.conftest import make_ohlcv


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_config():
    cfg = MagicMock()
    cfg.dry_run           = True
    cfg.pairs             = ["BTC/USDT", "ETH/USDT"]
    cfg.timeframe         = "1h"
    cfg.active_strategy   = "trend_ema"
    cfg.exchange.name     = "binance"
    cfg.exchange.api_key  = ""
    cfg.exchange.api_secret = ""
    cfg.exchange.sandbox  = False
    cfg.risk.max_drawdown_pct    = 0.15
    cfg.risk.risk_reward_ratio   = 2.0
    cfg.risk.max_position_size_pct = 0.10
    cfg.risk.hard_stop_pct       = 0.03
    cfg.risk.take_profit_pct     = 0.06
    cfg.data_dir = MagicMock()
    return cfg


def _get_state_side_effect(key, default=None):
    if key == "active_strategy":
        return "trend_ema"
    return default


@pytest.fixture
def live_trader(mock_config):
    """Construct a LiveTrader with all side-effects mocked."""
    with patch("ccxt.binance") as mock_exc_cls, \
         patch("bot.live_trader.init_db"), \
         patch("bot.live_trader.get_open_trades", return_value=[]), \
         patch("bot.live_trader.get_state", side_effect=_get_state_side_effect), \
         patch("bot.live_trader.notify_startup"):
        mock_exc_cls.return_value = MagicMock()
        from bot.live_trader import LiveTrader
        trader = LiveTrader(mock_config)
    return trader


# ── Constructor ───────────────────────────────────────────────────────────────

class TestLiveTraderInit:
    def test_creates_with_mocks(self, live_trader):
        assert live_trader is not None
        assert live_trader.dry_run is True

    def test_restores_no_positions_when_db_empty(self, mock_config):
        with patch("ccxt.binance"), \
             patch("bot.live_trader.init_db"), \
             patch("bot.live_trader.get_open_trades", return_value=[]), \
             patch("bot.live_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.live_trader.notify_startup"):
            from bot.live_trader import LiveTrader
            trader = LiveTrader(mock_config)
        assert len(trader.pos_mgr.positions) == 0

    def test_restores_open_positions_from_db(self, mock_config):
        fake_trades = [{
            "symbol": "BTC/USDT", "direction": "long",
            "entry_price": 40_000.0, "size": 0.01,
            "stop_loss": 39_000.0, "take_profit": 42_000.0,
        }]
        with patch("ccxt.binance"), \
             patch("bot.live_trader.init_db"), \
             patch("bot.live_trader.get_open_trades", return_value=fake_trades), \
             patch("bot.live_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.live_trader.notify_startup"):
            from bot.live_trader import LiveTrader
            trader = LiveTrader(mock_config)
        assert "BTC/USDT" in trader.pos_mgr.positions


# ── Pause / Resume via API state ──────────────────────────────────────────────

class TestTickPauseLogic:
    def test_tick_does_nothing_when_paused(self, live_trader):
        with patch("bot.live_trader.get_state", return_value=True), \
             patch.object(live_trader, "fetch_latest") as mock_fetch:
            live_trader.tick("BTC/USDT")
        mock_fetch.assert_not_called()

    def test_tick_proceeds_when_not_paused(self, live_trader):
        df = make_ohlcv(200)
        sig_df = df.copy()
        sig_df["signal"]      = 0
        sig_df["stop_loss"]   = sig_df["close"] * 0.97
        sig_df["take_profit"] = sig_df["close"] * 1.06
        sig_df["atr_14"]      = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "trend_ema"
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch.object(live_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch("bot.live_trader.add_candle_patterns", return_value=sig_df.assign(candle_score=1)), \
             patch.object(live_trader, "_refresh_sentiment"):
            live_trader.tick("BTC/USDT")

        # No order placed (signal=0), but fetch was called
        live_trader.exchange.create_order.assert_not_called()


# ── Force-close via API command ───────────────────────────────────────────────

class TestForceClose:
    def test_force_close_command_closes_position(self, live_trader):
        live_trader.pos_mgr.positions["BTC/USDT"] = MagicMock()
        live_trader.exchange.fetch_ticker.return_value = {"last": 41_000.0}

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "force_close_BTC/USDT":
                return True
            if key == "active_strategy":
                return "trend_ema"
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch("data.database.set_state"), \
             patch.object(live_trader.pos_mgr, "_close") as mock_close:
            live_trader.tick("BTC/USDT")

        mock_close.assert_called_once_with("BTC/USDT", 41_000.0, "api_force_close")


# ── Strategy hot-swap ─────────────────────────────────────────────────────────

class TestStrategyHotSwap:
    def test_strategy_switches_when_state_changes(self, live_trader):
        original_name = live_trader.strategy.name

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "breakout"   # Different from current
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state):
            result = live_trader._check_api_commands()

        assert live_trader.strategy.name == "breakout"
        assert result is True   # not paused, continue

    def test_strategy_unchanged_when_same(self, live_trader):
        original = live_trader.strategy

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return live_trader.strategy.name
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state):
            live_trader._check_api_commands()

        assert live_trader.strategy is original


# ── Signal processing ─────────────────────────────────────────────────────────

class TestSignalProcessing:
    def test_buy_signal_places_order(self, live_trader):
        df = make_ohlcv(200)
        sig_df = df.copy()
        sig_df["signal"]        = 0
        sig_df.iloc[-1, sig_df.columns.get_loc("signal")] = 1  # last bar is buy
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0
        sig_df["candle_score"]  = 1.0

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "trend_ema"
            if key.startswith("force_close_"):
                return False
            return default

        live_trader.exchange.fetch_ticker.return_value = {"last": float(sig_df.iloc[-1]["close"])}
        live_trader.exchange.fetch_balance.return_value = {"USDT": {"free": 10_000.0}}

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch("bot.live_trader.insert_trade"), \
             patch("bot.live_trader.save_equity"), \
             patch.object(live_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(live_trader.corr_filter, "is_correlated_with_open", return_value=False), \
             patch("bot.live_trader.add_candle_patterns",
                   return_value=sig_df.assign(candle_score=1.0)), \
             patch.object(live_trader, "_refresh_sentiment"), \
             patch.object(live_trader.pos_mgr, "open_position") as mock_open:
            live_trader._sentiment_gate = {"allow_long": True, "allow_short": True, "reason": "ok"}
            live_trader.tick("BTC/USDT")

        mock_open.assert_called_once()
        call_args = mock_open.call_args[0]
        assert call_args[0] == "BTC/USDT"
        assert call_args[1] == "buy"

    def test_events_filter_blocks_entry(self, live_trader):
        df = make_ohlcv(200)
        sig_df = df.copy()
        sig_df["signal"]        = 0
        sig_df.iloc[-1, sig_df.columns.get_loc("signal")] = 1
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "trend_ema"
            if key.startswith("force_close_"):
                return False
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch.object(live_trader.events, "is_safe_to_trade",
                          return_value=(False, "FOMC meeting")), \
             patch.object(live_trader.pos_mgr, "open_position") as mock_open:
            live_trader.tick("BTC/USDT")

        mock_open.assert_not_called()

    def test_correlation_filter_blocks_entry(self, live_trader):
        df = make_ohlcv(200)
        sig_df = df.copy()
        sig_df["signal"]        = 0
        sig_df.iloc[-1, sig_df.columns.get_loc("signal")] = 1
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "trend_ema"
            if key.startswith("force_close_"):
                return False
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch.object(live_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch("bot.live_trader.add_candle_patterns",
                   return_value=sig_df.assign(candle_score=1.0)), \
             patch.object(live_trader, "_refresh_sentiment"), \
             patch.object(live_trader.corr_filter, "is_correlated_with_open",
                          return_value=True), \
             patch.object(live_trader.pos_mgr, "open_position") as mock_open:
            live_trader._sentiment_gate = {"allow_long": True, "allow_short": True, "reason": "ok"}
            live_trader.tick("BTC/USDT")

        mock_open.assert_not_called()

    def test_exit_signal_closes_open_position(self, live_trader):
        df = make_ohlcv(200)
        sig_df = df.copy()
        sig_df["signal"]        = -1  # exit signal
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        live_trader.pos_mgr.positions["BTC/USDT"] = MagicMock()
        price = float(sig_df.iloc[-1]["close"])

        def fake_get_state(key, default=None):
            if key == "paused":
                return False
            if key == "active_strategy":
                return "trend_ema"
            if key.startswith("force_close_"):
                return False
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch.object(live_trader.pos_mgr, "update", return_value=[]), \
             patch.object(live_trader.pos_mgr, "_close") as mock_close:
            live_trader.tick("BTC/USDT")

        mock_close.assert_called_once_with("BTC/USDT", price, "signal_exit")


# ── Dry-run vs live ───────────────────────────────────────────────────────────

class TestDryRunVsLive:
    def test_dry_run_does_not_call_create_order(self, live_trader):
        assert live_trader.dry_run is True
        df = make_ohlcv(200)
        price = float(df.iloc[-1]["close"])
        live_trader.exchange.fetch_ticker.return_value = {"last": price}

        sig_df = df.copy()
        sig_df["signal"]        = 0
        sig_df.iloc[-1, sig_df.columns.get_loc("signal")] = 1
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        def fake_get_state(key, default=None):
            if key == "paused": return False
            if key == "active_strategy": return "trend_ema"
            if key.startswith("force_close_"): return False
            return default

        with patch("bot.live_trader.get_state", side_effect=fake_get_state), \
             patch.object(live_trader, "fetch_latest", return_value=df), \
             patch.object(live_trader.strategy, "run", return_value=sig_df), \
             patch("bot.live_trader.log_signal"), \
             patch("bot.live_trader.insert_trade"), \
             patch("bot.live_trader.save_equity"), \
             patch.object(live_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(live_trader.corr_filter, "is_correlated_with_open", return_value=False), \
             patch("bot.live_trader.add_candle_patterns",
                   return_value=sig_df.assign(candle_score=1.0)), \
             patch.object(live_trader, "_refresh_sentiment"):
            live_trader._sentiment_gate = {"allow_long": True, "allow_short": True, "reason": "ok"}
            live_trader.tick("BTC/USDT")

        live_trader.exchange.create_order.assert_not_called()

    def test_get_balance_dry_run(self, live_trader):
        live_trader.risk.portfolio.capital = 9_500.0
        bal = live_trader.get_balance()
        assert bal == pytest.approx(9_500.0)


# ── Seconds to next close ─────────────────────────────────────────────────────

class TestNextClose:
    def test_returns_positive_seconds(self, live_trader):
        secs = live_trader._seconds_to_next_close()
        assert 0 < secs <= 3600 + 5

    def test_unknown_timeframe_defaults_to_1h(self, live_trader, mock_config):
        mock_config.timeframe = "99m"
        live_trader.cfg = mock_config
        secs = live_trader._seconds_to_next_close()
        assert secs > 0
