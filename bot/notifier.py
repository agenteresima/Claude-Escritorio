"""
Notification system — Telegram alerts for trade events.
Gracefully skips if credentials are not configured.
"""
import os
import asyncio
from datetime import datetime
from loguru import logger
import aiohttp


TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


async def _send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status != 200:
                    logger.warning(f"Telegram send failed: {r.status}")
    except Exception as e:
        logger.debug(f"Telegram error (non-critical): {e}")


def notify(text: str):
    """Fire-and-forget notification (sync wrapper)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_send_telegram(text))
        else:
            loop.run_until_complete(_send_telegram(text))
    except Exception:
        pass


def notify_trade_open(symbol: str, direction: str, entry: float,
                      stop: float, target: float, size: float, dry_run: bool):
    mode = "📋 DRY RUN" if dry_run else "🟢 LIVE"
    msg = (
        f"{mode} — <b>TRADE OPEN</b>\n"
        f"Pair      : <code>{symbol}</code>\n"
        f"Direction : {direction.upper()}\n"
        f"Entry     : <b>{entry:.4f}</b>\n"
        f"Stop Loss : <b>{stop:.4f}</b>  ({abs(entry-stop)/entry*100:.2f}%)\n"
        f"Target    : <b>{target:.4f}</b>  (+{abs(target-entry)/entry*100:.2f}%)\n"
        f"Size      : {size:.4f}\n"
        f"Time      : {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    notify(msg)
    logger.info(f"[NOTIFY] Trade open: {symbol} {direction} @ {entry:.4f}")


def notify_trade_close(symbol: str, entry: float, exit_price: float,
                       pnl: float, pnl_pct: float, reason: str):
    icon  = "✅" if pnl >= 0 else "🔴"
    msg = (
        f"{icon} — <b>TRADE CLOSED</b>\n"
        f"Pair    : <code>{symbol}</code>\n"
        f"Entry   : {entry:.4f}  →  Exit: {exit_price:.4f}\n"
        f"PnL     : <b>{pnl:+.2f} USDT</b>  ({pnl_pct*100:+.2f}%)\n"
        f"Reason  : {reason}\n"
        f"Time    : {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    notify(msg)
    logger.info(f"[NOTIFY] Trade close: {symbol} PnL={pnl:+.2f} ({reason})")


def notify_drawdown_alert(current_dd_pct: float, capital: float):
    msg = (
        f"⚠️ <b>DRAWDOWN ALERT</b>\n"
        f"Current DD : <b>{current_dd_pct*100:.2f}%</b>\n"
        f"Capital    : {capital:.2f} USDT\n"
        f"Time       : {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    notify(msg)
    logger.warning(f"[NOTIFY] Drawdown alert: {current_dd_pct*100:.2f}%")


def notify_startup(strategy: str, pairs: list[str], dry_run: bool):
    mode = "DRY RUN" if dry_run else "⚠️ LIVE TRADING"
    msg = (
        f"🤖 <b>Trading Bot Started</b> [{mode}]\n"
        f"Strategy  : {strategy}\n"
        f"Pairs     : {', '.join(pairs)}\n"
        f"Time      : {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    notify(msg)
