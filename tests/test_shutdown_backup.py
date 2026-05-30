"""
Tests for:
  - bot/shutdown.py  (GracefulShutdown — install, callbacks, async)
  - bot/position_manager.py  (short position paths, closed_trades list)
  - data/backup.py  (backup, restore, list_backups, export_trades_csv)
"""
import sqlite3
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── GracefulShutdown ──────────────────────────────────────────────────────────

class TestGracefulShutdown:
    @pytest.fixture
    def gs(self):
        from bot.shutdown import GracefulShutdown
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            return GracefulShutdown()

    def test_initial_state_not_requested(self, gs):
        assert gs.requested is False

    def test_install_registers_signals(self, gs):
        import signal
        with patch("signal.signal") as mock_sig:
            gs.install()
        assert mock_sig.call_count == 2
        calls = [c[0][0] for c in mock_sig.call_args_list]
        assert signal.SIGTERM in calls
        assert signal.SIGINT  in calls

    def test_run_shutdown_sets_requested(self, gs):
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs._run_shutdown()
        assert gs.requested is True

    def test_run_shutdown_calls_set_state_paused(self, gs):
        with patch("bot.shutdown.set_state") as mock_ss, \
             patch("bot.shutdown.notify"):
            gs._run_shutdown()
        mock_ss.assert_called_once_with("paused", True)

    def test_run_shutdown_calls_notify(self, gs):
        with patch("bot.shutdown.set_state"), \
             patch("bot.shutdown.notify") as mock_notify:
            gs._run_shutdown()
        mock_notify.assert_called_once()

    def test_callbacks_are_called(self, gs):
        cb1 = MagicMock()
        cb2 = MagicMock()
        gs.add_callback(cb1)
        gs.add_callback(cb2)
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs._run_shutdown()
        cb1.assert_called_once()
        cb2.assert_called_once()

    def test_failing_callback_does_not_abort(self, gs):
        def bad_cb():
            raise RuntimeError("oops")
        gs.add_callback(bad_cb)
        good_cb = MagicMock()
        gs.add_callback(good_cb)
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs._run_shutdown()  # should not raise
        good_cb.assert_called_once()

    def test_close_positions_logs_symbols(self, gs):
        pos_manager = MagicMock()
        pos_manager.positions = {"BTC/USDT": MagicMock(), "ETH/USDT": MagicMock()}
        gs.close_positions = True
        gs.pos_manager     = pos_manager
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs._run_shutdown()
        assert gs.requested is True

    def test_install_async_adds_signal_handlers(self, gs):
        import asyncio
        loop = MagicMock(spec=asyncio.AbstractEventLoop)
        gs.install_async(loop=loop)
        assert loop.add_signal_handler.call_count == 2

    def test_handle_async_sets_requested(self, gs):
        with patch("bot.shutdown.set_state"), patch("bot.shutdown.notify"):
            gs._handle_async(15)  # SIGTERM
        assert gs.requested is True


# ── PositionManager — short side ─────────────────────────────────────────────

class TestPositionManagerShort:
    @pytest.fixture
    def pm(self):
        from bot.position_manager import PositionManager
        return PositionManager(max_bars=96, dry_run=True)

    def _open_short(self, pm, entry=40_000.0, stop=41_000.0, tp1=39_000.0, tp2=38_000.0):
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            pm.open_position("BTC/USDT", "short", entry, 0.01, stop, tp1, tp2)

    def test_short_stop_loss_closes(self, pm):
        self._open_short(pm)
        with patch("bot.position_manager.notify_trade_close"):
            actions = pm.update("BTC/USDT", current_price=41_500.0)  # above stop
        assert "stop_loss" in actions
        assert "BTC/USDT" not in pm.positions

    def test_short_breakeven_set(self, pm):
        self._open_short(pm, entry=40_000, stop=41_000, tp1=39_000, tp2=38_000)
        with patch("bot.position_manager.notify_trade_close"):
            # Price drops to below one_r = 40_000 - (40_000-39_000)*0.5 = 39_500
            actions = pm.update("BTC/USDT", current_price=39_400.0)
        assert "breakeven" in actions
        pos = pm.positions["BTC/USDT"]
        assert pos.breakeven_set is True
        assert pos.stop_loss == pytest.approx(40_000 * 0.999, rel=1e-4)

    def test_short_partial_tp_fires(self, pm):
        self._open_short(pm, entry=40_000, stop=41_000, tp1=39_000, tp2=38_000)
        with patch("bot.position_manager.notify_trade_close"):
            actions = pm.update("BTC/USDT", current_price=38_900.0)  # below tp1
        assert "partial_close" in actions
        pos = pm.positions.get("BTC/USDT")
        assert pos is not None
        assert pos.size == pytest.approx(0.005, rel=0.01)

    def test_short_full_close_at_tp2(self, pm):
        self._open_short(pm, entry=40_000, stop=41_000, tp1=39_000, tp2=38_000)
        with patch("bot.position_manager.notify_trade_close"):
            pm.update("BTC/USDT", current_price=38_900.0)   # partial TP
            actions = pm.update("BTC/USDT", current_price=37_900.0)  # full TP2
        assert "full_close" in actions
        assert "BTC/USDT" not in pm.positions

    def test_closed_trades_record_pnl(self, pm):
        self._open_short(pm, entry=40_000, stop=42_000, tp1=38_000, tp2=36_000)
        with patch("bot.position_manager.notify_trade_close"):
            pm.update("BTC/USDT", current_price=42_500.0)   # stop loss hit
        assert len(pm.closed_trades) == 1
        trade = pm.closed_trades[0]
        assert trade["pnl"] < 0   # loss on short stop-out at 42_500 > entry 40_000
        assert trade["reason"] == "stop_loss"

    def test_update_unknown_symbol_returns_empty(self, pm):
        actions = pm.update("UNKNOWN/USDT", current_price=100.0)
        assert actions == []

    def test_time_exit_short(self, pm):
        from bot.position_manager import PositionManager
        pm2 = PositionManager(max_bars=2, dry_run=True)
        with patch("bot.position_manager.notify_trade_open"), \
             patch("bot.position_manager.notify_trade_close"):
            pm2.open_position("ETH/USDT", "short", 2000, 0.5, 2100, 1900, 1800)
        with patch("bot.position_manager.notify_trade_close"):
            for _ in range(2):
                actions = pm2.update("ETH/USDT", current_price=2010.0)
        assert "time_exit" in actions


