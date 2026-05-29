"""
SQLite persistence layer — trades, equity snapshots, bot state, ML model metadata.
Uses only stdlib sqlite3 so no extra dependency needed.
"""
import sqlite3
import json
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from config import CONFIG

DB_PATH = CONFIG.data_dir / "bot.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol        TEXT    NOT NULL,
    direction     TEXT    NOT NULL,
    strategy      TEXT    NOT NULL,
    entry_price   REAL    NOT NULL,
    exit_price    REAL,
    size          REAL    NOT NULL,
    stop_loss     REAL,
    take_profit   REAL,
    pnl           REAL,
    pnl_pct       REAL,
    exit_reason   TEXT,
    entry_time    TEXT    NOT NULL,
    exit_time     TEXT,
    bars_held     INTEGER,
    is_open       INTEGER NOT NULL DEFAULT 1,
    dry_run       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS equity_snapshots (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT    NOT NULL,
    strategy  TEXT    NOT NULL,
    equity    REAL    NOT NULL,
    drawdown  REAL
);

CREATE TABLE IF NOT EXISTS bot_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT    NOT NULL,
    symbol    TEXT    NOT NULL,
    strategy  TEXT    NOT NULL,
    signal    INTEGER NOT NULL,
    price     REAL    NOT NULL,
    confidence REAL
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol   ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_open     ON trades(is_open);
CREATE INDEX IF NOT EXISTS idx_equity_ts       ON equity_snapshots(ts);
CREATE INDEX IF NOT EXISTS idx_signal_symbol   ON signal_log(symbol);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
    logger.info(f"Database ready: {DB_PATH}")


# ── Trades ─────────────────────────────────────────────────────────────────────

def insert_trade(symbol: str, direction: str, strategy: str,
                 entry_price: float, size: float,
                 stop_loss: float, take_profit: float,
                 dry_run: bool = True) -> int:
    sql = """INSERT INTO trades
             (symbol, direction, strategy, entry_price, size, stop_loss, take_profit,
              entry_time, dry_run)
             VALUES (?,?,?,?,?,?,?,?,?)"""
    with get_conn() as conn:
        cur = conn.execute(sql, (
            symbol, direction, strategy, entry_price, size,
            stop_loss, take_profit,
            datetime.utcnow().isoformat(), int(dry_run),
        ))
        return cur.lastrowid


def close_trade(trade_id: int, exit_price: float, pnl: float, pnl_pct: float,
                exit_reason: str, bars_held: int):
    sql = """UPDATE trades SET
               exit_price=?, pnl=?, pnl_pct=?, exit_reason=?,
               exit_time=?, bars_held=?, is_open=0
             WHERE id=?"""
    with get_conn() as conn:
        conn.execute(sql, (
            exit_price, pnl, pnl_pct, exit_reason,
            datetime.utcnow().isoformat(), bars_held, trade_id,
        ))


def get_open_trades() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM trades WHERE is_open=1").fetchall()
    return [dict(r) for r in rows]


def get_trade_history(symbol: Optional[str] = None, limit: int = 200) -> list[dict]:
    sql = "SELECT * FROM trades WHERE is_open=0"
    params: list = []
    if symbol:
        sql += " AND symbol=?"
        params.append(symbol)
    sql += " ORDER BY exit_time DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


# ── Equity snapshots ───────────────────────────────────────────────────────────

def save_equity(strategy: str, equity: float, drawdown: float = 0.0):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO equity_snapshots (ts, strategy, equity, drawdown) VALUES (?,?,?,?)",
            (datetime.utcnow().isoformat(), strategy, equity, drawdown),
        )


def get_equity_history(strategy: str, limit: int = 5000) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT ts, equity, drawdown FROM equity_snapshots WHERE strategy=? ORDER BY ts DESC LIMIT ?",
            (strategy, limit),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Bot state (survives restarts) ─────────────────────────────────────────────

def set_state(key: str, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO bot_state (key, value, updated_at) VALUES (?,?,?)",
            (key, json.dumps(value), datetime.utcnow().isoformat()),
        )


def get_state(key: str, default=None):
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM bot_state WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


# ── Signal log ─────────────────────────────────────────────────────────────────

def log_signal(symbol: str, strategy: str, signal: int,
               price: float, confidence: Optional[float] = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO signal_log (ts, symbol, strategy, signal, price, confidence) VALUES (?,?,?,?,?,?)",
            (datetime.utcnow().isoformat(), symbol, strategy, signal, price, confidence),
        )


# ── Stats helpers ──────────────────────────────────────────────────────────────

def trade_stats(strategy: Optional[str] = None) -> dict:
    sql = "SELECT * FROM trades WHERE is_open=0"
    params: list = []
    if strategy:
        sql += " AND strategy=?"
        params.append(strategy)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    if not rows:
        return {}

    pnls = [r["pnl"] for r in rows if r["pnl"] is not None]
    wins = [p for p in pnls if p > 0]

    return {
        "total_trades": len(pnls),
        "win_rate":     len(wins) / len(pnls) * 100 if pnls else 0,
        "total_pnl":    sum(pnls),
        "avg_pnl":      sum(pnls) / len(pnls) if pnls else 0,
        "best_trade":   max(pnls) if pnls else 0,
        "worst_trade":  min(pnls) if pnls else 0,
    }


# Initialise on import
init_db()
