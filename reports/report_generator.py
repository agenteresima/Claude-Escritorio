"""
Full HTML + PDF report generator for backtest results.
Produces a professional report like QuantConnect's backtest output.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from jinja2 import Template
from loguru import logger

from config import CONFIG


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Trading Bot Backtest Report</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', monospace; padding: 30px; }
  h1   { color: #58a6ff; margin-bottom: 5px; font-size: 28px; }
  h2   { color: #79c0ff; margin: 25px 0 10px; font-size: 18px; border-bottom: 1px solid #21262d; padding-bottom: 5px; }
  .subtitle { color: #8b949e; margin-bottom: 30px; font-size: 14px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }
  .kpi-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center; }
  .kpi-label { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
  .kpi-value { font-size: 22px; font-weight: bold; margin-top: 5px; }
  .green  { color: #3fb950; }
  .red    { color: #f85149; }
  .blue   { color: #58a6ff; }
  .purple { color: #d2a8ff; }
  .orange { color: #ffa657; }
  table  { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
  th     { background: #161b22; color: #58a6ff; padding: 10px; text-align: left; border: 1px solid #21262d; }
  td     { padding: 8px 10px; border: 1px solid #21262d; }
  tr:nth-child(even) { background: #161b22; }
  tr:hover { background: #1f2937; }
  .chart-container { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
                     padding: 10px; margin-bottom: 20px; }
  .footer { text-align: center; color: #484f58; margin-top: 40px; font-size: 11px; }
  .badge-good { background: #1a4731; color: #3fb950; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
  .badge-bad  { background: #4a1519; color: #f85149; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
</style>
</head>
<body>
<h1>📊 Trading Bot — Backtest Report</h1>
<p class="subtitle">Strategy: <strong>{{ strategy }}</strong> &nbsp;|&nbsp; Pair: <strong>{{ pair }}</strong>
   &nbsp;|&nbsp; {{ start_date }} → {{ end_date }} &nbsp;|&nbsp; Generated: {{ generated_at }}</p>

<h2>Performance Summary</h2>
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Total Return</div>
    <div class="kpi-value {{ 'green' if metrics.total_return_pct >= 0 else 'red' }}">
      {{ "%.1f"|format(metrics.total_return_pct) }}%
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">CAGR</div>
    <div class="kpi-value {{ 'green' if metrics.cagr >= 0 else 'red' }}">{{ "%.1f"|format(metrics.cagr) }}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Sharpe Ratio</div>
    <div class="kpi-value blue">{{ "%.2f"|format(metrics.sharpe) }}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Sortino Ratio</div>
    <div class="kpi-value blue">{{ "%.2f"|format(metrics.sortino) }}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Max Drawdown</div>
    <div class="kpi-value red">{{ "%.1f"|format(metrics.max_drawdown_pct) }}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Calmar Ratio</div>
    <div class="kpi-value orange">{{ "%.2f"|format(metrics.calmar) }}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Win Rate</div>
    <div class="kpi-value purple">{{ "%.1f"|format(metrics.win_rate) }}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Profit Factor</div>
    <div class="kpi-value {{ 'green' if metrics.profit_factor >= 1.5 else 'orange' }}">
      {{ "%.2f"|format(metrics.profit_factor) }}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Trades</div>
    <div class="kpi-value">{{ metrics.total_trades }}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg Trade</div>
    <div class="kpi-value {{ 'green' if metrics.avg_trade_pct >= 0 else 'red' }}">
      {{ "%.2f"|format(metrics.avg_trade_pct) }}%
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Best Trade</div>
    <div class="kpi-value green">{{ "%.2f"|format(metrics.best_trade_pct) }}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Worst Trade</div>
    <div class="kpi-value red">{{ "%.2f"|format(metrics.worst_trade_pct) }}%</div>
  </div>
</div>

<h2>Equity Curve & Drawdown</h2>
<div class="chart-container">{{ equity_chart }}</div>

<h2>Trade Log (last 50)</h2>
<table>
  <tr>
    <th>#</th><th>Symbol</th><th>Entry</th><th>Exit</th>
    <th>PnL</th><th>PnL%</th><th>Bars</th><th>Reason</th>
  </tr>
  {% for t in trades[-50:] %}
  <tr>
    <td>{{ loop.index }}</td>
    <td>{{ t.symbol }}</td>
    <td>{{ "%.4f"|format(t.entry_price) }}</td>
    <td>{{ "%.4f"|format(t.exit_price or 0) }}</td>
    <td class="{{ 'green' if t.pnl >= 0 else 'red' }}">{{ "+%.2f"|format(t.pnl) if t.pnl >= 0 else "%.2f"|format(t.pnl) }}</td>
    <td class="{{ 'green' if t.pnl_pct >= 0 else 'red' }}">{{ "+%.2f"|format(t.pnl_pct*100) if t.pnl_pct >= 0 else "%.2f"|format(t.pnl_pct*100) }}%</td>
    <td>{{ (t.exit_bar or 0) - t.entry_bar }}</td>
    <td><span class="{{ 'badge-good' if 'profit' in (t.exit_reason or '') else 'badge-bad' }}">{{ t.exit_reason }}</span></td>
  </tr>
  {% endfor %}
</table>

<p class="footer">Professional Trading Bot — Generated {{ generated_at }} — For educational and research purposes only.</p>
</body>
</html>
"""


def _build_equity_chart(equity: pd.Series, trades) -> str:
    """Return inline Plotly chart HTML."""
    roll_max  = equity.cummax()
    drawdown  = (equity - roll_max) / roll_max * 100

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.70, 0.30],
                        subplot_titles=["Equity Curve", "Drawdown %"])

    fig.add_trace(go.Scatter(
        x=equity.index, y=equity.values, name="Equity",
        line=dict(color="#3fb950", width=2), fill="tozeroy",
        fillcolor="rgba(63,185,80,0.1)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=drawdown.index, y=drawdown.values, name="Drawdown",
        line=dict(color="#f85149", width=1), fill="tozeroy",
        fillcolor="rgba(248,81,73,0.2)",
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        height=500, showlegend=False,
        font=dict(color="#c9d1d9"),
        xaxis2=dict(showgrid=True, gridcolor="#21262d"),
        yaxis=dict(showgrid=True, gridcolor="#21262d"),
        yaxis2=dict(showgrid=True, gridcolor="#21262d"),
        margin=dict(l=50, r=20, t=30, b=20),
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")


def generate_report(
    result,
    strategy_name: str,
    pair: str,
    output_dir: Path = CONFIG.reports_dir,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    equity_chart = _build_equity_chart(result.equity_curve, result.trades)

    # Convert metrics dict to a simple namespace for template access
    class M:
        pass
    m = M()
    for k, v in result.metrics.items():
        setattr(m, k, v)

    tmpl = Template(HTML_TEMPLATE)
    html = tmpl.render(
        strategy     = strategy_name,
        pair         = pair,
        start_date   = str(result.equity_curve.index[0])[:10],
        end_date     = str(result.equity_curve.index[-1])[:10],
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        metrics      = m,
        trades       = result.trades,
        equity_chart = equity_chart,
    )

    out = output_dir / f"{pair.replace('/','_')}_{strategy_name}_report.html"
    out.write_text(html)
    logger.info(f"Report saved: {out}")
    return out
