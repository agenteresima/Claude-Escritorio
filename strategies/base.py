"""
Abstract base class for all strategies.
Every strategy must implement generate_signals() returning a DataFrame
with a 'signal' column: 1=buy, -1=sell, 0=hold.
"""
from abc import ABC, abstractmethod
import pandas as pd
from risk.manager import RiskManager
from utils.indicators import add_all_indicators


class BaseStrategy(ABC):
    name: str = "base"
    description: str = ""

    def __init__(self, risk_manager: RiskManager):
        self.risk = risk_manager

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attach all indicators before calling generate_signals."""
        return add_all_indicators(df)

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Return df with added columns:
          signal    : 1 / -1 / 0
          stop_loss : price
          take_profit: price
        """

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare(df)
        return self.generate_signals(df)
