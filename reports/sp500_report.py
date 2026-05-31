"""
S&P 500 10-year backtest HTML report generator — Version 2.
Produces a self-contained interactive HTML with Chart.js charts.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger


# ─── helpers ──────────────────────────────────────────────────────────────────

def _series_to_json(s: pd.Series) -> str:
    data = [{"x": str(idx.date() if hasattr(idx, "date") else idx), "y": round(float(v), 2)}
            for idx, v in s.items() if not np.isnan(v)]
    return json.dumps(data)


def _fmt(v, pct=False, decimals=2) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    if pct:
        return f"{v:+.{decimals}f}%"
    return f"{v:.{decimals}f}"


def _color(v, good="positive") -> str:
    if v is None:
        return ""
    positive = float(v) >= 0
    if good == "positive":
        return "color:#22c55e" if positive else "color:#ef4444"
    return "color:#ef4444" if positive else "color:#22c55e"  # inverse (drawdown)


# ─── main report generator ────────────────────────────────────────────────────

def generate_sp500_report(result, output_path: Path | str | None = None) -> Path:
    """
    Generate an interactive HTML report from an SP500BacktestResult.
    Returns the path to the written file.
    """
    output_path = Path(output_path) if output_path else Path("reports/sp500_backtest_report.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pm = result.portfolio_metrics
    period_start = str(result.portfolio_equity.index[0])[:10] if len(result.portfolio_equity) else "2015-01-01"
    period_end   = str(result.portfolio_equity.index[-1])[:10] if len(result.portfolio_equity) else "2024-12-31"

    # Equity chart data
    port_json  = _series_to_json(result.portfolio_equity)
    bench_json = _series_to_json(result.benchmark_equity)

    # Per-stock table rows
    stock_rows = []
    for ticker, m in sorted(result.stock_results.items(), key=lambda x: x[1].get("sharpe", 0), reverse=True):
        ret   = m.get("total_return_pct", 0)
        sharpe= m.get("sharpe", 0)
        dd    = m.get("max_drawdown_pct", 0)
        trades= m.get("total_trades", 0)
        wr    = m.get("win_rate", 0)
        stock_rows.append(f"""
        <tr>
          <td class="ticker">{ticker}</td>
          <td style="{_color(ret)}">{_fmt(ret, pct=True)}</td>
          <td>{_fmt(sharpe)}</td>
          <td style="{_color(dd, good='inverse')}">{_fmt(dd, pct=True)}</td>
          <td>{_fmt(wr, pct=True)}</td>
          <td>{trades}</td>
        </tr>""")
    stock_table = "".join(stock_rows)

    # Sector performance rows
    sector_rows = []
    if result.sector_performance is not None and len(result.sector_performance) > 0:
        for _, row in result.sector_performance.iterrows():
            ret = row.get("avg_return", 0)
            sharpe = row.get("avg_sharpe", 0)
            sector_rows.append(f"""
            <tr>
              <td>{row.get("sector", "—")}</td>
              <td>{int(row.get("count", 0))}</td>
              <td style="{_color(ret)}">{_fmt(ret, pct=True)}</td>
              <td>{_fmt(sharpe)}</td>
            </tr>""")
    sector_table = "".join(sector_rows) or "<tr><td colspan='4'>—</td></tr>"

    # Best/Worst lists
    best_list  = "".join(f"<li><span class='pos'>{t}</span></li>" for t in result.best_stocks)
    worst_list = "".join(f"<li><span class='neg'>{t}</span></li>" for t in result.worst_stocks)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>S&P 500 Backtest 10 Años — Version 2</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<style>
:root{{
  --bg:#0f1117;--surface:#1a1d27;--border:#2d3148;
  --text:#e2e8f0;--muted:#64748b;
  --accent:#6366f1;--accent2:#22d3ee;
  --pos:#22c55e;--neg:#ef4444;--warn:#f59e0b;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;line-height:1.6}}
header{{background:linear-gradient(135deg,#1e1b4b,#0c1445);padding:2rem;border-bottom:1px solid var(--border);text-align:center}}
header h1{{font-size:2rem;font-weight:700;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
header p{{color:var(--muted);margin-top:.5rem}}
.badge{{display:inline-block;background:var(--accent);color:#fff;font-size:.75rem;padding:.2rem .6rem;border-radius:99px;margin:.25rem}}
nav{{display:flex;gap:.5rem;padding:1rem 2rem;background:var(--surface);border-bottom:1px solid var(--border);flex-wrap:wrap}}
nav button{{background:transparent;border:1px solid var(--border);color:var(--muted);padding:.4rem 1rem;border-radius:.5rem;cursor:pointer;transition:.2s}}
nav button.active,nav button:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.section{{display:none;padding:2rem}}
.section.active{{display:block}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem;margin-bottom:2rem}}
.kpi{{background:var(--surface);border:1px solid var(--border);border-radius:.75rem;padding:1.25rem;text-align:center}}
.kpi .label{{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
.kpi .value{{font-size:1.75rem;font-weight:700;margin-top:.25rem}}
.kpi .sub{{font-size:.8rem;color:var(--muted)}}
.pos{{color:var(--pos)}}
.neg{{color:var(--neg)}}
.warn{{color:var(--warn)}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:.75rem;padding:1.5rem;margin-bottom:1.5rem}}
.card h3{{font-size:1.1rem;font-weight:600;margin-bottom:1rem;color:var(--accent2)}}
.chart-box{{height:350px;position:relative}}
table{{width:100%;border-collapse:collapse;font-size:.875rem}}
th{{background:var(--bg);color:var(--muted);text-transform:uppercase;font-size:.7rem;letter-spacing:.05em;padding:.75rem;text-align:left;border-bottom:1px solid var(--border)}}
td{{padding:.6rem .75rem;border-bottom:1px solid var(--border)}}
tr:hover td{{background:rgba(99,102,241,.06)}}
.ticker{{font-weight:600;color:var(--accent2)}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}}
@media(max-width:768px){{.two-col{{grid-template-columns:1fr}}}}
ul.stock-list{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:.5rem}}
ul.stock-list li{{background:var(--bg);border:1px solid var(--border);border-radius:.5rem;padding:.4rem .75rem;font-size:.85rem}}
.vs-row{{display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap}}
.vs-card{{flex:1;min-width:200px;background:var(--bg);border:1px solid var(--border);border-radius:.75rem;padding:1rem}}
.vs-card h4{{font-size:.8rem;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}}
.vs-card .big{{font-size:2rem;font-weight:800}}
.delta{{font-size:.9rem;margin-top:.25rem}}
</style>
</head>
<body>
<header>
  <h1>S&P 500 Backtest — 10 Años</h1>
  <p>Período: {period_start} → {period_end} &nbsp;|&nbsp; {len(result.stock_results)} acciones analizadas</p>
  <span class="badge">Version 2.0</span>
  <span class="badge">Portfolio Activo</span>
  <span class="badge">Rebalanceo Mensual</span>
</header>
<nav>
  <button class="active" onclick="show('overview',this)">Resumen</button>
  <button onclick="show('equity',this)">Curva de Equity</button>
  <button onclick="show('stocks',this)">Acciones</button>
  <button onclick="show('sectors',this)">Sectores</button>
  <button onclick="show('ranking',this)">Ranking</button>
</nav>

<!-- ═══ OVERVIEW ════════════════════════════════════════════════════════════ -->
<div id="overview" class="section active">
  <div class="vs-row">
    <div class="vs-card">
      <h4>Portfolio Activo</h4>
      <div class="big {'pos' if pm.get('total_return_pct',0)>=0 else 'neg'}"
           style="{_color(pm.get('total_return_pct',0))}">{_fmt(pm.get("total_return_pct",0), pct=True)}</div>
      <div class="delta" style="{_color(pm.get('cagr',0))}">CAGR {_fmt(pm.get('cagr',0), pct=True)}</div>
    </div>
    <div class="vs-card">
      <h4>Benchmark S&P 500 (SPY)</h4>
      <div class="big" style="{_color(pm.get('benchmark_return',0))}">{_fmt(pm.get("benchmark_return",0), pct=True)}</div>
      <div class="delta" style="{_color(pm.get('benchmark_cagr',0))}">CAGR {_fmt(pm.get('benchmark_cagr',0), pct=True)}</div>
    </div>
    <div class="vs-card">
      <h4>Alpha Generado</h4>
      <div class="big" style="{_color(pm.get('alpha',0))}">{_fmt(pm.get('alpha',0), pct=True)}</div>
      <div class="delta" style="{_color(pm.get('information_ratio',0))}">Info Ratio {_fmt(pm.get('information_ratio',0))}</div>
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="label">Sharpe Ratio</div>
      <div class="value" style="{_color(pm.get('sharpe',0))}">{_fmt(pm.get('sharpe',0))}</div>
      <div class="sub">anualizado</div>
    </div>
    <div class="kpi">
      <div class="label">Sortino Ratio</div>
      <div class="value" style="{_color(pm.get('sortino',0))}">{_fmt(pm.get('sortino',0))}</div>
    </div>
    <div class="kpi">
      <div class="label">Max Drawdown</div>
      <div class="value" style="color:var(--neg)">{_fmt(pm.get('max_drawdown_pct',0), pct=True)}</div>
    </div>
    <div class="kpi">
      <div class="label">Calmar Ratio</div>
      <div class="value">{_fmt(pm.get('calmar',0))}</div>
    </div>
    <div class="kpi">
      <div class="label">Beta vs SPY</div>
      <div class="value">{_fmt(pm.get('beta',1.0))}</div>
    </div>
    <div class="kpi">
      <div class="label">Volatilidad Anual</div>
      <div class="value" style="color:var(--warn)">{_fmt(pm.get('annual_vol',0), pct=True)}</div>
    </div>
    <div class="kpi">
      <div class="label">Win Rate Stocks</div>
      <div class="value" style="{_color(pm.get('avg_win_rate',50)-50)}">{_fmt(pm.get('avg_win_rate',0), pct=True)}</div>
    </div>
    <div class="kpi">
      <div class="label">Acciones Activas</div>
      <div class="value">{len(result.stock_results)}</div>
      <div class="sub">de universo S&P 500</div>
    </div>
  </div>

  <div class="card">
    <h3>Metodología de la Version 2</h3>
    <p style="color:var(--muted);margin-bottom:1rem">
      La v2 amplía el bot de crypto a acciones del S&P 500, añade optimización de portafolio
      y realiza un backtest completo de 10 años (2015-2024) con rebalanceo mensual.
    </p>
    <table>
      <tr><th>Mejora</th><th>Version 1</th><th>Version 2</th></tr>
      <tr><td>Universo</td><td>Crypto (BTC/ETH)</td><td>S&P 500 (50 acciones)</td></tr>
      <tr><td>Período backtest</td><td>Variable (1-3 años)</td><td>10 años fijos (2015-2024)</td></tr>
      <tr><td>Construcción portafolio</td><td>Simple single-asset</td><td>MPT + Risk Parity + rebalanceo</td></tr>
      <tr><td>Estrategias equity</td><td>—</td><td>Momentum Factor, Sector Rotation, Mean Rev.</td></tr>
      <tr><td>Métricas</td><td>Sharpe, CAGR, Drawdown</td><td>+ Alpha, Beta, Info Ratio, Tracking Error</td></tr>
      <tr><td>Benchmark</td><td>BTC/ETH buy & hold</td><td>SPY (S&P 500 ETF)</td></tr>
    </table>
  </div>
</div>

<!-- ═══ EQUITY ════════════════════════════════════════════════════════════ -->
<div id="equity" class="section">
  <div class="card">
    <h3>Curva de Equity — Portfolio vs S&P 500 (SPY)</h3>
    <div class="chart-box"><canvas id="equityChart"></canvas></div>
  </div>
  <div class="card">
    <h3>Drawdown del Portfolio</h3>
    <div class="chart-box"><canvas id="drawdownChart"></canvas></div>
  </div>
</div>

<!-- ═══ STOCKS ════════════════════════════════════════════════════════════ -->
<div id="stocks" class="section">
  <div class="card">
    <h3>Rendimiento por Acción ({len(result.stock_results)} acciones)</h3>
    <div style="overflow-x:auto">
    <table>
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Retorno Total</th>
          <th>Sharpe</th>
          <th>Max Drawdown</th>
          <th>Win Rate</th>
          <th>Trades</th>
        </tr>
      </thead>
      <tbody>
        {stock_table}
      </tbody>
    </table>
    </div>
  </div>
</div>

<!-- ═══ SECTORS ════════════════════════════════════════════════════════════ -->
<div id="sectors" class="section">
  <div class="card">
    <h3>Performance por Sector GICS</h3>
    <div class="chart-box"><canvas id="sectorChart"></canvas></div>
  </div>
  <div class="card">
    <h3>Tabla de Sectores</h3>
    <table>
      <thead>
        <tr><th>Sector</th><th>Acciones</th><th>Retorno Promedio</th><th>Sharpe Promedio</th></tr>
      </thead>
      <tbody>
        {sector_table}
      </tbody>
    </table>
  </div>
</div>

<!-- ═══ RANKING ════════════════════════════════════════════════════════════ -->
<div id="ranking" class="section">
  <div class="two-col">
    <div class="card">
      <h3>Top 10 Mejores Acciones (por Sharpe)</h3>
      <ul class="stock-list">{best_list}</ul>
    </div>
    <div class="card">
      <h3>Bottom 10 Peores Acciones</h3>
      <ul class="stock-list">{worst_list}</ul>
    </div>
  </div>
  <div class="card">
    <h3>Nuevas Estrategias v2 para Equities</h3>
    <table>
      <thead><tr><th>Estrategia</th><th>Tipo</th><th>Descripción</th><th>Parámetros Clave</th></tr></thead>
      <tbody>
        <tr><td class="ticker">momentum_factor</td><td>Factor</td><td>Momentum cruzado 12-1 meses (Fama-French)</td><td>lookback=252, skip=21</td></tr>
        <tr><td class="ticker">sector_rotation</td><td>Rotación</td><td>Rotación entre ETFs sectoriales por fuerza relativa</td><td>rs_period=63, ma=200</td></tr>
        <tr><td class="ticker">equity_mean_reversion</td><td>Reversión</td><td>Z-score contra media móvil con filtro de volumen</td><td>window=20, z=2.0</td></tr>
      </tbody>
    </table>
  </div>
  <div class="card">
    <h3>Optimización de Portafolio</h3>
    <table>
      <thead><tr><th>Método</th><th>Objetivo</th><th>Resultado Esperado</th></tr></thead>
      <tbody>
        <tr><td class="ticker">Min Variance</td><td>Mínimo riesgo</td><td>Sharpe moderado, DD bajo</td></tr>
        <tr><td class="ticker">Max Sharpe</td><td>Mejor ratio riesgo/retorno</td><td>Sharpe alto, DD moderado</td></tr>
        <tr><td class="ticker">Risk Parity</td><td>Igual contribución de riesgo</td><td>Drawdowns balanceados</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
function show(id, btn) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
  if (id === 'equity') initCharts();
  if (id === 'sectors') initSectorChart();
}}

const portData  = {port_json};
const benchData = {bench_json};

let chartsInit = false;
function initCharts() {{
  if (chartsInit) return;
  chartsInit = true;

  const ctx1 = document.getElementById('equityChart').getContext('2d');
  new Chart(ctx1, {{
    type: 'line',
    data: {{
      datasets: [
        {{
          label: 'Portfolio Activo',
          data: portData,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          tension: 0.1,
        }},
        {{
          label: 'S&P 500 (SPY)',
          data: benchData,
          borderColor: '#22d3ee',
          backgroundColor: 'rgba(34,211,238,0.05)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: true,
          tension: 0.1,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
      scales: {{
        x: {{ type: 'time', time: {{ unit: 'year' }}, ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e2235' }} }},
        y: {{ ticks: {{ color: '#64748b', callback: v => '$'+v.toLocaleString() }}, grid: {{ color: '#1e2235' }} }}
      }}
    }}
  }});

  // Drawdown chart
  function computeDD(data) {{
    let peak = -Infinity, dd = [];
    for (const p of data) {{
      if (p.y > peak) peak = p.y;
      dd.push({{ x: p.x, y: peak > 0 ? ((p.y - peak) / peak * 100) : 0 }});
    }}
    return dd;
  }}
  const ctx2 = document.getElementById('drawdownChart').getContext('2d');
  new Chart(ctx2, {{
    type: 'line',
    data: {{
      datasets: [
        {{
          label: 'Portfolio DD',
          data: computeDD(portData),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239,68,68,0.15)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: true,
        }},
        {{
          label: 'SPY DD',
          data: computeDD(benchData),
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245,158,11,0.07)',
          borderWidth: 1,
          pointRadius: 0,
          fill: true,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
      scales: {{
        x: {{ type: 'time', time: {{ unit: 'year' }}, ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e2235' }} }},
        y: {{ ticks: {{ color: '#64748b', callback: v => v.toFixed(1)+'%' }}, grid: {{ color: '#1e2235' }} }}
      }}
    }}
  }});
}}

let sectorInit = false;
function initSectorChart() {{
  if (sectorInit) return;
  sectorInit = true;
  const sectorData = {json.dumps([
      {"sector": row.get("sector",""), "ret": round(float(row.get("avg_return",0)),2), "sharpe": round(float(row.get("avg_sharpe",0)),2)}
      for _, row in (result.sector_performance.iterrows() if result.sector_performance is not None and len(result.sector_performance) else iter([]))
  ])};
  if (!sectorData.length) return;
  const ctx = document.getElementById('sectorChart').getContext('2d');
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: sectorData.map(d => d.sector),
      datasets: [
        {{
          label: 'Retorno Promedio (%)',
          data: sectorData.map(d => d.ret),
          backgroundColor: sectorData.map(d => d.ret >= 0 ? 'rgba(99,102,241,0.7)' : 'rgba(239,68,68,0.7)'),
          borderRadius: 4,
        }},
        {{
          label: 'Sharpe Promedio',
          data: sectorData.map(d => d.sharpe),
          backgroundColor: 'rgba(34,211,238,0.5)',
          borderRadius: 4,
          type: 'line',
          borderColor: '#22d3ee',
          pointRadius: 4,
          yAxisID: 'y2',
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e2235' }} }},
        y: {{ ticks: {{ color: '#64748b', callback: v => v+'%' }}, grid: {{ color: '#1e2235' }} }},
        y2: {{ position: 'right', ticks: {{ color: '#22d3ee' }}, grid: {{ display: false }} }}
      }}
    }}
  }});
}}
</script>
<footer style="text-align:center;padding:2rem;color:var(--muted);font-size:.8rem;border-top:1px solid var(--border)">
  Generado el {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC &nbsp;|&nbsp; Professional Trading Bot v2.0 &nbsp;|&nbsp;
  <em>Los resultados pasados no garantizan rendimientos futuros. Solo para fines educativos.</em>
</footer>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    logger.info(f"S&P 500 report written to {output_path}")
    return output_path