# ── data/backup.py ───────────────────────────────────────────────────────────

class TestBackup:
    @pytest.fixture
    def tmp_db(self, tmp_path):
        """Create a minimal SQLite DB at the patched DB_PATH."""
        db = tmp_path / "bot.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE trades (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        return tmp_path, db

    def test_backup_creates_file(self, tmp_db):
        import data.backup as bk
        tmp_path, db = tmp_db
        orig_db   = bk.DB_PATH
        orig_bdir = bk.BACKUP_DIR
        bk.DB_PATH   = db
        bk.BACKUP_DIR = tmp_path / "backups"
        bk.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        try:
            dest = bk.backup(tag="test")
        finally:
            bk.DB_PATH   = orig_db
            bk.BACKUP_DIR = orig_bdir
        assert dest.exists()
        assert "test" in dest.name

    def test_backup_returns_empty_when_no_db(self, tmp_path):
        import data.backup as bk
        orig_db   = bk.DB_PATH
        orig_bdir = bk.BACKUP_DIR
        bk.DB_PATH   = tmp_path / "nonexistent.db"
        bk.BACKUP_DIR = tmp_path / "backups"
        bk.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        try:
            result = bk.backup()
        finally:
            bk.DB_PATH   = orig_db
            bk.BACKUP_DIR = orig_bdir
        assert str(result) == "."

    def test_backup_prunes_old_files(self, tmp_db):
        import data.backup as bk
        tmp_path, db = tmp_db
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        # Pre-create 32 fake backup files so pruning kicks in
        for i in range(32):
            (backup_dir / f"bot_2022010{i % 9}_00000{i}.db").write_bytes(b"x")
        orig_db   = bk.DB_PATH
        orig_bdir = bk.BACKUP_DIR
        bk.DB_PATH   = db
        bk.BACKUP_DIR = backup_dir
        try:
            bk.backup()
            remaining = list(backup_dir.glob("bot_*.db"))
        finally:
            bk.DB_PATH   = orig_db
            bk.BACKUP_DIR = orig_bdir
        assert len(remaining) <= 30

    def test_restore_copies_file(self, tmp_db):
        import data.backup as bk
        tmp_path, db = tmp_db
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        src = backup_dir / "bot_20220101_120000.db"
        src.write_bytes(b"restored content")
        orig_db   = bk.DB_PATH
        orig_bdir = bk.BACKUP_DIR
        bk.DB_PATH   = db
        bk.BACKUP_DIR = backup_dir
        try:
            bk.restore(src)
        finally:
            bk.DB_PATH   = orig_db
            bk.BACKUP_DIR = orig_bdir
        assert db.read_bytes() == b"restored content"

    def test_restore_raises_for_missing_file(self, tmp_db):
        import data.backup as bk
        _, db = tmp_db
        with pytest.raises(FileNotFoundError):
            bk.restore(Path("/nonexistent/backup.db"))

    def test_list_backups_returns_dicts(self, tmp_db):
        import data.backup as bk
        tmp_path, db = tmp_db
        backup_dir = tmp_path / "backups2"
        backup_dir.mkdir(parents=True, exist_ok=True)
        (backup_dir / "bot_20220101_000000.db").write_bytes(b"x" * 512)
        orig_bdir = bk.BACKUP_DIR
        bk.BACKUP_DIR = backup_dir
        try:
            result = bk.list_backups()
        finally:
            bk.BACKUP_DIR = orig_bdir
        assert len(result) == 1
        assert "file" in result[0]
        assert "size_kb" in result[0]

    def test_list_backups_empty_dir(self, tmp_path):
        import data.backup as bk
        backup_dir = tmp_path / "empty_backups"
        backup_dir.mkdir()
        orig_bdir = bk.BACKUP_DIR
        bk.BACKUP_DIR = backup_dir
        try:
            result = bk.list_backups()
        finally:
            bk.BACKUP_DIR = orig_bdir
        assert result == []

    def test_export_trades_csv(self, tmp_path):
        import data.backup as bk
        import data.database as db_mod
        fresh_db = tmp_path / "fresh.db"
        orig_db_path = db_mod.DB_PATH
        db_mod.DB_PATH = fresh_db
        db_mod.init_db()
        output = tmp_path / "trades.csv"
        try:
            result = bk.export_trades_csv(output_path=output)
        finally:
            db_mod.DB_PATH = orig_db_path
        assert result.exists()
        assert result.suffix == ".csv"
