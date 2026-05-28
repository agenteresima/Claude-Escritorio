"""
Correlation filter — prevents opening highly correlated positions simultaneously.
Professional traders cap portfolio correlation at 0.7 to maintain diversification.
"""
import pandas as pd
import numpy as np
from loguru import logger


class CorrelationFilter:
    def __init__(self, threshold: float = 0.75, window: int = 100):
        self.threshold = threshold
        self.window    = window
        self._returns_cache: dict[str, pd.Series] = {}

    def update(self, symbol: str, prices: pd.Series):
        self._returns_cache[symbol] = prices.pct_change().dropna().tail(self.window)

    def is_correlated_with_open(self, candidate: str,
                                 open_symbols: list[str]) -> bool:
        """
        Returns True if candidate is too correlated with any currently open position.
        """
        if candidate not in self._returns_cache or not open_symbols:
            return False

        r_cand = self._returns_cache[candidate]

        for sym in open_symbols:
            if sym not in self._returns_cache:
                continue
            r_open = self._returns_cache[sym]
            # Align series
            aligned = pd.concat([r_cand, r_open], axis=1).dropna()
            if len(aligned) < 20:
                continue
            corr = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
            if abs(corr) >= self.threshold:
                logger.debug(f"Correlation filter: {candidate} vs {sym} = {corr:.2f} — skipping")
                return True

        return False

    def correlation_matrix(self, symbols: list[str]) -> pd.DataFrame:
        available = [s for s in symbols if s in self._returns_cache]
        if len(available) < 2:
            return pd.DataFrame()
        returns = pd.DataFrame({s: self._returns_cache[s] for s in available})
        return returns.corr()

    def get_diversified_subset(self, candidates: list[str],
                                max_positions: int = 5) -> list[str]:
        """
        Greedy selection of low-correlated assets from candidate list.
        """
        selected: list[str] = []

        for c in candidates:
            if len(selected) >= max_positions:
                break
            if not self.is_correlated_with_open(c, selected):
                selected.append(c)

        return selected
