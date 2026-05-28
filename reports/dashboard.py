"""
Interactive Dash dashboard.
Run:  python reports/dashboard.py
Opens: http://localhost:8050
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, dash_table
from pathlib import Path
from config import CONFIG
from strategies import STRATEGIES

COLORS = {
    "bg":       "#0d1117",
    "panel":    "#161b22",
    "border":   "#30363d",
    "text":     "#c9d1d9",
    "dim":      "#8b949e",
    "blue":     "#58a6ff",
    "green":    "#3fb950",
    "red":      "#f85149",
    "purple":   "#d2a8ff",
    "orange":   "#ffa657",
}

app = dash.Dash(__name__, title="Pro Trading Bot")

PANEL = {"backgroundColor": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
         "borderRadius": "8px", "padding": "15px", "marginBottom": "15px"}

app.layout = html.Div(
    style={"backgroundColor": COLORS["bg"], "color": COLORS["text"],
           "fontFamily": "'Segoe UI', monospace", "padding": "20px", "minHeight": "100vh"},
    children=[
        # Header
        html.Div([
            html.H1("Professional Trading Bot", style={"color": COLORS["blue"], "margin": "0"}),
            html.P("Multi-strategy | Walk-forward optimised | Risk-managed",
                   style={"color": COLORS["dim"], "margin": "5px 0 0 0"}),
        ], style={"marginBottom": "25px"}),

        # Controls
        html.Div([
            html.Div([
                html.Label("Strategy", style={"color": COLORS["dim"], "fontSize": "12px"}),
                dcc.Dropdown(
                    id="strategy-dd",
                    options=[{"label": s, "value": s} for s in STRATEGIES.keys()],
                    value="trend_ema",
                    style={"backgroundColor": COLORS["panel"], "color": COLORS["text"]},
                    clearable=False,
                ),
            ], style={"width": "220px", "marginRight": "15px"}),
            html.Div([
                html.Label("Pair", style={"color": COLORS["dim"], "fontSize": "12px"}),
                dcc.Dropdown(
                    id="pair-dd",
                    options=[{"label": p, "value": p} for p in CONFIG.pairs],
                    value=CONFIG.pairs[0],
                    style={"backgroundColor": COLORS["panel"], "color": COLORS["text"]},
                    clearable=False,
                ),
            ], style={"width": "180px"}),
        ], style={"display": "flex", "marginBottom": "20px"}),

        dcc.Interval(id="refresh", interval=60_000, n_intervals=0),

        # KPI cards
        html.Div(id="kpis", style={"display": "flex", "flexWrap": "wrap", "gap": "12px", "marginBottom": "20px"}),

        # Charts row
        html.Div([
            html.Div([dcc.Graph(id="equity-chart")],
                     style={**PANEL, "flex": "2"}),
            html.Div([dcc.Graph(id="monthly-heatmap")],
                     style={**PANEL, "flex": "1"}),
        ], style={"display": "flex", "gap": "15px"}),

        html.Div([
            html.Div([dcc.Graph(id="drawdown-chart")],
                     style={**PANEL, "flex": "1"}),
            html.Div([dcc.Graph(id="trade-dist")],
                     style={**PANEL, "flex": "1"}),
        ], style={"display": "flex", "gap": "15px"}),

        # Strategy comparison
        html.Div([
            html.H3("Strategy Comparison", style={"color": COLORS["blue"], "marginBottom": "10px"}),
            html.Div(id="comparison-table"),
        ], style=PANEL),

        html.Div(id="status-bar",
                 style={"color": COLORS["dim"], "fontSize": "11px", "textAlign": "center", "marginTop": "15px"}),
    ],
)


def _kpi(label, value, color):
    return html.Div([
        html.P(label, style={"color": COLORS["dim"], "fontSize": "11px",
                             "margin": "0", "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.H3(value, style={"color": color, "margin": "4px 0 0 0", "fontSize": "20px"}),
    ], style={**PANEL, "minWidth": "140px", "textAlign": "center", "marginBottom": "0"})


def _load_csv(strategy: str, pair: str) -> tuple[dict, pd.Series]:
    """Load backtest results from saved CSV files."""
    eq_file = CONFIG.reports_dir / f"{pair.replace('/','_')}_{strategy}_equity.csv"
    if eq_file.exists():
        eq = pd.read_csv(eq_file, index_col=0, parse_dates=True).squeeze()
    else:
        eq = pd.Series(dtype=float)

    # Load comparison CSV for metrics
    cmp_files = sorted(CONFIG.reports_dir.glob("*comparison*.csv"))
    metrics = {}
    if cmp_files:
        df = pd.read_csv(cmp_files[-1])
        row = df[df["strategy"] == strategy]
        if not row.empty:
            metrics = row.iloc[0].to_dict()

    return metrics, eq


@app.callback(
    [Output("kpis", "children"),
     Output("equity-chart", "figure"),
     Output("drawdown-chart", "figure"),
     Output("monthly-heatmap", "figure"),
     Output("trade-dist", "figure"),
     Output("status-bar", "children")],
    [Input("strategy-dd", "value"),
     Input("pair-dd", "value"),
     Input("refresh", "n_intervals")],
)
def update_all(strategy, pair, _):
    metrics, equity = _load_csv(strategy, pair)

    # ── KPI cards ─────────────────────────────────────────────────────
    def fmt(k, suffix="", mult=1):
        v = metrics.get(k, 0)
        return f"{v * mult:.2f}{suffix}" if isinstance(v, float) else str(v)

    ret_pct = float(metrics.get("total_return_%", 0))
    kpis = [
        _kpi("Total Return",   f"{ret_pct:+.1f}%",           COLORS["green"] if ret_pct >= 0 else COLORS["red"]),
        _kpi("CAGR",           fmt("cagr_%", "%"),            COLORS["green"]),
        _kpi("Sharpe",         fmt("sharpe"),                 COLORS["blue"]),
        _kpi("Sortino",        fmt("sortino"),                COLORS["blue"]),
        _kpi("Max Drawdown",   fmt("max_dd_%", "%"),          COLORS["red"]),
        _kpi("Win Rate",       fmt("win_rate_%", "%"),        COLORS["purple"]),
        _kpi("Profit Factor",  fmt("profit_factor"),          COLORS["orange"]),
        _kpi("Total Trades",   str(int(metrics.get("total_trades", 0))), COLORS["text"]),
    ]

    base_layout = dict(
        template="plotly_dark", paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["panel"], font=dict(color=COLORS["text"]),
        margin=dict(l=50, r=20, t=35, b=30),
    )

    # ── Equity chart ──────────────────────────────────────────────────
    eq_fig = go.Figure(layout={**base_layout, "title": "Equity Curve", "height": 300})
    if not equity.empty:
        eq_fig.add_trace(go.Scatter(
            x=equity.index, y=equity.values, name="Equity",
            line=dict(color=COLORS["green"], width=2),
            fill="tozeroy", fillcolor="rgba(63,185,80,0.08)",
        ))

    # ── Drawdown chart ────────────────────────────────────────────────
    dd_fig = go.Figure(layout={**base_layout, "title": "Drawdown %", "height": 220})
    if not equity.empty:
        roll_max = equity.cummax()
        dd       = (equity - roll_max) / roll_max * 100
        dd_fig.add_trace(go.Scatter(
            x=dd.index, y=dd.values, name="Drawdown",
            line=dict(color=COLORS["red"], width=1),
            fill="tozeroy", fillcolor="rgba(248,81,73,0.15)",
        ))

    # ── Monthly heatmap ───────────────────────────────────────────────
    mh_fig = go.Figure(layout={**base_layout, "title": "Monthly Returns %", "height": 300})
    if not equity.empty and len(equity) > 30:
        from utils.performance import monthly_returns
        try:
            pivot = monthly_returns(equity)
            mh_fig.add_trace(go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale=[[0, COLORS["red"]], [0.5, COLORS["panel"]], [1, COLORS["green"]]],
                text=np.round(pivot.values, 1),
                texttemplate="%{text}%",
                showscale=False,
            ))
        except Exception:
            pass

    # ── Trade PnL distribution ────────────────────────────────────────
    dist_fig = go.Figure(layout={**base_layout, "title": "Trade PnL Distribution", "height": 220})

    status = f"Last updated: strategy={strategy} | pair={pair} | data={'loaded' if not equity.empty else 'no data — run a backtest first'}"

    return kpis, eq_fig, dd_fig, mh_fig, dist_fig, status


@app.callback(Output("comparison-table", "children"), Input("strategy-dd", "value"))
def update_comparison(_):
    cmp_files = sorted(CONFIG.reports_dir.glob("*comparison*.csv"))
    if not cmp_files:
        return html.P("No comparison data yet. Run: python main.py compare",
                      style={"color": COLORS["dim"]})
    df = pd.read_csv(cmp_files[-1])
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": COLORS["panel"], "color": COLORS["blue"],
                      "border": f"1px solid {COLORS['border']}", "fontWeight": "bold"},
        style_cell={"backgroundColor": COLORS["bg"], "color": COLORS["text"],
                    "border": f"1px solid {COLORS['border']}", "padding": "8px",
                    "fontFamily": "monospace"},
        style_data_conditional=[
            {"if": {"row_index": 0},
             "backgroundColor": "rgba(63,185,80,0.1)", "color": COLORS["green"]},
        ],
    )


if __name__ == "__main__":
    print("Dashboard: http://localhost:8050")
    app.run(debug=True, port=8050)
