"""
Database backup and restore.
- Daily automatic backup to data/backups/
- Keeps last 30 backups
- Restore from any backup file
- Export trades to CSV/Excel for external analysis
"""
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger
import pandas as pd

from config import CONFIG

BACKUP_DIR = CONFIG.data_dir / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = CONFIG.data_dir / "bot.db"


def backup(tag: str = "") -> Path:
    """Copy the live database to a timestamped backup file."""
    if not DB_PATH.exists():
        logger.warning("No database to backup yet.")
        return Path()

    ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = f"bot_{ts}{'_' + tag if tag else ''}.db"
    dest = BACKUP_DIR / name
    shutil.copy2(DB_PATH, dest)
    logger.info(f"Backup created: {dest}")

    # Prune old backups — keep last 30
    backups = sorted(BACKUP_DIR.glob("bot_*.db"))
    for old in backups[:-30]:
        old.unlink()
        logger.debug(f"Pruned old backup: {old.name}")

    return dest


def restore(backup_path: Path):
    """Restore database from a backup. Creates a safety backup of current DB first."""
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    # Safety backup of current state
    if DB_PATH.exists():
        backup(tag="pre_restore")

    shutil.copy2(backup_path, DB_PATH)
    logger.info(f"Database restored from: {backup_path}")


def list_backups() -> list[dict]:
    backups = sorted(BACKUP_DIR.glob("bot_*.db"), reverse=True)
    result  = []
    for b in backups:
        stat = b.stat()
        result.append({
            "file":     b.name,
            "path":     str(b),
            "size_kb":  round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return result


# ── Export helpers ────────────────────────────────────────────────────────────

def export_trades_csv(output_path: Optional[Path] = None) -> Path:
    from data.database import get_conn
    output_path = output_path or (CONFIG.reports_dir / f"trades_{datetime.utcnow().strftime('%Y%m%d')}.csv")
    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM trades ORDER BY entry_time DESC", conn)
    df.to_csv(output_path, index=False)
    logger.info(f"Trades exported to: {output_path}")
    return output_path


def export_trades_excel(output_path: Optional[Path] = None) -> Path:
    from data.database import get_conn
    output_path = output_path or (CONFIG.reports_dir / f"trades_{datetime.utcnow().strftime('%Y%m%d')}.xlsx")
    with get_conn() as conn:
        trades  = pd.read_sql("SELECT * FROM trades ORDER BY entry_time DESC", conn)
        equity  = pd.read_sql("SELECT * FROM equity_snapshots ORDER BY ts", conn)
        signals = pd.read_sql("SELECT * FROM signal_log ORDER BY ts DESC LIMIT 1000", conn)

    with pd.ExcelWriter(str(output_path), engine="openpyxl") as writer:
        trades.to_excel(writer,  sheet_name="Trades",   index=False)
        equity.to_excel(writer,  sheet_name="Equity",   index=False)
        signals.to_excel(writer, sheet_name="Signals",  index=False)

    logger.info(f"Excel export: {output_path}")
    return output_path
