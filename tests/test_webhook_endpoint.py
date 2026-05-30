"""
Tests for the TradingView webhook POST endpoint (bot/webhook.py).
Tests the full alert handling: secret validation, symbol normalisation,
buy/sell/close routing, paused-bot guard, and unknown symbol rejection.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

WEBHOOK_SECRET = "test-webhook-secret-123"


@pytest.fixture(scope="module")
def client():
    with patch.dict(os.environ, {"WEBHOOK_SECRET": WEBHOOK_SECRET}):
        import importlib
        import bot.webhook as wh_module
        importlib.reload(wh_module)
        yield TestClient(wh_module.app), wh_module


# ── Health endpoint ───────────────────────────────────────────────────────────

class TestWebhookHealth:
    def test_health_ok(self, client):
        c, _ = client
        r = c.get("/webhook/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ── Secret validation ─────────────────────────────────────────────────────────

class TestSecretValidation:
    def test_wrong_secret_returns_403(self, client):
        c, _ = client
        r = c.post("/webhook/tradingview", json={
            "symbol": "BTCUSDT", "action": "buy",
            "price": 40_000.0, "secret": "wrong-secret",
        })
        assert r.status_code == 403

    def test_missing_secret_field_returns_422(self, client):
        c, _ = client
        r = c.post("/webhook/tradingview", json={
            "symbol": "BTCUSDT", "action": "buy", "price": 40_000.0,
        })
        assert r.status_code == 422  # Pydantic validation error

    def test_valid_secret_passes_gate(self, client):
        c, wh = client
        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })
        # Should not be 403
        assert r.status_code == 200


# ── Paused guard ──────────────────────────────────────────────────────────────

class TestPausedGuard:
    def test_paused_bot_returns_not_ok(self, client):
        c, wh = client
        with patch.object(wh, "get_state", return_value=True), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })
        data = r.json()
        assert data["ok"] is False
        assert "paused" in data.get("reason", "").lower()


# ── Symbol not in allowed pairs ───────────────────────────────────────────────

class TestSymbolFilter:
    def test_unknown_symbol_rejected(self, client):
        c, wh = client
        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["ETH/USDT"]   # BTC not in list
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })
        data = r.json()
        assert data["ok"] is False
        assert "symbol" in data.get("reason", "").lower()

    def test_known_symbol_not_rejected(self, client):
        c, wh = client
        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT", "ETH/USDT"]
            # No live trader — falls through to "no_position_change"
            wh._live_trader = None
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })
        assert r.json()["ok"] is True


# ── BUY action ────────────────────────────────────────────────────────────────

class TestBuyAction:
    def _make_trader_mock(self):
        trader = MagicMock()
        trader.pos_mgr.positions = {}  # no open positions
        trader.risk = MagicMock()
        trader.risk.validate_signal.return_value = True
        trader.risk.atr_size.return_value = 0.01
        return trader

    def test_buy_opens_long_when_no_position(self, client):
        c, wh = client
        trader = self._make_trader_mock()
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg, \
             patch.object(wh, "insert_trade"), \
             patch.object(wh, "log_signal"), \
             patch.object(wh, "notify_trade_open"):
            mock_cfg.pairs = ["BTC/USDT"]
            mock_cfg.dry_run = True
            mock_cfg.risk.hard_stop_pct = 0.03
            mock_cfg.risk.take_profit_pct = 0.06
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })

        data = r.json()
        assert data["ok"] is True
        assert data["action"] == "opened_long"

    def test_buy_skipped_when_position_already_open(self, client):
        c, wh = client
        trader = self._make_trader_mock()
        trader.pos_mgr.positions = {"BTC/USDT": MagicMock()}  # already open
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })

        # Already open — falls through to "no_position_change"
        assert r.json()["ok"] is True

    def test_buy_with_explicit_stop_and_tp(self, client):
        c, wh = client
        trader = self._make_trader_mock()
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg, \
             patch.object(wh, "insert_trade") as mock_insert, \
             patch.object(wh, "log_signal"), \
             patch.object(wh, "notify_trade_open"):
            mock_cfg.pairs = ["BTC/USDT"]
            mock_cfg.dry_run = True
            mock_cfg.risk.hard_stop_pct = 0.03
            mock_cfg.risk.take_profit_pct = 0.06
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT",
                "action": "buy",
                "price": 40_000.0,
                "stop_loss": 39_000.0,
                "take_profit": 42_000.0,
                "size": 0.005,
                "secret": WEBHOOK_SECRET,
            })

        assert r.json()["ok"] is True
        # Verify open_position called with explicit stop
        trader.pos_mgr.open_position.assert_called_once()
        call_kwargs = trader.pos_mgr.open_position.call_args
        # stop_loss should use provided value
        _, _, _, _, sl, _, _ = call_kwargs[0]
        assert sl == pytest.approx(39_000.0)

    def test_buy_signal_validation_failure(self, client):
        c, wh = client
        trader = self._make_trader_mock()
        trader.risk.validate_signal.return_value = False  # validation fails
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            mock_cfg.risk.hard_stop_pct = 0.03
            mock_cfg.risk.take_profit_pct = 0.06
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })

        data = r.json()
        assert data["ok"] is False
        assert "validation" in data.get("reason", "").lower()


# ── SELL / CLOSE action ───────────────────────────────────────────────────────

class TestSellAction:
    def test_sell_closes_open_position(self, client):
        c, wh = client
        trader = MagicMock()
        trader.pos_mgr.positions = {"BTC/USDT": MagicMock()}
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg, \
             patch.object(wh, "log_signal"):
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "sell",
                "price": 41_000.0, "secret": WEBHOOK_SECRET,
            })

        data = r.json()
        assert data["ok"] is True
        assert data["action"] == "closed"
        trader.pos_mgr._close.assert_called_once_with("BTC/USDT", 41_000.0, "webhook_sell")

    def test_close_action_same_as_sell(self, client):
        c, wh = client
        trader = MagicMock()
        trader.pos_mgr.positions = {"ETH/USDT": MagicMock()}
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg, \
             patch.object(wh, "log_signal"):
            mock_cfg.pairs = ["ETH/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "ETHUSDT", "action": "close",
                "price": 2_100.0, "secret": WEBHOOK_SECRET,
            })

        assert r.json()["action"] == "closed"

    def test_sell_no_position_returns_no_change(self, client):
        c, wh = client
        trader = MagicMock()
        trader.pos_mgr.positions = {}   # no open position
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "sell",
                "price": 41_000.0, "secret": WEBHOOK_SECRET,
            })

        assert r.json()["action"] == "no_position_change"
        trader.pos_mgr._close.assert_not_called()

    def test_short_action_treated_as_close(self, client):
        c, wh = client
        trader = MagicMock()
        trader.pos_mgr.positions = {"BTC/USDT": MagicMock()}
        wh._live_trader = trader

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg, \
             patch.object(wh, "log_signal"):
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "short",
                "price": 41_000.0, "secret": WEBHOOK_SECRET,
            })

        assert r.json()["action"] == "closed"


# ── No live trader configured ─────────────────────────────────────────────────

class TestNoLiveTrader:
    def test_buy_without_trader_returns_no_change(self, client):
        c, wh = client
        wh._live_trader = None

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "buy",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })

        # No trader → falls to "no_position_change"
        assert r.json()["ok"] is True
        assert r.json()["action"] == "no_position_change"

    def test_sell_without_trader_returns_no_change(self, client):
        c, wh = client
        wh._live_trader = None

        with patch.object(wh, "get_state", return_value=False), \
             patch.object(wh, "CONFIG") as mock_cfg:
            mock_cfg.pairs = ["BTC/USDT"]
            r = c.post("/webhook/tradingview", json={
                "symbol": "BTCUSDT", "action": "sell",
                "price": 40_000.0, "secret": WEBHOOK_SECRET,
            })

        assert r.json()["action"] == "no_position_change"
