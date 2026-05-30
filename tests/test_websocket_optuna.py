"""
Tests for:
  - data/websocket_feed.py  (Candle, CandleBuffer, WebSocketFeed internals)
  - backtesting/optuna_optimizer.py  (_score, optimize error paths,
                                       optuna_importance_chart)
"""
import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock


# ── Candle ────────────────────────────────────────────────────────────────────

class TestCandle:
    def _make_ohlcv(self):
        # [timestamp_ms, open, high, low, close, volume]
        return [1_672_531_200_000, 40_000, 40_500, 39_800, 40_200, 1.5]

    def test_creation_parses_fields(self):
        from data.websocket_feed import Candle
        ohlcv = self._make_ohlcv()
        c = Candle("BTC/USDT", ohlcv, closed=True)
        assert c.symbol == "BTC/USDT"
        assert c.open   == 40_000
        assert c.high   == 40_500
        assert c.low    == 39_800
        assert c.close  == 40_200
        assert c.volume == 1.5
        assert c.closed is True
        assert isinstance(c.timestamp, datetime)

    def test_timestamp_is_utc(self):
        from data.websocket_feed import Candle
        c = Candle("ETH/USDT", self._make_ohlcv())
        assert c.timestamp.tzinfo is not None

    def test_to_series_returns_dict(self):
        from data.websocket_feed import Candle
        c = Candle("BTC/USDT", self._make_ohlcv())
        s = c.to_series()
        assert set(s.keys()) == {"open", "high", "low", "close", "volume"}
        assert s["close"] == 40_200

    def test_repr_contains_symbol(self):
        from data.websocket_feed import Candle
        c = Candle("BTC/USDT", self._make_ohlcv())
        assert "BTC/USDT" in repr(c)


# ── CandleBuffer ──────────────────────────────────────────────────────────────

