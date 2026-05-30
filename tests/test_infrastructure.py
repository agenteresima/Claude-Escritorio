"""
Tests for data and bot infrastructure:
  - data/websocket_feed.py  (Candle, CandleBuffer)
  - bot/webhook.py          (TVAlert validation, symbol normalisation, HMAC)
  - data/database.py        (schema, CRUD — in-memory)
  - config/settings.py      (env var loading, defaults)
"""
import os
import hmac
import hashlib
import pytest
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path


# ── Candle / CandleBuffer ────────────────────────────────────────────────────

class TestCandle:
    def test_candle_from_ohlcv(self):
        from data.websocket_feed import Candle
        ts_ms = 1_700_000_000_000
        c = Candle("BTC/USDT", [ts_ms, 40_000, 40_500, 39_500, 40_200, 1.5])
        assert c.symbol == "BTC/USDT"
        assert c.open   == pytest.approx(40_000)
        assert c.close  == pytest.approx(40_200)
        assert c.volume == pytest.approx(1.5)

    def test_candle_to_series(self):
        from data.websocket_feed import Candle
        c = Candle("ETH/USDT", [1_700_000_000_000, 2_000, 2_100, 1_950, 2_050, 10])
        d = c.to_series()
        for k in ["open", "high", "low", "close", "volume"]:
            assert k in d

    def test_candle_repr(self):
        from data.websocket_feed import Candle
        c = Candle("BTC/USDT", [1_700_000_000_000, 40_000, 40_500, 39_500, 40_200, 1.5])
        assert "BTC/USDT" in repr(c)


