"""
Vectorised backtesting engine.
Inspired by vectorbt performance and Backtrader's event-driven logic,
but written to be readable and easy to extend.

Features:
  - Commission + slippage modelling
  - Trailing stops
  - Drawdown tracking
  - Trade log with full detail
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger

from config import CONFIG
from risk.manager import RiskManager, TradeSignal


@dataclass
class Trade:
    symbol: str
    entry_bar: int
    entry_price: float
    direction: str
    size: float
    stop_loss: float
    take_profit: float
    exit_bar: Optional[int]   = None
    exit_price: Optional[float] = None
    exit_reason: str          = ""
    pnl: float                = 0.0
    pnl_pct: float            = 0.0

    def close(self, bar: int, price: float, reason: str, commission: float):
        self.exit_bar    = bar
        self.exit_price  = price
        self.exit_reason = reason
        gross = (price - self.entry_price) * self.size
        if self.direction == "short":
            gross = -gross
        cost = (self.entry_price + price) * self.size * commission
        self.pnl     = gross - cost
        self.pnl_pct = self.pnl / (self.entry_price * self.size + 1e-9)

    @property
    def is_open(self) -> bool:
        return self.exit_bar is None


@dataclass
class BacktestResult:
    trades: list[Trade]
    equity_curve: pd.Series
    metrics: dict

    def summary(self) -> str:
        m = self.metrics
        lines = [
            "=" * 50,
            "  BACKTEST RESULTS",
            "=" * 50,
            f"  Total Return      : {m.get('total_return_pct', 0):.2f}%",
            f"  CAGR              : {m.get('cagr', 0):.2f}%",
            f"  Sharpe Ratio      : {m.get('sharpe', 0):.2f}",
            f"  Sortino Ratio     : {m.get('sortino', 0):.2f}",
            f"  Max Drawdown      : {m.get('max_drawdown_pct', 0):.2f}%",
            f"  Win Rate          : {m.get('win_rate', 0):.2f}%",
            f"  Profit Factor     : {m.get('profit_factor', 0):.2f}",
            f"  Total Trades      : {m.get('total_trades', 0)}",
            f"  Avg Trade         : {m.get('avg_trade_pct', 0):.2f}%",
            f"  Best Trade        : {m.get('best_trade_pct', 0):.2f}%",
            f"  Worst Trade       : {m.get('worst_trade_pct', 0):.2f}%",
            f"  Calmar Ratio      : {m.get('calmar', 0):.2f}",
            "=" * 50,
        ]
        return "\n".join(lines)


def _compute_metrics(trades: list[Trade], equity: pd.Series,
                     initial_capital: float) -> dict:
    _empty = {
        "total_return_pct": (equity.iloc[-1] / initial_capital - 1) * 100
                            if len(equity) else 0.0,
        "cagr": 0.0, "sharpe": 0.0, "sortino": 0.0,
        "max_drawdown_pct": 0.0, "calmar": 0.0,
        "win_rate": 0.0, "profit_factor": 0.0, "total_trades": 0,
        "avg_trade_pct": 0.0, "best_trade_pct": 0.0, "worst_trade_pct": 0.0,
    }

    pnl_list = [t.pnl for t in trades if not t.is_open]
    pnl_pct  = [t.pnl_pct for t in trades if not t.is_open]

    if not pnl_list:
        return _empty

    wins  = [p for p in pnl_list if p > 0]
    losses= [p for p in pnl_list if p <= 0]

    total_return = (equity.iloc[-1] / initial_capital - 1) * 100
    n_years      = len(equity) / (365 * 24)  # assume hourly bars
    cagr         = ((equity.iloc[-1] / initial_capital) ** (1 / max(n_years, 0.01)) - 1) * 100

    returns      = equity.pct_change().dropna()
    sharpe       = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(365 * 24)

    neg_returns  = returns[returns < 0]
    sortino      = (returns.mean() / (neg_returns.std() + 1e-9)) * np.sqrt(365 * 24)

    roll_max     = equity.cummax()
    drawdown     = (equity - roll_max) / roll_max
    max_dd       = drawdown.min() * 100

    calmar       = cagr / abs(max_dd + 1e-9)

    profit_factor = sum(wins) / (abs(sum(losses)) + 1e-9)
    win_rate      = len(wins) / max(len(pnl_list), 1) * 100

    return {
        "total_return_pct" : total_return,
        "cagr"             : cagr,
        "sharpe"           : sharpe,
        "sortino"          : sortino,
        "max_drawdown_pct" : max_dd,
        "calmar"           : calmar,
        "win_rate"         : win_rate,
        "profit_factor"    : profit_factor,
        "total_trades"     : len(pnl_list),
        "avg_trade_pct"    : np.mean(pnl_pct) * 100 if pnl_pct else 0,
        "best_trade_pct"   : max(pnl_pct) * 100 if pnl_pct else 0,
        "worst_trade_pct"  : min(pnl_pct) * 100 if pnl_pct else 0,
    }


class BacktestEngine:
    """
    Single-symbol event-driven backtester.
    Pass in a DataFrame already annotated with signals/stop_loss/take_profit.
    """

    def __init__(self, config=CONFIG.backtest, risk_manager: Optional[RiskManager] = None):
        self.cfg   = config
        self.risk  = risk_manager or RiskManager(initial_capital=config.initial_capital)

    def run(self, df: pd.DataFrame, symbol: str = "ASSET") -> BacktestResult:
        capital   = self.cfg.initial_capital
        commission= self.cfg.commission
        slippage  = self.cfg.slippage

        trades: list[Trade]  = []
        equity_vals: list[float] = [capital]
        open_trade: Optional[Trade] = None

        for i, (ts, row) in enumerate(df.iterrows()):
            price = float(row["close"])

            # ---- Manage open trade ----
            if open_trade:
                # Update trailing stop
                open_trade.stop_loss = self.risk.update_trailing_stop(
                    price, open_trade.entry_price, open_trade.stop_loss, open_trade.direction
                )

                hit_sl = price <= open_trade.stop_loss
                hit_tp = price >= open_trade.take_profit
                exit_signal = row.get("signal", 0) == -1

                if hit_sl or hit_tp or exit_signal:
                    reason = "stop_loss" if hit_sl else ("take_profit" if hit_tp else "signal_exit")
                    exit_price = price * (1 - slippage if open_trade.direction == "long" else 1 + slippage)
                    open_trade.close(i, exit_price, reason, commission)
                    capital += open_trade.pnl
                    self.risk.portfolio.open_trades -= 1
                    trades.append(open_trade)
                    open_trade = None

            # ---- Open new trade ----
            if open_trade is None and row.get("signal", 0) == 1:
                sl  = float(row.get("stop_loss",   price * (1 - self.risk.cfg.hard_stop_pct)))
                tp  = float(row.get("take_profit", price * (1 + self.risk.cfg.take_profit_pct)))
                sig = TradeSignal(symbol, "long", price, sl, tp)

                if self.risk.validate_signal(sig):
                    entry = price * (1 + slippage)
                    size  = self.risk.atr_size(entry, float(row.get("atr_14", price * 0.02)))
                    size  = min(size, (capital * self.risk.cfg.max_position_size_pct) / entry)

                    open_trade = Trade(symbol, i, entry, "long", size, sl, tp)
                    self.risk.portfolio.open_trades += 1

            self.risk.portfolio.update(capital)
            equity_vals.append(capital)

        # Close any still-open trade at the last bar
        if open_trade:
            open_trade.close(len(df) - 1, float(df["close"].iloc[-1]), "end_of_data", commission)
            capital += open_trade.pnl
            trades.append(open_trade)

        equity = pd.Series(equity_vals[1:], index=df.index)
        metrics = _compute_metrics(trades, equity, self.cfg.initial_capital)

        return BacktestResult(trades=trades, equity_curve=equity, metrics=metrics)
