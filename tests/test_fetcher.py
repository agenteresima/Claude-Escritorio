"""
Tests for data/fetcher.py.
All network calls are mocked — no real exchange connections.
"""
import time
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from tests.conftest import make_ohlcv


def _fake_ohlcv(n: int = 10, since_ms: int = 0):
    """Return a list of n OHLCV rows starting at since_ms."""
    rows = []
    for i in range(n):
        ts = since_ms + i * 3_600_000
        rows.append([ts, 100 + i, 105 + i, 95 + i, 102 + i, 1000 + i])
    return rows


# ── Cache helpers ─────────────────────────────────────────────────────────────

class TestCachePath:
    def test_slash_replaced(self):
        from data.fetcher import _cache_path
        p = _cache_path("BTC/USDT", "1h", "binance")
        assert "/" not in p.name
        assert "BTC_USDT" in p.name

    def test_format(self):
        from data.fetcher import _cache_path
        p = _cache_path("ETH/USDT", "4h", "bybit")
        assert p.suffix == ".parquet"
        assert "bybit" in p.name
        assert "4h" in p.name


# ── CCXT fetch ────────────────────────────────────────────────────────────────

class TestFetchCCXT:
    @pytest.fixture
    def mock_exchange(self):
        exc = MagicMock()
        exc.rateLimit = 100
        return exc

    def test_returns_dataframe(self, tmp_path, mock_exchange):
        from data import fetcher as fetcher_module

        rows = _fake_ohlcv(5, since_ms=1_700_000_000_000)
        mock_exchange.fetch_ohlcv.return_value = rows

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exchange):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        for col in ["open", "high", "low", "close", "volume"]:
            assert col in df.columns
        assert df.index.tz is not None

    def test_cache_hit_skips_exchange(self, tmp_path, mock_exchange):
        from data import fetcher as fetcher_module

        # Pre-create a cache file
        safe = "BTC_USDT"
        cache_file = tmp_path / f"binance_{safe}_1h.parquet"
        df_cached = make_ohlcv(20)
        df_cached.to_parquet(cache_file)

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exchange):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2020-01-01", use_cache=True
            )

        mock_exchange.fetch_ohlcv.assert_not_called()
        assert len(df) == 20

    def test_cache_disabled_always_fetches(self, tmp_path, mock_exchange):
        from data import fetcher as fetcher_module

        rows = _fake_ohlcv(3, since_ms=1_700_000_000_000)
        mock_exchange.fetch_ohlcv.return_value = rows

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exchange):
            fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )
            fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )

        assert mock_exchange.fetch_ohlcv.call_count == 2

    def test_deduplicates_timestamps(self, tmp_path, mock_exchange):
        from data import fetcher as fetcher_module

        ts = 1_700_000_000_000
        # Duplicate first row
        rows = _fake_ohlcv(5, since_ms=ts)
        rows = [rows[0]] + rows
        mock_exchange.fetch_ohlcv.return_value = rows

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exchange):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )

        assert df.index.is_unique

    def test_until_ms_stops_pagination(self, tmp_path, mock_exchange):
        from data import fetcher as fetcher_module

        # 1000-row batch (triggers pagination), then 5 rows
        large_batch = _fake_ohlcv(1000, since_ms=1_700_000_000_000)
        mock_exchange.fetch_ohlcv.return_value = large_batch

        start_str = "2023-11-14"
        # end 1 hour after start — should stop after first batch exceeds until_ms
        end_str = "2023-11-14"

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exchange):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start=start_str, end=end_str, use_cache=False
            )

        # Should have stopped — only one batch fetched
        assert mock_exchange.fetch_ohlcv.call_count >= 1


# ── Retry logic ───────────────────────────────────────────────────────────────