class TestCandleBuffer:
    def test_buffer_appends(self):
        from data.websocket_feed import CandleBuffer, Candle
        buf = CandleBuffer(maxlen=50)
        c = Candle("BTC/USDT", [1_700_000_000_000, 40_000, 40_500, 39_500, 40_200, 1.5])
        buf.push(c)
        df = buf.to_dataframe()
        assert len(df) == 1
        assert "close" in df.columns

    def test_buffer_respects_maxlen(self):
        from data.websocket_feed import CandleBuffer, Candle
        buf = CandleBuffer(maxlen=10)
        for i in range(20):
            buf.push(Candle("BTC/USDT",
                            [1_700_000_000_000 + i * 3_600_000,
                             40_000, 40_500, 39_500, 40_200, 1.0]))
        assert len(buf.to_dataframe()) == 10

    def test_empty_buffer_returns_empty_df(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer()
        df = buf.to_dataframe()
        assert len(df) == 0


# ── Webhook ───────────────────────────────────────────────────────────────────

class TestWebhookNormalise:
    def test_normalise_binance_symbol(self):
        from bot.webhook import _normalise_symbol
        assert _normalise_symbol("BTCUSDT")  == "BTC/USDT"
        assert _normalise_symbol("ETHUSDT")  == "ETH/USDT"
        assert _normalise_symbol("SOLUSDT")  == "SOL/USDT"
        assert _normalise_symbol("BNB/USDT") == "BNB/USDT"  # already normalised

    def test_normalise_bybit_symbol(self):
        from bot.webhook import _normalise_symbol
        assert _normalise_symbol("BTCUSDT.P") == "BTC/USDT" or \
               _normalise_symbol("BTCUSDT.P").startswith("BTC")


class TestWebhookHMAC:
    def test_valid_secret_passes(self):
        from bot.webhook import _verify_secret
        secret = "test_webhook_secret"
        assert _verify_secret(secret, secret) is True

    def test_invalid_secret_fails(self):
        from bot.webhook import _verify_secret
        assert _verify_secret("correct_secret", "wrong_secret") is False

    def test_empty_secret_fails(self):
        from bot.webhook import _verify_secret
        assert _verify_secret("correct_secret", "") is False


class TestTVAlertModel:
    def test_valid_alert(self):
        from bot.webhook import TVAlert
        alert = TVAlert(
            symbol="BTCUSDT",
            action="buy",
            price=40_000.0,
            secret="test_secret",
        )
        assert alert.action == "buy"

    def test_missing_required_fields(self):
        from bot.webhook import TVAlert
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            TVAlert(action="buy", price=40_000.0)  # missing symbol and secret


# ── Database schema and CRUD ──────────────────────────────────────────────────

class TestDatabase:
    @pytest.fixture(autouse=True)
    def patch_db(self, tmp_path):
        import data.database as db_module
        db_path = tmp_path / "test.db"
        with patch.object(db_module, "DB_PATH", db_path):
            db_module.init_db()
            yield db_module

    def test_init_creates_tables(self, patch_db, tmp_path):
        db_path = tmp_path / "test.db"
        with sqlite3.connect(str(db_path)) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
        assert "trades" in tables
        assert "equity_snapshots" in tables
        assert "bot_state" in tables

    def test_insert_and_get_trade(self, patch_db):
        patch_db.insert_trade(
            symbol="BTC/USDT", direction="long",
            entry_price=40_000.0, size=0.01,
            stop_loss=39_000.0, take_profit=42_000.0,
            strategy="trend_ema"
        )
        open_trades = patch_db.get_open_trades()
        assert len(open_trades) == 1
        assert open_trades[0]["symbol"] == "BTC/USDT"

    def test_close_trade(self, patch_db):
        patch_db.insert_trade(
            symbol="ETH/USDT", direction="long",
            entry_price=2_000.0, size=1.0,
            stop_loss=1_900.0, take_profit=2_200.0,
            strategy="trend_ema"
        )
        open_trades = patch_db.get_open_trades()
        trade_id = open_trades[0]["id"]
        patch_db.close_trade(
            trade_id=trade_id,
            exit_price=2_100.0,
            pnl=100.0,
            reason="take_profit"
        )
        assert len(patch_db.get_open_trades()) == 0

    def test_state_persistence(self, patch_db):
        patch_db.set_state("paused", True)
        patch_db.set_state("active_strategy", "regime_adaptive")
        assert patch_db.get_state("paused", False) is True
        assert patch_db.get_state("active_strategy", "") == "regime_adaptive"

    def test_equity_snapshot(self, patch_db):
        patch_db.save_equity(equity=10_500.0, strategy="trend_ema")
        history = patch_db.get_equity_history("trend_ema", limit=10)
        assert len(history) == 1
        assert history[0]["equity"] == pytest.approx(10_500.0)

    def test_trade_stats_no_trades(self, patch_db):
        stats = patch_db.trade_stats()
        assert stats["total_trades"] == 0
        assert stats["win_rate"] == 0.0

    def test_trade_stats_with_trades(self, patch_db):
        for pnl in [100, -50, 80, 60, -30]:
            patch_db.insert_trade(
                symbol="BTC/USDT", direction="long",
                entry_price=40_000.0, size=0.01,
                stop_loss=39_000.0, take_profit=42_000.0,
                strategy="trend_ema"
            )
        open_ = patch_db.get_open_trades()
        pnls = [100, -50, 80, 60, -30]
        for i, trade in enumerate(open_):
            patch_db.close_trade(
                trade["id"], exit_price=40_000 + pnls[i],
                pnl=pnls[i], reason="test"
            )
        stats = patch_db.trade_stats("trend_ema")
        assert stats["total_trades"] == 5
        assert stats["win_rate"] == pytest.approx(60.0, abs=1.0)


# ── Config loading ────────────────────────────────────────────────────────────

class TestConfig:
    def test_config_loads(self):
        from config import CONFIG
        assert CONFIG is not None
        assert CONFIG.backtest.initial_capital == 10_000.0

    def test_pairs_are_list(self):
        from config import CONFIG
        assert isinstance(CONFIG.pairs, list)
        assert len(CONFIG.pairs) > 0

    def test_active_strategy_env_override(self):
        with patch.dict(os.environ, {"ACTIVE_STRATEGY": "trend_ema"}):
            from config.settings import BotConfig
            cfg = BotConfig()
            assert cfg.active_strategy == "trend_ema"

    def test_dry_run_env_override(self):
        with patch.dict(os.environ, {"DRY_RUN": "false"}):
            from config.settings import BotConfig
            cfg = BotConfig()
            assert cfg.dry_run is False

    def test_backtest_config_standalone(self):
        from config import BacktestConfig
        bc = BacktestConfig(initial_capital=50_000, commission=0.002)
        assert bc.initial_capital == 50_000.0
        assert bc.commission == 0.002
