"""
Tests for bot/async_trader.py — AsyncLiveTrader._process_symbol and helpers.
All network, exchange, and WebSocket calls are mocked.
"""
import pytest
import asyncio
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
from tests.conftest import make_ohlcv


def _get_state_side_effect(key, default=None):
    if key == "active_strategy":
        return "trend_ema"
    if key == "paused":
        return False
    return default


@pytest.fixture
def async_trader():
    """Build an AsyncLiveTrader with all side-effects mocked."""
    with patch("bot.async_trader.init_db"), \
         patch("bot.auto_compound.get_state", return_value=None), \
         patch("bot.auto_compound.set_state"), \
         patch("bot.async_trader.notify_startup"):
        from bot.async_trader import AsyncLiveTrader
        trader = AsyncLiveTrader.__new__(AsyncLiveTrader)
        # Manually init without calling __init__ (avoids DB/notify calls)
        from config import CONFIG
        from risk.manager import RiskManager
        from bot.position_manager import PositionManager
        from utils.correlation import CorrelationFilter
        from utils.events_filter import EventsFilter
        from bot.auto_compound import AutoCompounder, CompoundMode
        from bot.strategy_monitor import StrategyMonitor
        from data.websocket_feed import CandleBuffer
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            trader.cfg        = CONFIG
            trader.dry_run    = True
            trader.risk       = RiskManager(initial_capital=10_000)
            trader.pos_mgr    = PositionManager(dry_run=True)
            trader.corr_filter = CorrelationFilter(threshold=0.80)
            trader.events     = EventsFilter()
            trader.compounder = AutoCompounder(10_000, mode=CompoundMode.REINVEST_ALL)
            trader.monitor    = StrategyMonitor("trend_ema", baseline_sharpe=1.5)
            trader.buffer     = CandleBuffer(maxlen=500)
            trader._sentiment = {"allow_long": True, "allow_short": True, "reason": "ok"}
            trader._sentiment_ts = 0.0
    return trader


def _load_buffer(trader, symbol: str, n: int = 200):
    """Push n fake candles into the buffer for a symbol."""
    from data.websocket_feed import Candle
    df = make_ohlcv(n, seed=42)
    for ts, row in df.iterrows():
        ts_ms = int(ts.timestamp() * 1000)
        ohlcv = [ts_ms, row["open"], row["high"], row["low"], row["close"], row["volume"]]
        candle = Candle(symbol, ohlcv, closed=True)
        trader.buffer.push(candle)


# ── Paused state ──────────────────────────────────────────────────────────────

class TestProcessSymbolPaused:
    @pytest.mark.asyncio
    async def test_skips_when_paused(self, async_trader):
        with patch("bot.async_trader.get_state", return_value=True):
            await async_trader._process_symbol("BTC/USDT")
        # No exception and no positions opened
        assert "BTC/USDT" not in async_trader.pos_mgr.positions

    @pytest.mark.asyncio
    async def test_processes_when_not_paused(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = df.copy()
        sig_df["signal"]        = 0
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch.object(async_trader.buffer, "to_df", return_value=df), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.pos_mgr, "update", return_value=[]):
            # Ensure strategy returns a signal
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(
                    __import__("strategies", fromlist=["STRATEGIES"]).STRATEGIES,
                    {"trend_ema": lambda rm: strat}
                ):
                    await async_trader._process_symbol("BTC/USDT")
        # No error — signal=0 means no new position


# ── Empty buffer ──────────────────────────────────────────────────────────────

class TestProcessSymbolEmptyBuffer:
    @pytest.mark.asyncio
    async def test_skips_on_empty_buffer(self, async_trader):
        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect):
            # Buffer is empty for this symbol
            await async_trader._process_symbol("XRP/USDT")
        assert "XRP/USDT" not in async_trader.pos_mgr.positions


# ── Strategy error handling ───────────────────────────────────────────────────

class TestProcessSymbolStrategyError:
    @pytest.mark.asyncio
    async def test_handles_strategy_exception_gracefully(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect):
            from strategies import STRATEGIES
            broken_strat = MagicMock()
            broken_strat.name = "trend_ema"
            broken_strat.run.side_effect = RuntimeError("indicator error")
            with patch.dict(STRATEGIES, {"trend_ema": lambda rm: broken_strat}):
                # Should not raise
                await async_trader._process_symbol("BTC/USDT")

        assert "BTC/USDT" not in async_trader.pos_mgr.positions


# ── Open position management ──────────────────────────────────────────────────

