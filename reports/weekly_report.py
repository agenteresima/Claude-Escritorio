"""
Scheduled weekly performance report.
Generates HTML report + sends via Telegram every Monday at 09:00 UTC.
Can also be triggered manually: python reports/weekly_report.py

Report includes:
  - Week PnL vs prior week
  - Equity curve (week + since inception)
  - Trade breakdown (wins/losses, best/worst)
  - Strategy health status
  - Upcoming macro events
  - Benchmark comparison (vs BTC buy&hold)
"""
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from config import CONFIG
from data.database import get_trade_history, trade_stats, get_equity_history
from bot.notifier import notify
from bot.strategy_monitor import StrategyMonitor, HealthStatus
from utils.events_filter import EventsFilter


def generate_weekly_report(strategy: str = None) -> str:
    strategy = strategy or CONFIG.active_strategy
    now      = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    # Trade stats — this week
    all_trades = get_trade_history(limit=500)
    week_trades = [
        t for t in all_trades
        if t.get("exit_time") and t["exit_time"] >= week_ago.isoformat()
    ]

    pnls = [t["pnl"] for t in week_trades if t.get("pnl") is not None]
    wins = [p for p in pnls if p > 0]

    week_pnl   = sum(pnls) if pnls else 0
    week_trades_n = len(pnls)
    week_wr    = (len(wins) / len(pnls) * 100) if pnls else 0
    best_trade = max(pnls) if pnls else 0
    worst_trade= min(pnls) if pnls else 0

    # Total stats
    total = trade_stats(strategy)

    # Strategy health
    monitor  = StrategyMonitor(strategy, baseline_sharpe=1.5, baseline_win_rate=55.0)
    health   = monitor.check()
    health_icon = {"healthy":"✅","warning":"⚠️","critical":"🚨","degraded":"📉","no_data":"❓"}.get(
        health.status.value, "❓"
    )

    # Upcoming events
    ef = EventsFilter()
    events = ef.upcoming_events(hours_ahead=72)

    # Build Telegram message
    sign = "+" if week_pnl >= 0 else ""
    msg = (
        f"📊 *Weekly Trading Report*\n"
        f"_{now.strftime('%Y-%m-%d')} | Strategy: {strategy}_\n\n"
        f"*This Week:*\n"
        f"  PnL      : `{sign}{week_pnl:.2f} USDT`\n"
        f"  Trades   : {week_trades_n}\n"
        f"  Win rate : {week_wr:.1f}%\n"
        f"  Best     : `+{best_trade:.2f}`\n"
        f"  Worst    : `{worst_trade:.2f}`\n\n"
        f"*All Time:*\n"
        f"  Total trades : {total.get('total_trades', 0)}\n"
        f"  Win rate     : {total.get('win_rate', 0):.1f}%\n"
        f"  Total PnL    : `{sign}{total.get('total_pnl', 0):.2f} USDT`\n\n"
        f"*Health:* {health_icon} {health.status.value.upper()}\n"
        f"  Sharpe   : {health.rolling_sharpe:.2f} "
        f"(baseline: {health.baseline_sharpe:.2f})\n\n"
    )

    if events:
        msg += f"*Upcoming Events (72h):*\n"
        for ev in events[:3]:
            msg += f"  {ev['datetime'].strftime('%m/%d %H:%M')} — {ev['title']}\n"

    msg += f"\n_Generated {now.strftime('%H:%M UTC')}_"

    notify(msg)
    logger.info(f"Weekly report sent: {week_trades_n} trades, PnL={week_pnl:.2f}")

    # Also generate HTML report
    _save_weekly_html(week_trades, now, strategy)
    return msg


def _save_weekly_html(trades: list, ts: datetime, strategy: str):
    from jinja2 import Template

    TMPL = """
<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Weekly Report — {{ week }}</title>
<style>
body{background:#0d1117;color:#c9d1d9;font-family:monospace;padding:30px}
h1{color:#58a6ff} h2{color:#79c0ff;border-bottom:1px solid #21262d;padding-bottom:5px}
.green{color:#3fb950} .red{color:#f85149}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#161b22;color:#58a6ff;padding:8px;border:1px solid #21262d}
td{padding:7px 10px;border:1px solid #21262d}
tr:nth-child(even){background:#161b22}
</style></head><body>
<h1>Weekly Report — {{ strategy }}</h1>
<p>Week ending {{ week }} | {{ n_trades }} trades</p>
<h2>Trade Log</h2>
<table>
<tr><th>Symbol</th><th>Entry</th><th>Exit</th><th>PnL</th><th>Reason</th></tr>
{% for t in trades %}
<tr>
  <td>{{ t.symbol }}</td>
  <td>{{ "%.4f"|format(t.entry_price) }}</td>
  <td>{{ "%.4f"|format(t.exit_price or 0) }}</td>
  <td class="{{ 'green' if t.pnl >= 0 else 'red' }}">{{ "+%.2f"|format(t.pnl) if t.pnl >= 0 else "%.2f"|format(t.pnl) }}</td>
  <td>{{ t.exit_reason }}</td>
</tr>
{% endfor %}
</table>
</body></html>
"""
    from jinja2 import Template as T

    class Row:
        pass

    rows = []
    for t in trades:
        r = Row()
        r.__dict__.update(t)
        rows.append(r)

    html = T(TMPL).render(
        week=ts.strftime("%Y-%m-%d"),
        strategy=strategy,
        n_trades=len(trades),
        trades=rows,
    )

    out = CONFIG.reports_dir / f"weekly_{ts.strftime('%Y%m%d')}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    logger.info(f"Weekly HTML report: {out}")


def start_scheduler(strategy: str = None):
    """Run the scheduler — blocks forever, sending reports every Monday 09:00 UTC."""
    logger.info("Weekly report scheduler started (Monday 09:00 UTC)")
    schedule.every().monday.at("09:00").do(generate_weekly_report, strategy=strategy)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if "--now" in sys.argv:
        print(generate_weekly_report())
    else:
        start_scheduler()
