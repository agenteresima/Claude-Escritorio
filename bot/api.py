"""
FastAPI REST control API — manage the bot remotely without SSH.

Endpoints:
  GET  /status          — bot health, open positions, equity
  GET  /trades          — full trade history
  GET  /signals         — recent signal log
  POST /strategy        — switch active strategy on the fly
  POST /pause           — pause trading (closes nothing)
  POST /resume          — resume trading
  POST /close/{symbol}  — manually close a position
  GET  /metrics         — live performance metrics
  GET  /pairs           — configured pairs
  POST /pairs           — add / remove pairs

Run:  uvicorn bot.api:app --host 0.0.0.0 --port 8000
"""
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from config import CONFIG
from data.database import (
    get_open_trades, get_trade_history, trade_stats,
    get_equity_history, get_state, set_state,
)

app = FastAPI(
    title="Trading Bot API",
    description="Remote control & monitoring for the professional trading bot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("BOT_API_KEY", "changeme-set-BOT_API_KEY-env-var")


def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Models ─────────────────────────────────────────────────────────────────────

class StrategySwitch(BaseModel):
    strategy: str

class PairUpdate(BaseModel):
    action: str   # "add" | "remove"
    pair:   str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}


@app.get("/status", dependencies=[Depends(verify_key)])
def status():
    paused         = get_state("paused", False)
    active_strat   = get_state("active_strategy", CONFIG.active_strategy)
    open_positions = get_open_trades()
    stats          = trade_stats(active_strat)

    return {
        "paused":           paused,
        "active_strategy":  active_strat,
        "dry_run":          CONFIG.dry_run,
        "pairs":            CONFIG.pairs,
        "open_positions":   len(open_positions),
        "positions":        open_positions,
        "stats":            stats,
        "ts":               datetime.utcnow().isoformat(),
    }


@app.get("/trades", dependencies=[Depends(verify_key)])
def trades(symbol: Optional[str] = None, limit: int = 100):
    return get_trade_history(symbol=symbol, limit=limit)


@app.get("/equity", dependencies=[Depends(verify_key)])
def equity(strategy: Optional[str] = None, limit: int = 2000):
    strat = strategy or get_state("active_strategy", CONFIG.active_strategy)
    return get_equity_history(strat, limit=limit)


@app.get("/metrics", dependencies=[Depends(verify_key)])
def metrics(strategy: Optional[str] = None):
    strat = strategy or get_state("active_strategy", CONFIG.active_strategy)
    return trade_stats(strat)


@app.get("/signals", dependencies=[Depends(verify_key)])
def signals(limit: int = 50):
    from data.database import get_conn
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM signal_log ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/strategy", dependencies=[Depends(verify_key)])
def switch_strategy(body: StrategySwitch):
    from strategies import STRATEGIES
    if body.strategy not in STRATEGIES:
        raise HTTPException(400, f"Unknown strategy. Available: {list(STRATEGIES.keys())}")
    set_state("active_strategy", body.strategy)
    return {"ok": True, "strategy": body.strategy}


@app.post("/pause", dependencies=[Depends(verify_key)])
def pause():
    set_state("paused", True)
    return {"ok": True, "paused": True}


@app.post("/resume", dependencies=[Depends(verify_key)])
def resume():
    set_state("paused", False)
    return {"ok": True, "paused": False}


@app.post("/close/{symbol}", dependencies=[Depends(verify_key)])
def close_position(symbol: str):
    set_state(f"force_close_{symbol}", True)
    return {"ok": True, "symbol": symbol, "queued": True}


@app.get("/pairs", dependencies=[Depends(verify_key)])
def get_pairs():
    return {"pairs": get_state("pairs", CONFIG.pairs)}


@app.post("/pairs", dependencies=[Depends(verify_key)])
def update_pairs(body: PairUpdate):
    pairs = get_state("pairs", list(CONFIG.pairs))
    if body.action == "add":
        if body.pair not in pairs:
            pairs.append(body.pair)
    elif body.action == "remove":
        if body.pair in pairs:
            pairs.remove(body.pair)
    else:
        raise HTTPException(400, "action must be 'add' or 'remove'")
    set_state("pairs", pairs)
    return {"ok": True, "pairs": pairs}


@app.get("/strategies")
def list_strategies():
    from strategies import STRATEGIES
    return {"strategies": list(STRATEGIES.keys())}
