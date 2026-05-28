"""
Interactive Dash dashboard for real-time monitoring and backtest review.
Run:  python reports/dashboard.py
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, dash_table
from pathlib import Path
from config import CONFIG


app = dash.Dash(__name__, title="Pro Trading Bot Dashboard")

app.layout = html.Div(
    style={"backgroundColor": "#0d1117", "color": "#c9d1d9", "fontFamily": "monospace", "padding": "20px"},
    children=[
        html.H1("Professional Trading Bot", style={"color": "#58a6ff", "textAlign": "center"}),

        html.Div([
            html.Label("Strategy:", style={"color": "#8b949e"}),
            dcc.Dropdown(
                id="strategy-selector",
                options=[{"label": s, "value": s} for s in
                         ["trend_ema", "mean_reversion", "breakout", "hybrid_ml"]],
                value="trend_ema",
                style={"backgroundColor": "#161b22", "color": "#c9d1d9", "width": "300px"},
            ),
        ], style={"marginBottom": "20px"}),

        dcc.Interval(id="live-interval", interval=60_000, n_intervals=0),

        html.Div(id="kpi-cards", style={"display": "flex", "gap": "20px", "marginBottom": "20px"}),

        dcc.Graph(id="equity-chart",     style={"height": "400px"}),
        dcc.Graph(id="drawdown-chart",   style={"height": "250px"}),
        dcc.Graph(id="trade-dist-chart", style={"height": "300px"}),

        html.H3("Trade Log", style={"color": "#58a6ff", "marginTop": "30px"}),
        html.Div(id="trade-table"),
    ],
)


def _load_results(strategy: str) -> dict:
    """Load latest backtest results from reports dir."""
    report_dir = CONFIG.reports_dir
    csv_files  = list(report_dir.glob(f"*comparison*.csv"))
    if not csv_files:
        return {}
    df  = pd.read_csv(csv_files[-1])
    row = df[df["strategy"] == strategy]
    return row.iloc[0].to_dict() if not row.empty else {}


def _kpi_card(label: str, value: str, color: str = "#58a6ff") -> html.Div:
    return html.Div(
        style={
            "backgroundColor": "#161b22", "border": f"1px solid {color}",
            "borderRadius": "8px", "padding": "15px", "minWidth": "150px", "textAlign": "center",
        },
        children=[
            html.P(label, style={"color": "#8b949e", "margin": "0", "fontSize": "12px"}),
            html.H3(value, style={"color": color, "margin": "5px 0 0 0"}),
        ],
    )


@app.callback(
    [Output("kpi-cards", "children"),
     Output("equity-chart", "figure"),
     Output("drawdown-chart", "figure"),
     Output("trade-dist-chart", "figure")],
    [Input("strategy-selector", "value"),
     Input("live-interval", "n_intervals")],
)
def update_dashboard(strategy, _):
    metrics = _load_results(strategy)

    # KPI cards
    cards = [
        _kpi_card("Total Return", f"{metrics.get('total_return_%', 0):.1f}%", "#3fb950"),
        _kpi_card("Sharpe Ratio", f"{metrics.get('sharpe', 0):.2f}",          "#58a6ff"),
        _kpi_card("Win Rate",     f"{metrics.get('win_rate_%', 0):.1f}%",     "#d2a8ff"),
        _kpi_card("Max DD",       f"{metrics.get('max_dd_%', 0):.1f}%",       "#f85149"),
        _kpi_card("Profit Factor",f"{metrics.get('profit_factor', 0):.2f}",   "#ffa657"),
        _kpi_card("CAGR",         f"{metrics.get('cagr_%', 0):.1f}%",         "#79c0ff"),
    ]

    # Placeholder charts (populated from real data when available)
    empty_fig = go.Figure()
    empty_fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        title="No data yet — run a backtest first",
        font=dict(color="#c9d1d9"),
    )

    return cards, empty_fig, empty_fig, empty_fig


@app.callback(Output("trade-table", "children"), Input("strategy-selector", "value"))
def update_table(strategy):
    return html.P("Run a backtest to populate the trade log.", style={"color": "#8b949e"})


if __name__ == "__main__":
    app.run(debug=True, port=8050)
