"""
Tests for SQLite persistence layer.
Uses a separate in-memory database path per test session.
"""
import pytest
from pathlib import Path
import tempfile
import os


@pytest.fixture(autouse=True)
def patch_db_path(monkeypatch, tmp_path):
    """Redirect database to a temp file so tests don't pollute real DB."""
    test_db = tmp_path / "test_bot.db"
    monkeypatch.setattr("data.database.DB_PATH", test_db)
    # Re-init schema on temp path
    import data.database as db_mod
    db_mod.DB_PATH = test_db
    db_mod.init_db()
    yield
    if test_db.exists():
        os.unlink(test_db)


class TestTrades:
    def test_insert_and_retrieve_open_trade(self):
        from data.database import insert_trade, get_open_trades
        tid = insert_trade("BTC/USDT", "long", "trend_ema",
                           30_000, 0.1, 29_000, 32_000, dry_run=True)
        assert tid > 0
        open_ = get_open_trades()
        assert any(t["id"] == tid for t in open_)

    def test_close_trade(self):
        from data.database import insert_trade, close_trade, get_trade_history, get_open_trades
        tid = insert_trade("ETH/USDT", "long", "ensemble",
                           2_000, 1.0, 1_900, 2_200, dry_run=True)
        close_trade(tid, 2_100, 100.0, 0.05, "take_profit", 12)
        history = get_trade_history()
        closed  = [t for t in history if t["id"] == tid]
        assert len(closed) == 1
        assert closed[0]["exit_reason"] == "take_profit"
        assert closed[0]["is_open"] == 0
        # Should no longer appear in open trades
        assert not any(t["id"] == tid for t in get_open_trades())


class TestBotState:
    def test_set_and_get_state(self):
        from data.database import set_state, get_state
        set_state("test_key", {"foo": "bar", "num": 42})
        val = get_state("test_key")
        assert val == {"foo": "bar", "num": 42}

    def test_default_returned_for_missing_key(self):
        from data.database import get_state
        val = get_state("nonexistent_key", default="fallback")
        assert val == "fallback"

    def test_overwrite_state(self):
        from data.database import set_state, get_state
        set_state("strategy", "trend_ema")
        set_state("strategy", "ensemble")
        assert get_state("strategy") == "ensemble"


class TestEquitySnapshots:
    def test_save_and_load(self):
        from data.database import save_equity, get_equity_history
        save_equity("trend_ema", 10_500.0, -0.02)
        save_equity("trend_ema", 10_800.0, -0.01)
        history = get_equity_history("trend_ema")
        assert len(history) == 2
        assert any(abs(h["equity"] - 10_500.0) < 0.01 for h in history)


class TestTradeStats:
    def test_stats_with_mixed_pnl(self):
        from data.database import insert_trade, close_trade, trade_stats
        # Win
        t1 = insert_trade("BTC/USDT", "long", "test", 30_000, 0.1, 29_000, 32_000)
        close_trade(t1, 31_500, 150.0, 0.05, "take_profit", 10)
        # Loss
        t2 = insert_trade("ETH/USDT", "long", "test", 2_000, 0.5, 1_900, 2_200)
        close_trade(t2, 1_950, -25.0, -0.025, "stop_loss", 5)

        stats = trade_stats()
        assert stats["total_trades"] == 2
        assert 45 <= stats["win_rate"] <= 55   # 1 win, 1 loss → 50 %
        assert stats["total_pnl"] == pytest.approx(125.0)
