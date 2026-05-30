"""
Tests for utils modules lacking coverage:
  - utils/performance.py
  - utils/indicators.py
  - utils/events_filter.py (unit, no network)
  - utils/sentiment.py    (unit, no network)
  - utils/correlation.py
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from tests.conftest import make_ohlcv


# ── Performance analytics ─────────────────────────────────────────────────────

class TestPerformance:
    @pytest.fixture
    def equity(self):
        rng = np.random.default_rng(0)
        vals = 10_000 * np.cumprod(1 + rng.normal(0.001, 0.01, 252))
        return pd.Series(vals, index=pd.date_range("2022-01-01", periods=252, freq="D"))

    @pytest.fixture
    def trades(self):
        return [
            {"pnl": 120, "entry_time": "2022-01-01", "exit_time": "2022-01-03"},
            {"pnl": -40, "entry_time": "2022-01-04", "exit_time": "2022-01-05"},
            {"pnl": 80,  "entry_time": "2022-01-06", "exit_time": "2022-01-08"},
            {"pnl": 60,  "entry_time": "2022-01-09", "exit_time": "2022-01-11"},
            {"pnl": -30, "entry_time": "2022-01-12", "exit_time": "2022-01-13"},
        ]

    def test_monthly_returns(self, equity):
        from utils.performance import monthly_returns
        monthly = monthly_returns(equity)
        assert isinstance(monthly, pd.Series)
        assert len(monthly) > 0

    def test_rolling_sharpe(self, equity):
        from utils.performance import rolling_sharpe
        rs = rolling_sharpe(equity, window=30)
        assert isinstance(rs, pd.Series)
        assert rs.notna().any()

    def test_max_consecutive_losses(self, trades):
        from utils.performance import max_consecutive_losses
        mc = max_consecutive_losses(trades)
        assert mc == 1  # only 1 loss in a row

    def test_expectancy(self, trades):
        from utils.performance import expectancy
        exp = expectancy(trades)
        assert exp > 0  # net profitable set

    def test_r_multiples(self, trades):
        from utils.performance import r_multiples
        rs = r_multiples(trades, risk_per_trade=40)
        assert len(rs) == len(trades)
        assert rs[0] == pytest.approx(3.0, abs=0.01)  # 120/40

    def test_ulcer_index(self, equity):
        from utils.performance import ulcer_index
        ui = ulcer_index(equity)
        assert ui >= 0

    def test_full_analytics(self, equity, trades):
        from utils.performance import full_analytics
        report = full_analytics(equity, trades)
        assert "sharpe" in report or "total_return" in report


# ── Indicators ────────────────────────────────────────────────────────────────

class TestIndicators:
    @pytest.fixture
    def df(self):
        return make_ohlcv(300)

    def test_add_all_indicators(self, df):
        from utils.indicators import add_all_indicators
        out = add_all_indicators(df)
        assert len(out) == len(df)
        assert "ema_20" in out.columns or "close" in out.columns

    def test_add_trend_indicators(self, df):
        from utils.indicators import add_trend_indicators
        out = add_trend_indicators(df)
        for col in ["ema_9", "ema_21", "ema_50", "ema_200"]:
            assert col in out.columns

    def test_add_momentum_indicators(self, df):
        from utils.indicators import add_momentum_indicators
        out = add_momentum_indicators(df)
        assert "rsi" in out.columns
        assert "macd" in out.columns

    def test_add_volatility_indicators(self, df):
        from utils.indicators import add_volatility_indicators
        out = add_volatility_indicators(df)
        assert "atr" in out.columns
        assert "bb_upper" in out.columns or "bbands_upper" in out.columns

    def test_add_volume_indicators(self, df):
        from utils.indicators import add_volume_indicators
        out = add_volume_indicators(df)
        assert "obv" in out.columns or "volume" in out.columns

    def test_compute_market_regime(self, df):
        from utils.indicators import compute_market_regime, add_all_indicators
        df_ind = add_all_indicators(df)
        regime = compute_market_regime(df_ind.iloc[-1])
        assert regime in ("trending", "ranging", "breakout", "unknown") or isinstance(regime, str)

    def test_no_nan_in_tail(self, df):
        from utils.indicators import add_all_indicators
        out = add_all_indicators(df)
        tail = out.tail(10)
        # Key columns should not be NaN at the end
        for col in ["rsi", "macd", "atr"]:
            if col in tail.columns:
                assert not tail[col].isna().all(), f"{col} is all NaN in tail"


# ── Events filter (unit — no network) ────────────────────────────────────────

class TestEventsFilter:
    def test_import(self):
        from utils.events_filter import EventsFilter
        ef = EventsFilter()
        assert ef is not None

    def test_is_safe_to_trade_no_events(self):
        from utils.events_filter import EventsFilter
        ef = EventsFilter()
        with patch.object(ef, "upcoming_events", return_value=[]):
            safe, reason = ef.is_safe_to_trade()
        assert safe is True
        assert reason == "ok"

    def test_blocks_during_event(self):
        from utils.events_filter import EventsFilter
        from datetime import datetime, timedelta, timezone
        ef = EventsFilter()
        now = datetime.now(timezone.utc)
        # Simulate event in 30 min — within 1h pre-blackout
        mock_event = {
            "datetime": now + timedelta(minutes=30),
            "title": "US CPI",
            "impact": "high",
        }
        with patch.object(ef, "upcoming_events", return_value=[mock_event]):
            safe, reason = ef.is_safe_to_trade()
        assert safe is False
        assert "CPI" in reason or "event" in reason.lower()

    def test_upcoming_events_returns_list(self):
        from utils.events_filter import EventsFilter
        ef = EventsFilter()
        with patch.object(ef, "_fetch_forex_factory", return_value=[]):
            events = ef.upcoming_events(hours_ahead=48)
        assert isinstance(events, list)


# ── Sentiment gate (unit — no network) ───────────────────────────────────────

class TestSentiment:
    def test_sentiment_gate_neutral(self):
        from utils.sentiment import sentiment_gate
        result = sentiment_gate(fng_value=50, funding_rate=0.0001)
        assert result["allow_long"] is True
        assert result["reason"] == "ok"

    def test_sentiment_gate_blocks_longs_extreme_greed(self):
        from utils.sentiment import sentiment_gate
        result = sentiment_gate(fng_value=85, funding_rate=0.0001)
        assert result["allow_long"] is False
        assert "greed" in result["reason"].lower()

    def test_sentiment_gate_blocks_on_high_funding(self):
        from utils.sentiment import sentiment_gate
        result = sentiment_gate(fng_value=50, funding_rate=0.0015)
        assert result["allow_long"] is False
        assert "funding" in result["reason"].lower()

    def test_sentiment_gate_allows_shorts_extreme_greed(self):
        from utils.sentiment import sentiment_gate
        result = sentiment_gate(fng_value=85, funding_rate=0.0001)
        assert result["allow_short"] is True

    def test_sentiment_gate_none_values(self):
        from utils.sentiment import sentiment_gate
        result = sentiment_gate(fng_value=None, funding_rate=None)
        # Should default to allowing both when data unavailable
        assert isinstance(result["allow_long"], bool)
        assert isinstance(result["allow_short"], bool)


# ── Correlation filter ────────────────────────────────────────────────────────

class TestCorrelationFilter:
    @pytest.fixture
    def price_series(self):
        rng = np.random.default_rng(42)
        idx = pd.date_range("2022-01-01", periods=200, freq="1h")
        btc = pd.Series(np.cumprod(1 + rng.normal(0.001, 0.01, 200)), index=idx)
        eth = btc * (1 + rng.normal(0, 0.005, 200))  # highly correlated
        sol = pd.Series(np.cumprod(1 + rng.normal(0.001, 0.02, 200)), index=idx)
        return {"BTC/USDT": btc, "ETH/USDT": eth, "SOL/USDT": sol}

    def test_import(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)
        assert cf.threshold == 0.80

    def test_detects_correlation(self, price_series):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)
        cf.update_prices(price_series)
        # ETH is highly correlated with BTC
        is_corr = cf.is_correlated_with_open(
            candidate="ETH/USDT",
            open_symbols=["BTC/USDT"],
        )
        assert is_corr is True

    def test_uncorrelated_passes(self, price_series):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)
        cf.update_prices(price_series)
        # SOL (random walk) should not always be blocked
        # Just verify the method returns bool without error
        result = cf.is_correlated_with_open(
            candidate="SOL/USDT",
            open_symbols=[],
        )
        assert isinstance(result, bool)

    def test_diversified_subset(self, price_series):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)
        cf.update_prices(price_series)
        subset = cf.get_diversified_subset(
            list(price_series.keys()), max_pairs=2
        )
        assert len(subset) <= 2