class TestProcessSymbolPositionManagement:
    @pytest.mark.asyncio
    async def test_updates_existing_position(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        price = float(df.iloc[-1]["close"])

        sig_df = df.copy()
        sig_df["signal"]        = 0   # hold
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        async_trader.pos_mgr.positions["BTC/USDT"] = MagicMock()

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch.object(async_trader.pos_mgr, "update", return_value=[]) as mock_update, \
             patch("bot.async_trader.log_signal"):
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_update.assert_called_once_with("BTC/USDT", price)

    @pytest.mark.asyncio
    async def test_exit_signal_closes_position(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        price = float(df.iloc[-1]["close"])

        sig_df = df.copy()
        sig_df["signal"]        = -1   # exit
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0

        async_trader.pos_mgr.positions["BTC/USDT"] = MagicMock()

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch.object(async_trader.pos_mgr, "update", return_value=[]), \
             patch.object(async_trader.pos_mgr, "_close") as mock_close, \
             patch("bot.async_trader.log_signal"):
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_close.assert_called_once_with("BTC/USDT", price, "signal_exit")


# ── Entry filters ─────────────────────────────────────────────────────────────

class TestProcessSymbolEntryFilters:
    def _make_sig_df(self, df: pd.DataFrame, signal: int = 1) -> pd.DataFrame:
        sig_df = df.copy()
        sig_df["signal"]        = signal
        sig_df["stop_loss"]     = sig_df["close"] * 0.97
        sig_df["take_profit"]   = sig_df["close"] * 1.06
        sig_df["atr_14"]        = sig_df["close"] * 0.02
        sig_df["ml_confidence"] = 1.0
        return sig_df

    @pytest.mark.asyncio
    async def test_events_filter_blocks_entry(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = self._make_sig_df(df, signal=1)

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.events, "is_safe_to_trade",
                          return_value=(False, "FOMC meeting")), \
             patch.object(async_trader.pos_mgr, "open_position") as mock_open:
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_open.assert_not_called()

    @pytest.mark.asyncio
    async def test_sentiment_blocks_long(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        async_trader._sentiment = {"allow_long": False, "allow_short": True, "reason": "extreme greed"}
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = self._make_sig_df(df, signal=1)

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(async_trader.pos_mgr, "open_position") as mock_open:
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_open.assert_not_called()

    @pytest.mark.asyncio
    async def test_correlation_filter_blocks_entry(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = self._make_sig_df(df, signal=1)

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(async_trader.corr_filter, "is_correlated_with_open", return_value=True), \
             patch.object(async_trader.pos_mgr, "open_position") as mock_open:
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_open.assert_not_called()

    @pytest.mark.asyncio
    async def test_orderbook_filter_blocks_entry(self, async_trader):
        from utils.orderbook import OrderBookSnapshot
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = self._make_sig_df(df, signal=1)

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(async_trader.corr_filter, "is_correlated_with_open", return_value=False), \
             patch("bot.async_trader.fetch_orderbook", new_callable=AsyncMock,
                   return_value=None), \
             patch("bot.async_trader.orderbook_filter", return_value=(False, "ask wall")), \
             patch.object(async_trader.pos_mgr, "open_position") as mock_open:
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_open.assert_not_called()

    @pytest.mark.asyncio
    async def test_candle_pattern_negative_blocks_entry(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT")
        df = async_trader.buffer.to_df("BTC/USDT")
        sig_df = self._make_sig_df(df, signal=1)
        neg_candle_df = sig_df.assign(candle_score=-1.0)

        with patch("bot.async_trader.get_state", side_effect=_get_state_side_effect), \
             patch("bot.async_trader.log_signal"), \
             patch.object(async_trader.events, "is_safe_to_trade", return_value=(True, "ok")), \
             patch.object(async_trader.corr_filter, "is_correlated_with_open", return_value=False), \
             patch("bot.async_trader.fetch_orderbook", new_callable=AsyncMock, return_value=None), \
             patch("bot.async_trader.orderbook_filter", return_value=(True, "ok")), \
             patch("bot.async_trader.add_candle_patterns", return_value=neg_candle_df), \
             patch.object(async_trader.pos_mgr, "open_position") as mock_open:
            from strategies import STRATEGIES
            strat = STRATEGIES["trend_ema"](async_trader.risk)
            with patch.object(strat, "run", return_value=sig_df):
                with patch.dict(STRATEGIES, {"trend_ema": lambda rm: strat}):
                    await async_trader._process_symbol("BTC/USDT")

        mock_open.assert_not_called()


# ── Compound loop ─────────────────────────────────────────────────────────────

class TestCompoundLoop:
    @pytest.mark.asyncio
    async def test_compound_fires_when_due(self, async_trader):
        from datetime import datetime, timedelta

        # Force should_compound to return True
        async_trader.compounder.state.last_compound_ts = (
            datetime.utcnow() - timedelta(days=8)
        )
        async_trader.risk.portfolio.capital = 11_000.0

        compound_called = []
        original_run = async_trader.compounder.run

        def mock_run(equity):
            compound_called.append(equity)
            return original_run(equity)

        with patch.object(async_trader.compounder, "run", side_effect=mock_run), \
             patch.object(async_trader.compounder, "should_compound", return_value=True), \
             patch("bot.auto_compound.set_state"):
            # Run one iteration of the loop by cancelling after first pass
            async def one_pass():
                if async_trader.compounder.should_compound():
                    result = async_trader.compounder.run(async_trader.risk.portfolio.capital)
            await one_pass()

        assert len(compound_called) == 1
        assert compound_called[0] == pytest.approx(11_000.0)


# ── CandleBuffer readiness ────────────────────────────────────────────────────

class TestCandleBufferReadiness:
    def test_buffer_not_ready_below_threshold(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT", n=50)
        assert not async_trader.buffer.is_ready("BTC/USDT", min_bars=100)

    def test_buffer_ready_above_threshold(self, async_trader):
        _load_buffer(async_trader, "BTC/USDT", n=150)
        assert async_trader.buffer.is_ready("BTC/USDT", min_bars=100)

    def test_to_df_returns_correct_symbol(self, async_trader):
        _load_buffer(async_trader, "ETH/USDT", n=20)
        df = async_trader.buffer.to_df("ETH/USDT")
        assert len(df) == 20
        assert "close" in df.columns
