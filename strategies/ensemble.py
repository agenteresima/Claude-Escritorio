"""
Strategy Ensemble — majority voting across multiple strategies.
Only enters a trade when N out of M strategies agree.
This dramatically improves win rate by reducing false signals.

Voting modes:
  "majority"  — more than half agree (default)
  "unanimous" — all agree (highest quality, fewer trades)
  "weighted"  — weight each strategy by its recent Sharpe ratio

Inspired by: QuantConnect ensemble research, Jesse multi-strategy approach.
"""
import pandas as pd
import numpy as np
from collections import Counter
from typing import Literal
from loguru import logger

from strategies.base import BaseStrategy
from strategies.trend_ema import TrendEMAStrategy
from strategies.supertrend import SuperTrendStrategy
from strategies.breakout import BreakoutStrategy
from strategies.ichimoku import IchimokuStrategy
from strategies.regime_adaptive import RegimeAdaptiveStrategy
from risk.manager import RiskManager


ENSEMBLE_MEMBERS = {
    "trend_ema":       TrendEMAStrategy,
    "supertrend":      SuperTrendStrategy,
    "breakout":        BreakoutStrategy,
    "ichimoku":        IchimokuStrategy,
    "regime_adaptive": RegimeAdaptiveStrategy,
}


class EnsembleStrategy(BaseStrategy):
    name = "ensemble"
    description = "Majority vote across 5 strategies — highest signal quality"

    def __init__(self, risk_manager: RiskManager,
                 mode: Literal["majority", "unanimous", "weighted"] = "majority",
                 min_votes: int = 3):
        super().__init__(risk_manager)
        self.mode      = mode
        self.min_votes = min_votes
        self._members  = {k: cls(risk_manager) for k, cls in ENSEMBLE_MEMBERS.items()}
        self._weights: dict[str, float] = {k: 1.0 for k in ENSEMBLE_MEMBERS}

    def update_weights_from_backtest(self, sharpe_scores: dict[str, float]):
        """Call after backtesting each member — weights by Sharpe ratio."""
        total = sum(max(v, 0.01) for v in sharpe_scores.values())
        for k in self._weights:
            self._weights[k] = max(sharpe_scores.get(k, 0.0), 0.0) / total if total else 1.0
        logger.info(f"Ensemble weights updated: {self._weights}")

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        member_signals: dict[str, pd.Series] = {}

        for name, strat in self._members.items():
            try:
                # Strategies need indicators already attached (from prepare())
                sig_df = strat.generate_signals(df.copy())
                member_signals[name] = sig_df["signal"]
            except Exception as e:
                logger.debug(f"Ensemble member '{name}' failed: {e}")
                member_signals[name] = pd.Series(0, index=df.index)

        votes_df = pd.DataFrame(member_signals)

        if self.mode == "majority":
            long_votes  = (votes_df == 1).sum(axis=1)
            short_votes = (votes_df == -1).sum(axis=1)
            total       = len(self._members)
            threshold   = max(self.min_votes, total // 2 + 1)
            df["signal"]      = 0
            df.loc[long_votes  >= threshold, "signal"] = 1
            df.loc[short_votes >= threshold, "signal"] = -1

        elif self.mode == "unanimous":
            df["signal"] = 0
            df.loc[(votes_df == 1).all(axis=1),  "signal"] = 1
            df.loc[(votes_df == -1).all(axis=1), "signal"] = -1

        elif self.mode == "weighted":
            score = pd.Series(0.0, index=df.index)
            for name, sigs in member_signals.items():
                w = self._weights.get(name, 1.0)
                score += sigs * w
            df["signal"] = 0
            threshold = sum(self._weights.values()) * 0.5
            df.loc[score >=  threshold, "signal"] = 1
            df.loc[score <= -threshold, "signal"] = -1

        # Attach vote counts for analysis
        df["long_votes"]  = (votes_df == 1).sum(axis=1)
        df["short_votes"] = (votes_df == -1).sum(axis=1)
        df["vote_consensus"] = df["long_votes"] / len(self._members)

        # Use average of member stop/take-profit
        stop_cols = []
        tp_cols   = []
        for name, strat in self._members.items():
            try:
                sig_df = strat.generate_signals(df.copy())
                if "stop_loss"   in sig_df.columns: stop_cols.append(sig_df["stop_loss"])
                if "take_profit" in sig_df.columns: tp_cols.append(sig_df["take_profit"])
            except Exception:
                pass

        if stop_cols:
            df["stop_loss"]   = pd.concat(stop_cols, axis=1).mean(axis=1)
        if tp_cols:
            df["take_profit"] = pd.concat(tp_cols, axis=1).mean(axis=1)

        n_long  = (df["signal"] == 1).sum()
        n_short = (df["signal"] == -1).sum()
        logger.debug(f"Ensemble [{self.mode}]: {n_long} longs, {n_short} shorts")

        return df
