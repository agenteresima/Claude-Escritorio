"""
Risk management module.
Implements position sizing (Kelly, fixed-fraction, ATR-based),
drawdown control, and trade validation.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger

from config import CONFIG


@dataclass
class TradeSignal:
    symbol: str
    direction: str          # "long" | "short"
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float = 1.0  # [0, 1] — used by ML strategies


@dataclass
class PortfolioState:
    capital: float
    equity_curve: list[float] = field(default_factory=list)
    open_trades: int = 0
    peak_equity: float = 0.0

    def current_drawdown(self) -> float:
        if self.peak_equity == 0:
            return 0.0
        return (self.peak_equity - self.capital) / self.peak_equity

    def update(self, new_equity: float):
        self.capital = new_equity
        self.equity_curve.append(new_equity)
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity


class RiskManager:
    """
    Central risk manager used by all strategies.
    Combines techniques from Freqtrade's stoploss manager,
    Jesse's position sizer, and institutional Kelly-fraction sizing.
    """

    def __init__(self, config=CONFIG.risk, initial_capital: float = CONFIG.backtest.initial_capital):
        self.cfg = config
        self.portfolio = PortfolioState(capital=initial_capital)
        self.portfolio.peak_equity = initial_capital

    # ------------------------------------------------------------------
    # Position sizing
    # ------------------------------------------------------------------

    def fixed_fraction_size(self, entry: float, stop: float) -> float:
        """Risk a fixed % of capital per trade (standard approach)."""
        risk_amount = self.portfolio.capital * self.cfg.stake_amount_pct
        price_risk = abs(entry - stop)
        if price_risk == 0:
            return 0.0
        return risk_amount / price_risk

    def kelly_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Half-Kelly criterion for position sizing.
        Only used when we have sufficient trade history (min 30 trades).
        """
        if avg_loss == 0:
            return self.cfg.stake_amount_pct
        b = avg_win / avg_loss
        kelly = (b * win_rate - (1 - win_rate)) / b
        half_kelly = max(0.0, kelly / 2)
        # Clamp between 1 % and max_position_size_pct
        return np.clip(half_kelly, 0.01, self.cfg.max_position_size_pct)

    def atr_size(self, entry: float, atr: float, multiplier: float = 1.5) -> float:
        """
        ATR-based position sizing — normalises for market volatility.
        Used by professional traders and Jesse framework.
        """
        stop_distance = atr * multiplier
        stop_price = entry - stop_distance
        return self.fixed_fraction_size(entry, stop_price)

    # ------------------------------------------------------------------
    # Dynamic stop/target computation
    # ------------------------------------------------------------------

    def atr_stop_loss(self, entry: float, atr: float, direction: str = "long",
                      multiplier: float = 2.0) -> float:
        if direction == "long":
            return entry - atr * multiplier
        return entry + atr * multiplier

    def atr_take_profit(self, entry: float, stop: float, direction: str = "long",
                        rr_ratio: Optional[float] = None) -> float:
        rr = rr_ratio or self.cfg.risk_reward_ratio
        risk = abs(entry - stop)
        if direction == "long":
            return entry + risk * rr
        return entry - risk * rr

    # ------------------------------------------------------------------
    # Trade validation — gate before placing any order
    # ------------------------------------------------------------------

    def validate_signal(self, signal: TradeSignal) -> bool:
        if self.portfolio.current_drawdown() > self.cfg.max_drawdown_pct:
            logger.warning(
                f"Max drawdown {self.cfg.max_drawdown_pct*100:.1f}% hit — trading paused."
            )
            return False

        if self.portfolio.open_trades >= self.cfg.max_open_trades:
            logger.debug(f"Max open trades ({self.cfg.max_open_trades}) reached.")
            return False

        denom = abs(signal.entry_price - signal.stop_loss)
        if denom < 1e-9:
            return False
        rr = abs(signal.take_profit - signal.entry_price) / denom
        if rr < self.cfg.risk_reward_ratio - 1e-9:
            logger.debug(f"R/R {rr:.2f} below minimum {self.cfg.risk_reward_ratio}")
            return False

        return True

    # ------------------------------------------------------------------
    # Trailing stop update
    # ------------------------------------------------------------------

    def update_trailing_stop(self, current_price: float, entry: float,
                              current_stop: float, direction: str = "long") -> float:
        trail = self.cfg.trailing_stop_pct
        if direction == "long":
            new_stop = current_price * (1 - trail)
            return max(current_stop, new_stop)
        else:
            new_stop = current_price * (1 + trail)
            return min(current_stop, new_stop)
