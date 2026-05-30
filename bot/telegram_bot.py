"""
Telegram bot — control the trading bot via chat commands.
No extra library needed beyond python-telegram-bot (added to requirements).

Commands:
  /status    — open positions, equity, drawdown
  /pause     — pause trading
  /resume    — resume trading
  /stats     — trade statistics
  /close BTC/USDT — force close a position
  /strategy regime_adaptive — switch strategy
  /events    — upcoming macro events
  /help      — list commands

Run:  python bot/telegram_bot.py
Or start automatically via docker-compose.
"""
import os
import asyncio
from datetime import datetime
from loguru import logger

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_IDS = set(
    int(x) for x in os.getenv("TELEGRAM_CHAT_ID", "").split(",") if x.strip().isdigit()
)


def _auth(chat_id: int) -> bool:
    if not ALLOWED_CHAT_IDS:
        return True   # no restriction if not configured
    return chat_id in ALLOWED_CHAT_IDS


async def run_bot():
    if not TELEGRAM_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
        return

    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
    except ImportError:
        logger.warning("python-telegram-bot not installed. Run: pip install python-telegram-bot")
        return

    from data.database import get_open_trades, trade_stats, get_state, set_state
    from utils.events_filter import EventsFilter

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ── Handlers ─────────────────────────────────────────────────────────────

    async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        open_  = get_open_trades()
        paused = get_state("paused", False)
        strat  = get_state("active_strategy", "—")
        lines  = [
            f"📊 *Bot Status*",
            f"Strategy : `{strat}`",
            f"Paused   : {'⏸ YES' if paused else '▶ NO'}",
            f"Open pos : {len(open_)}",
        ]
        for p in open_:
            lines.append(f"  • `{p['symbol']}` {p['direction']} @ {p['entry_price']:.4f}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        set_state("paused", True)
        await update.message.reply_text("⏸ Trading *paused*.", parse_mode="Markdown")

    async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        set_state("paused", False)
        await update.message.reply_text("▶ Trading *resumed*.", parse_mode="Markdown")

    async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        s = trade_stats()
        if not s:
            await update.message.reply_text("No closed trades yet.")
            return
        sign = "+" if s["total_pnl"] >= 0 else ""
        msg = (
            f"📈 *Trade Stats*\n"
            f"Trades    : {s['total_trades']}\n"
            f"Win rate  : {s['win_rate']:.1f}%\n"
            f"Total PnL : `{sign}{s['total_pnl']:.2f} USDT`\n"
            f"Avg trade : `{s['avg_pnl']:+.2f}`\n"
            f"Best      : `+{s['best_trade']:.2f}`\n"
            f"Worst     : `{s['worst_trade']:.2f}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_close(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        if not ctx.args:
            await update.message.reply_text("Usage: /close BTC/USDT")
            return
        symbol = ctx.args[0].upper()
        set_state(f"force_close_{symbol}", True)
        await update.message.reply_text(f"🔴 Force-close queued for `{symbol}`", parse_mode="Markdown")

    async def cmd_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        from strategies import STRATEGIES
        if not ctx.args:
            current = get_state("active_strategy", "—")
            options = ", ".join(STRATEGIES.keys())
            await update.message.reply_text(
                f"Current: `{current}`\nAvailable: `{options}`\n"
                f"Switch: /strategy regime_adaptive", parse_mode="Markdown"
            )
            return
        new = ctx.args[0].lower()
        if new not in STRATEGIES:
            await update.message.reply_text(f"Unknown strategy: `{new}`", parse_mode="Markdown")
            return
        set_state("active_strategy", new)
        await update.message.reply_text(f"✅ Strategy switched to `{new}`", parse_mode="Markdown")

    async def cmd_events(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not _auth(update.effective_chat.id): return
        ef   = EventsFilter()
        safe, reason = ef.is_safe_to_trade()
        lines = [f"🗓 *Macro Events*"]
        lines.append(f"Status: {'✅ Safe' if safe else f'🚫 {reason}'}")
        upcoming = ef.upcoming_events(48)
        if upcoming:
            lines.append("*Next 48h:*")
            for ev in upcoming[:5]:
                lines.append(f"  {ev['datetime'].strftime('%m/%d %H:%M')} — {ev['title']}")
        else:
            lines.append("No high-impact events in 48h.")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        msg = (
            "🤖 *Trading Bot Commands*\n\n"
            "/status   — open positions & bot state\n"
            "/pause    — pause trading\n"
            "/resume   — resume trading\n"
            "/stats    — trade statistics\n"
            "/close PAIR — force close a position\n"
            "/strategy [name] — show/switch strategy\n"
            "/events   — upcoming macro events\n"
            "/help     — this message"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # ── Register & run ────────────────────────────────────────────────────────
    for name, handler in [
        ("status",   cmd_status),
        ("pause",    cmd_pause),
        ("resume",   cmd_resume),
        ("stats",    cmd_stats),
        ("close",    cmd_close),
        ("strategy", cmd_strategy),
        ("events",   cmd_events),
        ("help",     cmd_help),
        ("start",    cmd_help),
    ]:
        app.add_handler(CommandHandler(name, handler))

    logger.info("Telegram bot started — polling for commands...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run_bot())
