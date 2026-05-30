"""
Tests filling coverage gaps in:
  - data/fetcher.py       (fetch_ohlcv_yfinance, fetch_multiple_pairs yfinance)
  - risk/portfolio_heat.py (PositionRisk properties, HeatReport.__str__,
                             can_add_position single-limit, reduce_size_to_fit zero-risk)
  - utils/performance.py  (r_multiples, full_analytics with trades)
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


# ── fetch_ohlcv_yfinance ──────────────────────────────────────────────────────

class TestFetchYFinance:
    def _make_yf_df(self):
        idx = pd.date_range("2022-01-01", periods=50, freq="1h", tz="UTC")
        return pd.DataFrame({
            "Open": np.full(50, 100.0),
            "High": np.full(50, 101.0),
            "Low":  np.full(50,  99.0),
            "Close": np.full(50, 100.5),
            "Volume": np.full(50, 1000.0),
        }, index=idx)

    def test_returns_dataframe(self, tmp_path):
        from data.fetcher import fetch_ohlcv_yfinance
        df = self._make_yf_df()
        with patch("data.fetcher.yf.download", return_value=df), \
             patch("data.fetcher.CACHE_DIR", tmp_path):
            result = fetch_ohlcv_yfinance("SPY", interval="1h", use_cache=False)
        assert isinstance(result, pd.DataFrame)
        assert "close" in result.columns

    def test_cache_hit(self, tmp_path):
        from data.fetcher import fetch_ohlcv_yfinance, _cache_path
        df = self._make_yf_df()
        df.columns = [c.lower() for c in df.columns]
        cache = tmp_path / "SPY_1h_yfinance.parquet"
        df.to_parquet(cache)
        with patch("data.fetcher.CACHE_DIR", tmp_path), \
             patch("data.fetcher.yf.download") as mock_dl:
            # Patch cache path to use tmp_path
            with patch("data.fetcher._cache_path", return_value=cache):
                result = fetch_ohlcv_yfinance("SPY", interval="1h", use_cache=True)
        mock_dl.assert_not_called()
        assert not result.empty

    def test_multiindex_columns_flattened(self, tmp_path):
        from data.fetcher import fetch_ohlcv_yfinance
        idx = pd.date_range("2022-01-01", periods=10, freq="1h", tz="UTC")
        # MultiIndex columns (pandas yfinance newer API)
        multi_cols = pd.MultiIndex.from_tuples([
            ("Open", "SPY"), ("High", "SPY"), ("Low", "SPY"),
            ("Close", "SPY"), ("Volume", "SPY"),
        ])
        df = pd.DataFrame(
            np.ones((10, 5)) * 100, index=idx, columns=multi_cols
        )
        with patch("data.fetcher.yf.download", return_value=df), \
             patch("data.fetcher.CACHE_DIR", tmp_path):
            result = fetch_ohlcv_yfinance("SPY", use_cache=False)
        assert "close" in result.columns

    def test_retry_on_yfinance_error(self, tmp_path):
        from data.fetcher import fetch_ohlcv_yfinance
        df = self._make_yf_df()
        call_count = [0]

        def _flaky(*a, **kw):
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("network glitch")
            return df

        with patch("data.fetcher.yf.download", side_effect=_flaky), \
             patch("data.fetcher._retry_sleep"), \
             patch("data.fetcher.CACHE_DIR", tmp_path):
            result = fetch_ohlcv_yfinance("SPY", use_cache=False)
        assert call_count[0] == 2
        assert not result.empty

    def test_fetch_multiple_pairs_yfinance_source(self, tmp_path):
        from data.fetcher import fetch_multiple_pairs
        df = self._make_yf_df()
        df.columns = [c.lower() for c in df.columns]
        with patch("data.fetcher.fetch_ohlcv_yfinance", return_value=df) as mock_yf, \
             patch("data.fetcher.CACHE_DIR", tmp_path):
            result = fetch_multiple_pairs(["SPY", "QQQ"], source="yfinance")
        assert "SPY" in result
        assert "QQQ" in result
        assert mock_yf.call_count == 2

    def test_fetch_multiple_pairs_error_skipped(self, tmp_path):
        from data.fetcher import fetch_multiple_pairs
        df = self._make_yf_df()
        df.columns = [c.lower() for c in df.columns]

        def _partial_fetch(pair, *a, **kw):
            if pair == "SPY":
                return df
            raise Exception("fetch failed")

        with patch("data.fetcher.fetch_ohlcv_ccxt", side_effect=_partial_fetch), \
             patch("data.fetcher.CACHE_DIR", tmp_path):
            result = fetch_multiple_pairs(["SPY", "FAIL/USDT"], source="ccxt")
        assert "SPY" in result
        assert "FAIL/USDT" not in result


# ── PositionRisk properties ───────────────────────────────────────────────────

class TestPositionRiskProperties:
    def _make_pos(self, direction="long", entry=40_000, current=41_000, stop=39_000, size=0.01):
        from risk.portfolio_heat import PositionRisk
        return PositionRisk(
            symbol="BTC/USDT", direction=direction,
            entry_price=entry, current_price=current,
            stop_loss=stop, size=size,
        )

    def test_dollar_risk_uses_entry_distance(self):
        pos = self._make_pos(entry=40_000, stop=39_000, size=0.01)
        # |40000 - 39000| * 0.01 = 10
        assert pos.dollar_risk == pytest.approx(10.0)

    def test_dollar_risk_current_uses_current_price(self):
        pos = self._make_pos(current=41_000, stop=39_000, size=0.01)
        # |41000 - 39000| * 0.01 = 20
        assert pos.dollar_risk_current == pytest.approx(20.0)

    def test_unrealised_pnl_long(self):
        pos = self._make_pos(direction="long", entry=40_000, current=41_000, size=0.01)
        # (41000 - 40000) * 0.01 = 10
        assert pos.unrealised_pnl == pytest.approx(10.0)

    def test_unrealised_pnl_short(self):
        pos = self._make_pos(direction="short", entry=40_000, current=39_000, size=0.01)
        # (40000 - 39000) * 0.01 = 10
        assert pos.unrealised_pnl == pytest.approx(10.0)

    def test_r_multiple_positive(self):
        # entry=40000, stop=39000, current=41000: unrealised=10, risk=10 → R=1.0
        pos = self._make_pos(entry=40_000, stop=39_000, current=41_000, size=0.01)
        assert pos.r_multiple == pytest.approx(1.0, rel=0.01)

    def test_r_multiple_zero_risk(self):
        # stop == entry → dollar_risk = 0 → returns 0.0
        pos = self._make_pos(entry=40_000, stop=40_000, size=0.01)
        assert pos.r_multiple == 0.0


# ── PortfolioHeatManager ──────────────────────────────────────────────────────

class TestPortfolioHeatManagerExtended:
    @pytest.fixture
    def phm(self):
        from risk.portfolio_heat import PortfolioHeatManager
        return PortfolioHeatManager(max_heat_pct=0.06, max_single_pct=0.02)

    def test_heat_report_str_ok(self, phm):
        phm.update_position("BTC/USDT", "long", 40_000, 40_500, 39_000, 0.001)
        report = phm.compute_heat(100_000)
        text = str(report)
        assert "OK" in text or "OVERLIMIT" in text

    def test_heat_report_str_overlimit(self, phm):
        # Add many large positions to breach 6% limit
        for i in range(10):
            phm.update_position(f"COIN{i}", "long", 40_000, 40_000, 30_000, 0.1)
        report = phm.compute_heat(10_000)
        assert not report.heat_ok
        assert "OVERLIMIT" in str(report)

    def test_can_add_position_single_too_large(self, phm):
        capital = 10_000
        new_risk = capital * 0.05   # 5% > 2% single limit
        allowed, reason = phm.can_add_position(capital, new_risk)
        assert allowed is False
        assert "Single" in reason or "single" in reason.lower()

    def test_can_add_position_portfolio_too_hot(self):
        from risk.portfolio_heat import PortfolioHeatManager
        # Use high single-pct limit so single-position check doesn't fire first
        phm = PortfolioHeatManager(max_heat_pct=0.06, max_single_pct=0.10)
        capital = 10_000
        # Fill portfolio close to 6% heat limit
        phm.update_position("BTC/USDT", "long", 40_000, 40_000, 39_400, 0.8)
        current_heat = phm.compute_heat(capital).total_heat_pct
        remaining = phm.max_heat_pct - current_heat
        # New risk would push over portfolio limit but is under single-pos limit
        new_risk = capital * (remaining + 0.005)
        allowed, reason = phm.can_add_position(capital, new_risk)
        assert allowed is False
        assert "heat" in reason.lower() or "portfolio" in reason.lower()

    def test_reduce_size_to_fit_zero_risk(self, phm):
        size = phm.reduce_size_to_fit(10_000, entry=40_000, stop=40_000)
        assert size == 0.0

    def test_reduce_size_to_fit_returns_positive(self, phm):
        size = phm.reduce_size_to_fit(10_000, entry=40_000, stop=39_000)
        assert size >= 0.0

    def test_remove_position(self, phm):
        phm.update_position("BTC/USDT", "long", 40_000, 40_000, 39_000, 0.01)
        phm.remove_position("BTC/USDT")
        assert "BTC/USDT" not in phm._positions

    def test_net_delta_pure_long(self, phm):
        phm.update_position("BTC/USDT", "long", 40_000, 40_000, 39_000, 1.0)
        report = phm.compute_heat(100_000)
        assert report.net_delta > 0

    def test_net_delta_mixed(self, phm):
        phm.update_position("BTC/USDT", "long",  40_000, 40_000, 39_000, 1.0)
        phm.update_position("ETH/USDT", "short", 2_000,  2_000,  2_100,  5.0)
        report = phm.compute_heat(100_000)
        assert -1 <= report.net_delta <= 1


# ── utils/performance.py ─────────────────────────────────────────────────────

class TestPerformanceExtended:
    def _make_trade(self, pnl, entry=40_000, stop=39_000, size=0.01, is_open=False):
        t = MagicMock()
        t.is_open     = is_open
        t.pnl         = pnl
        t.entry_price = entry
        t.stop_loss   = stop
        t.size        = size
        return t

    def test_r_multiples_with_closed_trades(self):
        from utils.performance import r_multiples
        trades = [
            self._make_trade(10.0),   # pnl=10, risk=10 → R=1.0
            self._make_trade(-5.0),   # pnl=-5, risk=10 → R=-0.5
        ]
        result = r_multiples(trades)
        assert len(result) == 2
        assert result.iloc[0] == pytest.approx(1.0, rel=0.01)

    def test_r_multiples_skips_open_trades(self):
        from utils.performance import r_multiples
        trades = [
            self._make_trade(10.0, is_open=False),
            self._make_trade(5.0,  is_open=True),   # should be skipped
        ]
        result = r_multiples(trades)
        assert len(result) == 1

    def test_r_multiples_skips_zero_risk(self):
        from utils.performance import r_multiples
        trades = [self._make_trade(10.0, entry=40_000, stop=40_000)]
        result = r_multiples(trades)
        assert len(result) == 0  # zero initial_risk → skipped

    def test_full_analytics_with_trades(self):
        from utils.performance import full_analytics
        from backtesting.engine import BacktestResult

        idx    = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.linspace(10_000, 11_000, 50), index=idx)
        metrics = {
            "sharpe": 1.5, "max_drawdown_pct": -5.0, "win_rate": 60.0,
            "total_return_pct": 10.0, "total_trades": 2, "profit_factor": 1.5,
            "sortino": 1.2, "calmar": 0.8, "cagr": 9.0,
        }
        trades = [
            self._make_trade(pnl=200.0),
            self._make_trade(pnl=-100.0),
        ]
        result = BacktestResult(equity_curve=equity, trades=trades, metrics=metrics)
        analytics = full_analytics(result, initial_capital=10_000)
        assert "expectancy"        in analytics
        assert "ulcer_index"       in analytics
        assert "max_consec_losses" in analytics
        assert "r_expectancy"      in analytics   # non-empty r_multiples → included

    def test_full_analytics_no_closed_trades(self):
        from utils.performance import full_analytics
        from backtesting.engine import BacktestResult

        idx    = pd.date_range("2022-01-01", periods=50, freq="1h")
        equity = pd.Series(np.ones(50) * 10_000, index=idx)
        metrics = {
            "sharpe": 0.0, "max_drawdown_pct": 0.0, "win_rate": 0.0,
            "total_return_pct": 0.0, "total_trades": 0, "profit_factor": 0.0,
            "sortino": 0.0, "calmar": 0.0, "cagr": 0.0,
        }
        result = BacktestResult(equity_curve=equity, trades=[], metrics=metrics)
        analytics = full_analytics(result, initial_capital=10_000)
        assert isinstance(analytics, dict)
        assert "expectancy" in analytics