class TestCandleBufferExtended:
    def _make_candle(self, symbol="BTC/USDT", close=40_000.0, ts_offset_s=0):
        from data.websocket_feed import Candle
        ts_ms = (1_672_531_200 + ts_offset_s) * 1000
        return Candle(symbol, [ts_ms, close, close * 1.01, close * 0.99, close, 1.0])

    def test_push_and_is_ready(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer(maxlen=500)
        for i in range(200):
            buf.push(self._make_candle(ts_offset_s=i * 60))
        assert buf.is_ready("BTC/USDT", min_bars=200) is True
        assert buf.is_ready("BTC/USDT", min_bars=201) is False

    def test_maxlen_trims_oldest(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer(maxlen=5)
        for i in range(8):
            buf.push(self._make_candle(ts_offset_s=i * 60))
        assert len(buf._data["BTC/USDT"]) == 5

    def test_to_dataframe_multi_symbol(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer()
        for i in range(3):
            buf.push(self._make_candle("BTC/USDT", ts_offset_s=i * 60))
            buf.push(self._make_candle("ETH/USDT", ts_offset_s=i * 60))
        df = buf.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6
        assert df.index.is_monotonic_increasing

    def test_to_dataframe_empty(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer()
        df = buf.to_dataframe()
        assert df.empty

    def test_to_df_unknown_symbol_empty(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer()
        df = buf.to_df("UNKNOWN/USDT")
        assert df.empty

    def test_push_multiple_symbols_independent(self):
        from data.websocket_feed import CandleBuffer
        buf = CandleBuffer()
        buf.push(self._make_candle("BTC/USDT"))
        buf.push(self._make_candle("ETH/USDT"))
        buf.push(self._make_candle("ETH/USDT", ts_offset_s=60))
        assert len(buf._data["BTC/USDT"]) == 1
        assert len(buf._data["ETH/USDT"]) == 2


# ── WebSocketFeed ─────────────────────────────────────────────────────────────

class TestWebSocketFeed:
    def test_constructor_initialises(self):
        from data.websocket_feed import WebSocketFeed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            feed = WebSocketFeed(["BTC/USDT", "ETH/USDT"], timeframe="1m")
            assert feed.symbols == ["BTC/USDT", "ETH/USDT"]
            assert feed.timeframe == "1m"
            assert feed._running is False
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    def test_stop_sets_running_false(self):
        from data.websocket_feed import WebSocketFeed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            feed = WebSocketFeed(["BTC/USDT"])
            feed._running = True
            feed.stop()
            assert feed._running is False
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    @pytest.mark.asyncio
    async def test_produce_falls_back_to_rest_on_import_error(self):
        from data.websocket_feed import WebSocketFeed

        feed = WebSocketFeed(["BTC/USDT"])

        async def _fake_rest():
            feed._running = False  # stop after one "iteration"

        with patch.object(feed, "_rest_poll_loop", side_effect=_fake_rest) as mock_rest, \
             patch.dict("sys.modules", {"ccxtpro": None}):
            await feed._produce()
        mock_rest.assert_called_once()

    @pytest.mark.asyncio
    async def test_watch_symbol_emits_closed_candle(self):
        from data.websocket_feed import WebSocketFeed

        feed = WebSocketFeed(["BTC/USDT"])
        feed._running = True

        ohlcv_a = [1_000_000, 40_000, 40_500, 39_800, 40_200, 1.0]
        ohlcv_b = [2_000_000, 40_200, 40_600, 40_100, 40_400, 0.8]

        call_count = 0

        async def _fake_watch(sym, tf):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [ohlcv_a]
            feed._running = False
            return [ohlcv_b]

        mock_exchange = MagicMock()
        mock_exchange.watch_ohlcv = _fake_watch

        await feed._watch_symbol(mock_exchange, "BTC/USDT")
        # The second call emits the "closed" previous candle
        assert feed._queue.qsize() == 1
        candle = feed._queue.get_nowait()
        assert candle.symbol == "BTC/USDT"
        assert candle.closed is True

    @pytest.mark.asyncio
    async def test_watch_symbol_handles_exception(self):
        """Exception inside watch_ohlcv → logs warning, retries, eventually stops."""
        from data.websocket_feed import WebSocketFeed

        feed = WebSocketFeed(["BTC/USDT"])
        feed._running = True

        call_count = 0

        async def _bad_watch(sym, tf):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("ws disconnect")
            feed._running = False
            return []

        mock_exchange = MagicMock()
        mock_exchange.watch_ohlcv = _bad_watch

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await feed._watch_symbol(mock_exchange, "BTC/USDT")

        assert call_count >= 2  # retried at least once


# ── optuna_optimizer._score ───────────────────────────────────────────────────

class TestOptunaScore:
    def test_negative_sharpe_returns_minus_ten(self):
        from backtesting.optuna_optimizer import _score
        m = {"sharpe": -0.5, "win_rate": 55, "max_drawdown_pct": -10, "profit_factor": 1.2, "total_trades": 40}
        assert _score(m) == -10.0

    def test_zero_sharpe_returns_minus_ten(self):
        from backtesting.optuna_optimizer import _score
        m = {"sharpe": 0.0, "win_rate": 55, "max_drawdown_pct": -10, "profit_factor": 1.2, "total_trades": 40}
        assert _score(m) == -10.0

    def test_positive_sharpe_positive_score(self):
        from backtesting.optuna_optimizer import _score
        m = {"sharpe": 2.0, "win_rate": 60, "max_drawdown_pct": -5, "profit_factor": 2.0, "total_trades": 50}
        score = _score(m)
        assert score > 0

    def test_high_drawdown_penalises_score(self):
        from backtesting.optuna_optimizer import _score
        low_dd  = {"sharpe": 1.0, "win_rate": 55, "max_drawdown_pct": -5,  "profit_factor": 1.5, "total_trades": 50}
        high_dd = {"sharpe": 1.0, "win_rate": 55, "max_drawdown_pct": -80, "profit_factor": 1.5, "total_trades": 50}
        assert _score(low_dd) > _score(high_dd)

    def test_few_trades_penalised(self):
        from backtesting.optuna_optimizer import _score
        few   = {"sharpe": 1.0, "win_rate": 60, "max_drawdown_pct": -5, "profit_factor": 1.5, "total_trades": 3}
        many  = {"sharpe": 1.0, "win_rate": 60, "max_drawdown_pct": -5, "profit_factor": 1.5, "total_trades": 80}
        assert _score(many) > _score(few)

    def test_profit_factor_capped_at_3(self):
        from backtesting.optuna_optimizer import _score
        big_pf   = {"sharpe": 1.0, "win_rate": 60, "max_drawdown_pct": -5, "profit_factor": 100, "total_trades": 50}
        cap_pf   = {"sharpe": 1.0, "win_rate": 60, "max_drawdown_pct": -5, "profit_factor": 3,   "total_trades": 50}
        assert _score(big_pf) == pytest.approx(_score(cap_pf), rel=0.01)


# ── optimize() error paths ────────────────────────────────────────────────────

class TestOptimizeErrors:
    def test_optimize_raises_when_optuna_unavailable(self):
        import backtesting.optuna_optimizer as oo
        orig = oo.OPTUNA_AVAILABLE
        oo.OPTUNA_AVAILABLE = False
        try:
            with pytest.raises(RuntimeError, match="optuna"):
                oo.optimize(MagicMock(), pd.DataFrame())
        finally:
            oo.OPTUNA_AVAILABLE = orig

    def test_optimize_raises_for_unknown_strategy(self):
        import backtesting.optuna_optimizer as oo
        orig = oo.OPTUNA_AVAILABLE
        oo.OPTUNA_AVAILABLE = True
        strategy_cls = MagicMock()
        strategy_cls.name = "unknown_xyz"
        try:
            with pytest.raises(ValueError, match="No param space"):
                oo.optimize(strategy_cls, pd.DataFrame({"a": [1]}),
                            strategy_name="unknown_xyz")
        finally:
            oo.OPTUNA_AVAILABLE = orig


# ── PARAM_SPACES coverage ─────────────────────────────────────────────────────

class TestParamSpaces:
    def test_all_param_spaces_callable(self):
        from backtesting.optuna_optimizer import PARAM_SPACES
        for name, fn in PARAM_SPACES.items():
            mock_trial = MagicMock()
            mock_trial.suggest_int.return_value   = 10
            mock_trial.suggest_float.return_value = 0.5
            result = fn(mock_trial)
            assert isinstance(result, dict), f"PARAM_SPACES[{name!r}] must return dict"
            assert len(result) > 0


# ── optuna_importance_chart ───────────────────────────────────────────────────

class TestOptunaImportanceChart:
    def test_chart_no_op_without_optuna(self, tmp_path):
        import backtesting.optuna_optimizer as oo
        orig = oo.OPTUNA_AVAILABLE
        oo.OPTUNA_AVAILABLE = False
        try:
            oo.optuna_importance_chart(MagicMock(), output_dir=tmp_path)
        finally:
            oo.OPTUNA_AVAILABLE = orig
        # No files created (early return)
        assert list(tmp_path.glob("*.html")) == []

    def test_chart_exception_silenced(self, tmp_path):
        import backtesting.optuna_optimizer as oo
        orig = oo.OPTUNA_AVAILABLE
        oo.OPTUNA_AVAILABLE = True
        fake_study = MagicMock()
        with patch.dict("sys.modules", {
            "optuna": MagicMock(logging=MagicMock()),
            "optuna.visualization": MagicMock(
                plot_param_importances=MagicMock(side_effect=Exception("no viz")),
                plot_optimization_history=MagicMock(),
            ),
        }):
            try:
                oo.optuna_importance_chart(fake_study, output_dir=tmp_path)
            except Exception:
                pytest.fail("optuna_importance_chart raised unexpectedly")
        oo.OPTUNA_AVAILABLE = orig
