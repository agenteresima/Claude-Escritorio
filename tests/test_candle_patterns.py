"""
Tests for candlestick pattern recognition.
Uses handcrafted OHLCV rows where patterns are guaranteed present.
"""
import pytest
import pandas as pd
import numpy as np
from utils.candle_patterns import (
    bullish_engulfing, bearish_engulfing,
    hammer, shooting_star,
    morning_star, doji,
    add_candle_patterns,
)


def _make_candle(open_, high, low, close):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000}


def _df(*rows) -> pd.DataFrame:
    idx = pd.date_range("2023-01-01", periods=len(rows), freq="1h", tz="UTC")
    return pd.DataFrame(list(rows), index=idx)


class TestBullishEngulfing:
    def test_detects_pattern(self):
        df = _df(
            _make_candle(105, 106, 99, 100),   # bear candle
            _make_candle(98,  110, 97, 109),   # bull engulfs
        )
        result = bullish_engulfing(df)
        assert result.iloc[-1] is True or result.iloc[-1] == True

    def test_no_false_positive_on_bull_bear(self):
        df = _df(
            _make_candle(100, 110, 99, 108),  # bull
            _make_candle(109, 111, 105, 106), # bear but doesn't engulf
        )
        result = bullish_engulfing(df)
        assert not result.iloc[-1]


class TestHammer:
    def test_detects_hammer(self):
        # Small body at top, long lower wick
        df = _df(
            _make_candle(100, 101, 80, 100),   # hammer
        )
        result = hammer(df)
        assert result.iloc[-1]

    def test_rejects_non_hammer(self):
        # Large body, small wick
        df = _df(
            _make_candle(100, 115, 98, 114),   # large bull candle, not a hammer
        )
        result = hammer(df)
        assert not result.iloc[-1]


class TestShootingStar:
    def test_detects_shooting_star(self):
        df = _df(
            _make_candle(100, 120, 99, 101),   # small body at bottom, long upper wick
        )
        result = shooting_star(df)
        assert result.iloc[-1]


class TestDoji:
    def test_detects_doji(self):
        df = _df(
            _make_candle(100, 105, 95, 100),   # open == close
        )
        result = doji(df)
        assert result.iloc[-1]


class TestAddCandlePatterns:
    def test_columns_added(self, ohlcv):
        df = add_candle_patterns(ohlcv)
        expected_cols = [
            "pat_bull_engulf", "pat_bear_engulf", "pat_hammer",
            "pat_shooting_star", "candle_score",
        ]
        for col in expected_cols:
            assert col in df.columns

    def test_candle_score_range(self, ohlcv):
        df = add_candle_patterns(ohlcv)
        # Score is bounded by number of patterns
        assert df["candle_score"].between(-5, 5).all()
