"""
Tests for the FastAPI REST control API (bot/api.py).
Uses TestClient — no network required. Database functions are patched.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


API_KEY = "test-api-key-123"


@pytest.fixture(scope="module")
def client():
    with patch.dict(os.environ, {"BOT_API_KEY": API_KEY}):
        import importlib
        import bot.api as api_module
        importlib.reload(api_module)
        yield TestClient(api_module.app)


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_health_requires_no_key(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_status_requires_key(self, client):
        r = client.get("/status")
        assert r.status_code == 422  # missing header

    def test_status_wrong_key_rejected(self, client):
        r = client.get("/status", headers={"x-api-key": "wrong"})
        assert r.status_code == 401

    def test_status_valid_key_accepted(self, client):
        with patch("bot.api.get_open_trades", return_value=[]), \
             patch("bot.api.get_state", return_value=None), \
             patch("bot.api.trade_stats", return_value={}):
            r = client.get("/status", headers={"x-api-key": API_KEY})
        assert r.status_code == 200

    def test_strategies_endpoint_public(self, client):
        r = client.get("/strategies")
        assert r.status_code == 200
        assert "strategies" in r.json()
        assert "trend_ema" in r.json()["strategies"]


# ── Status endpoint ───────────────────────────────────────────────────────────

class TestStatusEndpoint:
    def test_returns_expected_keys(self, client):
        with patch("bot.api.get_open_trades", return_value=[]), \
             patch("bot.api.get_state", return_value=None), \
             patch("bot.api.trade_stats", return_value={"total_trades": 5}):
            r = client.get("/status", headers={"x-api-key": API_KEY})
        data = r.json()
        for key in ("paused", "active_strategy", "dry_run", "pairs", "open_positions"):
            assert key in data

    def test_paused_state_reflected(self, client):
        def fake_get_state(key, default=None):
            if key == "paused":
                return True
            return default

        with patch("bot.api.get_open_trades", return_value=[]), \
             patch("bot.api.get_state", side_effect=fake_get_state), \
             patch("bot.api.trade_stats", return_value={}):
            r = client.get("/status", headers={"x-api-key": API_KEY})
        assert r.json()["paused"] is True

    def test_open_positions_count(self, client):
        fake_positions = [
            {"id": 1, "symbol": "BTC/USDT", "direction": "long",
             "entry_price": 40_000.0, "size": 0.01},
            {"id": 2, "symbol": "ETH/USDT", "direction": "long",
             "entry_price": 2_000.0, "size": 0.5},
        ]
        with patch("bot.api.get_open_trades", return_value=fake_positions), \
             patch("bot.api.get_state", return_value=None), \
             patch("bot.api.trade_stats", return_value={}):
            r = client.get("/status", headers={"x-api-key": API_KEY})
        assert r.json()["open_positions"] == 2


# ── Pause / Resume ────────────────────────────────────────────────────────────

class TestPauseResume:
    def test_pause_sets_state(self, client):
        with patch("bot.api.set_state") as mock_set:
            r = client.post("/pause", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert r.json()["paused"] is True
        mock_set.assert_called_once_with("paused", True)

    def test_resume_clears_state(self, client):
        with patch("bot.api.set_state") as mock_set:
            r = client.post("/resume", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert r.json()["paused"] is False
        mock_set.assert_called_once_with("paused", False)


# ── Strategy switch ───────────────────────────────────────────────────────────

class TestStrategySwitchEndpoint:
    def test_valid_strategy_accepted(self, client):
        with patch("bot.api.set_state") as mock_set:
            r = client.post(
                "/strategy",
                json={"strategy": "trend_ema"},
                headers={"x-api-key": API_KEY},
            )
        assert r.status_code == 200
        assert r.json()["strategy"] == "trend_ema"
        mock_set.assert_called_once_with("active_strategy", "trend_ema")

    def test_invalid_strategy_rejected(self, client):
        r = client.post(
            "/strategy",
            json={"strategy": "nonexistent_strategy"},
            headers={"x-api-key": API_KEY},
        )
        assert r.status_code == 400

    def test_all_known_strategies_accepted(self, client):
        from strategies import STRATEGIES
        for name in list(STRATEGIES.keys())[:3]:
            with patch("bot.api.set_state"):
                r = client.post(
                    "/strategy",
                    json={"strategy": name},
                    headers={"x-api-key": API_KEY},
                )
            assert r.status_code == 200, f"Strategy {name} rejected"


# ── Trades / Equity / Metrics ─────────────────────────────────────────────────

class TestDataEndpoints:
    def test_trades_returns_list(self, client):
        fake_trades = [
            {"id": 1, "symbol": "BTC/USDT", "pnl": 50.0, "is_open": 0},
        ]
        with patch("bot.api.get_trade_history", return_value=fake_trades):
            r = client.get("/trades", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json()[0]["symbol"] == "BTC/USDT"

    def test_trades_filtered_by_symbol(self, client):
        with patch("bot.api.get_trade_history", return_value=[]) as mock_hist:
            r = client.get("/trades?symbol=BTC/USDT", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        mock_hist.assert_called_once_with(symbol="BTC/USDT", limit=100)

    def test_equity_returns_list(self, client):
        fake_equity = [
            {"ts": "2022-01-01T00:00:00", "equity": 10_500.0, "drawdown": -0.01},
        ]
        with patch("bot.api.get_equity_history", return_value=fake_equity), \
             patch("bot.api.get_state", return_value="trend_ema"):
            r = client.get("/equity", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_metrics_returns_stats(self, client):
        fake_stats = {"total_trades": 10, "win_rate": 60.0, "total_pnl": 250.0}
        with patch("bot.api.trade_stats", return_value=fake_stats), \
             patch("bot.api.get_state", return_value="trend_ema"):
            r = client.get("/metrics", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert r.json()["total_trades"] == 10

    def test_signals_returns_list(self, client):
        mock_conn = MagicMock()
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value.fetchall.return_value = []
        with patch("data.database.get_conn", return_value=mock_conn):
            r = client.get("/signals", headers={"x-api-key": API_KEY})
        assert r.status_code == 200


# ── Close position ────────────────────────────────────────────────────────────

class TestCloseEndpoint:
    def test_close_queues_force_close(self, client):
        with patch("bot.api.set_state") as mock_set:
            # Symbols with '/' can't be embedded in URL paths; use underscored form
            r = client.post("/close/BTCUSDT", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert r.json()["queued"] is True
        mock_set.assert_called_once()

    def test_close_encodes_symbol_correctly(self, client):
        with patch("bot.api.set_state") as mock_set:
            r = client.post("/close/ETHUSDT", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        call_args = mock_set.call_args[0]
        assert "ETHUSDT" in call_args[0] or "ETH" in call_args[0]


# ── Pairs management ──────────────────────────────────────────────────────────

class TestPairsEndpoint:
    def test_get_pairs(self, client):
        with patch("bot.api.get_state", return_value=["BTC/USDT", "ETH/USDT"]):
            r = client.get("/pairs", headers={"x-api-key": API_KEY})
        assert r.status_code == 200
        assert "pairs" in r.json()

    def test_add_pair(self, client):
        current = ["BTC/USDT"]
        with patch("bot.api.get_state", return_value=current), \
             patch("bot.api.set_state") as mock_set:
            r = client.post(
                "/pairs",
                json={"action": "add", "pair": "SOL/USDT"},
                headers={"x-api-key": API_KEY},
            )
        assert r.status_code == 200
        saved = mock_set.call_args[0][1]
        assert "SOL/USDT" in saved

    def test_remove_pair(self, client):
        with patch("bot.api.get_state", return_value=["BTC/USDT", "ETH/USDT"]), \
             patch("bot.api.set_state") as mock_set:
            r = client.post(
                "/pairs",
                json={"action": "remove", "pair": "ETH/USDT"},
                headers={"x-api-key": API_KEY},
            )
        assert r.status_code == 200
        saved = mock_set.call_args[0][1]
        assert "ETH/USDT" not in saved

    def test_invalid_action_rejected(self, client):
        with patch("bot.api.get_state", return_value=[]):
            r = client.post(
                "/pairs",
                json={"action": "invalid", "pair": "BTC/USDT"},
                headers={"x-api-key": API_KEY},
            )
        assert r.status_code == 400

    def test_add_duplicate_pair_ignored(self, client):
        with patch("bot.api.get_state", return_value=["BTC/USDT"]), \
             patch("bot.api.set_state") as mock_set:
            r = client.post(
                "/pairs",
                json={"action": "add", "pair": "BTC/USDT"},
                headers={"x-api-key": API_KEY},
            )
        assert r.status_code == 200
        saved = mock_set.call_args[0][1]
        assert saved.count("BTC/USDT") == 1