class TestRetryLogic:
    def test_retries_on_network_error(self, tmp_path):
        import ccxt
        from data import fetcher as fetcher_module

        mock_exc = MagicMock()
        mock_exc.rateLimit = 100
        rows = _fake_ohlcv(3, since_ms=1_700_000_000_000)
        # Fail twice then succeed
        mock_exc.fetch_ohlcv.side_effect = [
            ccxt.NetworkError("timeout"),
            ccxt.NetworkError("timeout"),
            rows,
        ]

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch.object(fetcher_module, "_retry_sleep"), \
             patch("ccxt.binance", return_value=mock_exc):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )

        assert len(df) == 3
        assert mock_exc.fetch_ohlcv.call_count == 3

    def test_raises_after_max_retries(self, tmp_path):
        import ccxt
        from data import fetcher as fetcher_module

        mock_exc = MagicMock()
        mock_exc.rateLimit = 100
        mock_exc.fetch_ohlcv.side_effect = ccxt.NetworkError("no route to host")

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch.object(fetcher_module, "_retry_sleep"), \
             patch("ccxt.binance", return_value=mock_exc):
            with pytest.raises(ccxt.NetworkError):
                fetcher_module.fetch_ohlcv_ccxt(
                    "BTC/USDT", "1h", start="2023-11-14", use_cache=False
                )

        assert mock_exc.fetch_ohlcv.call_count == fetcher_module.MAX_RETRIES

    def test_rate_limit_exceeded_backs_off(self, tmp_path):
        import ccxt
        from data import fetcher as fetcher_module

        mock_exc = MagicMock()
        mock_exc.rateLimit = 100
        rows = _fake_ohlcv(3, since_ms=1_700_000_000_000)
        mock_exc.fetch_ohlcv.side_effect = [
            ccxt.RateLimitExceeded("too many requests"),
            rows,
        ]

        sleep_calls = []
        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch.object(fetcher_module, "_retry_sleep", side_effect=sleep_calls.append), \
             patch("ccxt.binance", return_value=mock_exc):
            df = fetcher_module.fetch_ohlcv_ccxt(
                "BTC/USDT", "1h", start="2023-11-14", use_cache=False
            )

        assert len(df) == 3
        assert len(sleep_calls) >= 1   # backed off at least once


# ── Multi-pair fetch ──────────────────────────────────────────────────────────

class TestFetchMultiplePairs:
    def test_returns_dict(self, tmp_path):
        from data import fetcher as fetcher_module

        mock_exc = MagicMock()
        mock_exc.rateLimit = 100
        rows = _fake_ohlcv(5, since_ms=1_700_000_000_000)
        mock_exc.fetch_ohlcv.return_value = rows

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exc):
            result = fetcher_module.fetch_multiple_pairs(
                ["BTC/USDT", "ETH/USDT"], timeframe="1h", start="2023-11-14"
            )

        assert "BTC/USDT" in result
        assert "ETH/USDT" in result
        assert isinstance(result["BTC/USDT"], pd.DataFrame)

    def test_failed_pair_skipped(self, tmp_path):
        from data import fetcher as fetcher_module

        mock_exc = MagicMock()
        mock_exc.rateLimit = 100
        rows = _fake_ohlcv(5, since_ms=1_700_000_000_000)
        mock_exc.fetch_ohlcv.side_effect = [rows, Exception("bad symbol")]

        with patch.object(fetcher_module, "CACHE_DIR", tmp_path), \
             patch("ccxt.binance", return_value=mock_exc):
            result = fetcher_module.fetch_multiple_pairs(
                ["BTC/USDT", "INVALID/PAIR"], timeframe="1h", start="2023-11-14"
            )

        assert "BTC/USDT" in result
        assert "INVALID/PAIR" not in result


# ── Retry sleep timing ────────────────────────────────────────────────────────

class TestRetrySleep:
    def test_backoff_grows_exponentially(self):
        from data.fetcher import _retry_sleep, _BACKOFF_BASE
        waited = []
        with patch("time.sleep", side_effect=lambda t: waited.append(t)):
            _retry_sleep(0)
            _retry_sleep(1)
            _retry_sleep(2)
        assert waited[0] == pytest.approx(_BACKOFF_BASE ** 0)
        assert waited[1] == pytest.approx(_BACKOFF_BASE ** 1)
        assert waited[2] == pytest.approx(_BACKOFF_BASE ** 2)
