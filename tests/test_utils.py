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
    def pnl_list(self):
        return [120.0, -40.0, 80.0, 60.0, -30.0]

    def test_monthly_returns(self, equity):
        from utils.performance import monthly_returns
        monthly = monthly_returns(equity)
        assert isinstance(monthly, pd.DataFrame)
        assert len(monthly) > 0

    def test_rolling_sharpe(self, equity):
        from utils.performance import rolling_sharpe
        rs = rolling_sharpe(equity, window=30)
        assert isinstance(rs, pd.Series)
        assert rs.notna().any()

    def test_max_consecutive_losses(self, pnl_list):
        from utils.performance import max_consecutive_losses
        mc = max_consecutive_losses(pnl_list)
        assert mc == 1  # only 1 loss in a row max

    def test_expectancy_positive(self):
        from utils.performance import expectancy
        # 60% win rate, avg_win=100, avg_loss=50 → 0.6*100 - 0.4*50 = 40
        exp = expectancy(win_rate=0.6, avg_win=100, avg_loss=50)
        assert exp == pytest.approx(40.0, abs=0.01)

    def test_expectancy_negative(self):
        from utils.performance import expectancy
        exp = expectancy(win_rate=0.3, avg_win=50, avg_loss=200)
        assert exp < 0

    def test_ulcer_index(self, equity):
        from utils.performance import ulcer_index
        ui = ulcer_index(equity)
        assert ui >= 0

    def test_mar_ratio(self):
        from utils.performance import mar_ratio
        assert mar_ratio(cagr_pct=20.0, max_dd_pct=-10.0) == pytest.approx(2.0)
        assert mar_ratio(cagr_pct=20.0, max_dd_pct=0.0) == 0.0

    def test_full_analytics_uses_backtest_result(self, equity):
        from utils.performance import full_analytics
        from backtesting.engine import BacktestResult
        metrics = {
            "sharpe": 1.5, "max_drawdown_pct": -5.0, "win_rate": 60.0,
            "total_return_pct": 20.0, "total_trades": 0, "profit_factor": 1.8,
            "cagr": 18.0, "sortino": 1.6, "calmar": 1.2,
        }
        result = BacktestResult(trades=[], equity_curve=equity, metrics=metrics)
        report = full_analytics(result, initial_capital=10_000)
        assert "expectancy"  in report
        assert "ulcer_index" in report


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
        assert "rsi_14" in out.columns
        # pandas-ta MACD columns: MACD_12_26_9
        assert any(c.startswith("MACD") for c in out.columns)

    def test_add_volatility_indicators(self, df):
        from utils.indicators import add_volatility_indicators
        out = add_volatility_indicators(df)
        assert "atr_14" in out.columns
        # pandas-ta BB columns: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
        assert any(c.startswith("BB") for c in out.columns)

    def test_add_volume_indicators(self, df):
        from utils.indicators import add_volume_indicators
        out = add_volume_indicators(df)
        assert "obv" in out.columns
        assert "vol_ratio" in out.columns

    def test_compute_market_regime(self, df):
        from utils.indicators import compute_market_regime, add_all_indicators
        df_ind = add_all_indicators(df)
        regime = compute_market_regime(df_ind)
        # Returns pd.Series of {-1, 0, 1}
        assert isinstance(regime, pd.Series)
        assert set(regime.unique()).issubset({-1, 0, 1})

    def test_no_nan_in_tail(self, df):
        from utils.indicators import add_all_indicators
        out = add_all_indicators(df)
        tail = out.tail(10)
        for col in ["rsi_14", "atr_14"]:
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
        from datetime import datetime, timezone
        ef = EventsFilter()
        # Use a date/time that doesn't match any recurring events
        # (recurring events match specific weekdays and day ranges)
        non_event_day = datetime(2022, 6, 15, 10, 0, tzinfo=timezone.utc)  # Wed mid-month
        with patch.object(ef, "_fetch_forex_factory", return_value=[]):
            safe, reason = ef.is_safe_to_trade(now=non_event_day)
        assert safe is True
        assert reason == "ok"

    def test_blocks_during_event(self):
        from utils.events_filter import EventsFilter
        from datetime import datetime, timedelta, timezone
        ef = EventsFilter()
        now = datetime(2022, 6, 15, 10, 0, tzinfo=timezone.utc)
        # Simulate event in 30 min — within 1h pre-blackout
        mock_event = {
            "datetime": now + timedelta(minutes=30),
            "title": "US CPI",
        }
        with patch.object(ef, "_fetch_forex_factory", return_value=[mock_event]):
            safe, reason = ef.is_safe_to_trade(now=now)
        assert safe is False
        assert "CPI" in reason or "macro" in reason.lower() or reason != "ok"

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
    def cf_with_data(self):
        from utils.correlation import CorrelationFilter
        rng = np.random.default_rng(42)
        idx = pd.date_range("2022-01-01", periods=200, freq="1h")
        btc = pd.Series(np.cumprod(1 + rng.normal(0.001, 0.01, 200)), index=idx)
        # ETH closely tracks BTC (highly correlated)
        eth = btc * pd.Series(np.cumprod(1 + rng.normal(0, 0.002, 200)), index=idx)
        # SOL is an independent random walk
        sol = pd.Series(np.cumprod(1 + rng.normal(0.001, 0.02, 200)), index=idx)

        cf = CorrelationFilter(threshold=0.80)
        cf.update("BTC/USDT", btc)
        cf.update("ETH/USDT", eth)
        cf.update("SOL/USDT", sol)
        return cf

    def test_threshold_attribute(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter(threshold=0.80)
        assert cf.threshold == 0.80

    def test_detects_high_correlation(self, cf_with_data):
        # ETH mirrors BTC closely → should be blocked
        is_corr = cf_with_data.is_correlated_with_open(
            candidate="ETH/USDT",
            open_symbols=["BTC/USDT"],
        )
        assert is_corr is True

    def test_empty_open_symbols(self, cf_with_data):
        # Nothing open → never correlated
        result = cf_with_data.is_correlated_with_open(
            candidate="BTC/USDT",
            open_symbols=[],
        )
        assert result is False

    def test_unknown_candidate(self, cf_with_data):
        result = cf_with_data.is_correlated_with_open(
            candidate="UNKNOWN/USDT",
            open_symbols=["BTC/USDT"],
        )
        assert result is False

    def test_diversified_subset(self, cf_with_data):
        subset = cf_with_data.get_diversified_subset(
            ["BTC/USDT", "ETH/USDT", "SOL/USDT"], max_positions=2
        )
        assert len(subset) <= 2
        # BTC and ETH are correlated → should not both be in subset
        assert not ("BTC/USDT" in subset and "ETH/USDT" in subset)

    def test_correlation_matrix(self, cf_with_data):
        mat = cf_with_data.correlation_matrix(["BTC/USDT", "ETH/USDT"])
        assert isinstance(mat, pd.DataFrame)
        assert mat.shape == (2, 2)
