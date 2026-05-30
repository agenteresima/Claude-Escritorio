"""
TradingView webhook receiver — FastAPI endpoint that accepts
Pine Script alerts and converts them into bot trades.

TradingView alert message format (JSON):
  {
    "symbol":    "BTCUSDT",
    "action":    "buy" | "sell" | "close",
    "price":     {{close}},
    "strategy":  "my_pine_strategy",
    "timeframe": "1h",
    "secret":    "<WEBHOOK_SECRET>"
  }

Setup in TradingView:
  Alert → Webhook URL → http://your-vps:8001/webhook/tradingview
  Message → paste the JSON above (fill {{close}} etc with Pine vars)
"""
import os
import hmac
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from config import CONFIG
from data.database import log_signal, insert_trade, get_state
from bot.notifier import notify_trade_open

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me-in-env")

app = FastAPI(title="TradingView Webhook Receiver", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["POST"], allow_headers=["*"])

# ── Shared state injected by LiveTrader at startup ────────────────────────────
_live_trader = None

def set_live_trader(trader):
    global _live_trader
    _live_trader = trader


# ── Models ────────────────────────────────────────────────────────────────────

class TVAlert(BaseModel):
    symbol:    str
    action:    str            # buy | sell | close
    price:     float
    strategy:  Optional[str] = "tradingview"
    timeframe: Optional[str] = "1h"
    secret:    str
    stop_loss:   Optional[float] = None
    take_profit: Optional[float] = None
    size:        Optional[float] = None   # override risk manager if provided


# ── Helpers ──────────────────────────────────────────────────────────────────

def _normalise_symbol(raw: str) -> str:
    """BTCUSDT → BTC/USDT"""
    raw = raw.upper().replace("-", "").replace("/", "")
    for quote in ["USDT", "BUSD", "USD", "BTC", "ETH"]:
        if raw.endswith(quote) and raw != quote:
            return raw[:-len(quote)] + "/" + quote
    return raw


def _verify_secret(expected: str, provided: str) -> bool:
    if not provided:
        return False
    try:
        return hmac.compare_digest(expected, provided)
    except TypeError:
        return False


def _require_secret(provided: str) -> None:
    if not _verify_secret(WEBHOOK_SECRET, provided):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")


# ── Endpoint ─────────────────────────────────────────────────────────────────

@app.post("/webhook/tradingview")
async def tradingview_alert(alert: TVAlert, request: Request):
    _require_secret(alert.secret)

    symbol = _normalise_symbol(alert.symbol)
    action = alert.action.lower()

    logger.info(f"TradingView alert: {symbol} {action} @ {alert.price}")

    if get_state("paused", False):
        return {"ok": False, "reason": "bot paused"}

    # ── BUY ──────────────────────────────────────────────────────────────────
    if action in ("buy", "long"):
        if _live_trader and symbol not in _live_trader.pos_mgr.positions:
            from risk.manager import TradeSignal, RiskManager
            rm    = _live_trader.risk
            price = alert.price
            sl    = alert.stop_loss   or price * (1 - CONFIG.risk.hard_stop_pct)
            tp    = alert.take_profit or price * (1 + CONFIG.risk.take_profit_pct)

            sig = TradeSignal(symbol, "long", price, sl, tp)
            if rm.validate_signal(sig):
                atr  = price * 0.02   # fallback ATR estimate
                size = alert.size or rm.atr_size(price, atr)
                _live_trader.pos_mgr.open_position(symbol, "long", price, size, sl, sl, tp)
                insert_trade(symbol, "long", alert.strategy, price, size,
                             sl, tp, dry_run=CONFIG.dry_run)
                log_signal(symbol, alert.strategy, 1, price)
                notify_trade_open(symbol, "long", price, sl, tp, size, CONFIG.dry_run)
                return {"ok": True, "action": "opened_long", "symbol": symbol}
            return {"ok": False, "reason": "signal validation failed"}

    # ── SELL / CLOSE ─────────────────────────────────────────────────────────
    elif action in ("sell", "short", "close"):
        if _live_trader and symbol in _live_trader.pos_mgr.positions:
            _live_trader.pos_mgr._close(symbol, alert.price, "webhook_sell")
            log_signal(symbol, alert.strategy, -1, alert.price)
            return {"ok": True, "action": "closed", "symbol": symbol}

    return {"ok": True, "action": "no_position_change"}


@app.get("/webhook/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}
