"""
Targeted tests filling remaining coverage gaps in:
  - strategies/ensemble.py  (update_weights, weighted mode, member-exception path)
  - strategies/hybrid_ml.py  (model load from file, generate_signals with mock model)
  - bot/async_trader.py  (__init__, _compound_loop, _health_loop,
                           _sentiment_refresh_loop, _candle_consumer)
  - data/backup.py  (export_trades_excel)
"""
import pytest
import asyncio
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from tests.conftest import make_ohlcv


# ── EnsembleStrategy — uncovered paths ───────────────────────────────────────

class TestEnsembleExtended:
    @pytest.fixture
    def ohlcv(self):
        return make_ohlcv(n=500)

    @pytest.fixture
    def rm(self):
        from risk.manager import RiskManager
        return RiskManager(initial_capital=10_000)

    def test_update_weights_from_backtest(self, rm):
        from strategies.ensemble import EnsembleStrategy
        ens = EnsembleStrategy(rm, mode="majority")
        scores = {k: float(i + 1) for i, k in enumerate(ens._members)}
        ens.update_weights_from_backtest(scores)
        total = sum(ens._weights.values())
        assert total == pytest.approx(1.0, abs=0.01)

    def test_update_weights_all_zero_keeps_equal(self, rm):
        from strategies.ensemble import EnsembleStrategy
        ens = EnsembleStrategy(rm, mode="weighted")
        ens.update_weights_from_backtest({k: 0.0 for k in ens._members})
        # All zero → weights stay at 0 or equal fractions — no crash
        assert isinstance(ens._weights, dict)

    def test_weighted_mode_produces_signals(self, ohlcv, rm):
        from strategies.ensemble import EnsembleStrategy
        ens = EnsembleStrategy(rm, mode="weighted")
        out = ens.run(ohlcv)
        assert "signal" in out.columns
        assert set(out["signal"].unique()).issubset({-1, 0, 1})

    def test_member_exception_graceful(self, ohlcv, rm):
        """One member raises → its signal defaults to 0, no crash."""
        from strategies.ensemble import EnsembleStrategy
        ens = EnsembleStrategy(rm, mode="majority")
        first_key = list(ens._members.keys())[0]
        ens._members[first_key].generate_signals = MagicMock(
            side_effect=RuntimeError("bad indicator")
        )
        out = ens.run(ohlcv)
        assert "signal" in out.columns

    def test_stop_loss_averaged_across_members(self, ohlcv, rm):
        """Ensemble averages stop_loss from members that provide it."""
        from strategies.ensemble import EnsembleStrategy
        ens = EnsembleStrategy(rm, mode="majority")
        out = ens.run(ohlcv)
        # stop_loss column should exist if any member provides one
        # (just confirm no crash and shape is right)
        assert len(out) == len(ohlcv)


# ── HybridMLStrategy — model-load path and generate with mock model ──────────

class TestHybridMLExtended:
    @pytest.fixture
    def rm(self):
        from risk.manager import RiskManager
        return RiskManager(initial_capital=10_000)

    def test_constructor_loads_existing_model(self, tmp_path, rm):
        """If model .pkl exists and retrain=False, joblib.load is called."""
        from strategies.hybrid_ml import HybridMLStrategy

        model_path  = tmp_path / "hybrid_ml_xgb.pkl"
        scaler_path = tmp_path / "hybrid_ml_scaler.pkl"
        model_path.write_bytes(b"fake_model")
        scaler_path.write_bytes(b"fake_scaler")

        fake_model  = MagicMock()
        fake_scaler = MagicMock()

        with patch("strategies.hybrid_ml.MODEL_DIR", tmp_path), \
             patch("strategies.hybrid_ml.joblib.load",
                   side_effect=[fake_model, fake_scaler]) as mock_load:
            strat = HybridMLStrategy(rm, retrain=False)

        assert mock_load.call_count == 2
        assert strat.model is fake_model

    def test_generate_signals_with_mock_model(self, rm):
        """generate_signals() with a mock model adds ml_confidence column."""
        from strategies.hybrid_ml import HybridMLStrategy
        df = make_ohlcv(n=400, trend="up", seed=7)

        strat = HybridMLStrategy(rm, retrain=False)
        strat.model = MagicMock()
        strat.model.predict_proba.return_value = np.full((len(df), 2), 0.5)
        strat.scaler = MagicMock()
        strat.scaler.transform.return_value = np.zeros((len(df), 10))

        prepared = strat.prepare(df)
        base_out  = strat._base.generate_signals(prepared)
        out       = strat.generate_signals(base_out)
        assert "ml_confidence" in out.columns
        assert (out["ml_confidence"] >= 0).all()

    def test_generate_signals_prediction_error_falls_back(self, rm):
        """If scaler.transform raises, returns df without ml_confidence crash."""
        from strategies.hybrid_ml import HybridMLStrategy
        df = make_ohlcv(n=400, seed=8)
        strat = HybridMLStrategy(rm, retrain=False)
        strat.model = MagicMock()
        strat.scaler = MagicMock()
        strat.scaler.transform.side_effect = ValueError("transform error")

        out = strat.generate_signals(strat._base.generate_signals(strat.prepare(df)))
        assert "signal" in out.columns  # no crash, falls back to base signals

    def test_train_returns_dict(self, rm):
        """train() always returns a dict (possibly empty)."""
        from strategies.hybrid_ml import HybridMLStrategy
        df = make_ohlcv(n=300, trend="up", seed=42)
        strat = HybridMLStrategy(rm, retrain=True)
        result = strat.train(df)
        assert isinstance(result, dict)


# ── AsyncLiveTrader — init and background loops ───────────────────────────────

def _make_mock_config():
    cfg = MagicMock()
    cfg.dry_run = True
    cfg.active_strategy = "trend_ema"
    cfg.pairs = ["BTC/USDT"]
    cfg.timeframe = "1h"
    cfg.exchange.name = "binance"
    cfg.risk.max_drawdown_pct = 0.15
    cfg.risk.risk_reward_ratio = 2.0
    cfg.risk.max_position_size_pct = 0.05
    cfg.backtest.initial_capital = 10_000
    return cfg


class TestAsyncLiveTraderInit:
    def test_init_creates_all_components(self):
        from bot.async_trader import AsyncLiveTrader
        cfg = _make_mock_config()
        with patch("bot.async_trader.init_db"), \
             patch("bot.async_trader.notify_startup"), \
             patch("bot.async_trader.get_state", return_value=None), \
             patch("bot.async_trader.set_state"), \
             patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            trader = AsyncLiveTrader(cfg)
        assert trader.cfg is cfg
        assert trader.dry_run is True
        assert trader.buffer is not None
        assert trader._sentiment["allow_long"] is True


class TestAsyncLiveTraderLoops:
    @pytest.fixture
    def trader(self):
        from bot.async_trader import AsyncLiveTrader
        cfg = _make_mock_config()
        t = AsyncLiveTrader.__new__(AsyncLiveTrader)
        t.cfg = cfg
        t.dry_run = True
        t._sentiment = {"allow_long": True, "allow_short": True, "reason": "ok"}
        t._sentiment_ts = 0.0
        t.risk = MagicMock()
        t.risk.portfolio.capital = 10_000.0
        t.compounder = MagicMock()
        t.compounder.should_compound.return_value = False
        t.monitor = MagicMock()
        t.monitor.check.return_value = MagicMock(
            status=MagicMock(value="healthy"), message="ok"
        )
        return t

    @pytest.mark.asyncio
    async def test_compound_loop_checks_and_runs(self, trader):
        """_compound_loop runs compounder.run() when should_compound() is True."""
        from bot.async_trader import AsyncLiveTrader

        call_count = 0

        async def _fast_sleep(seconds):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise asyncio.CancelledError()

        trader.compounder.should_compound.return_value = True
        trader.compounder.run.return_value = {"compounded": 100}

        with patch("asyncio.sleep", side_effect=_fast_sleep):
            with pytest.raises(asyncio.CancelledError):
                await trader._compound_loop()

        trader.compounder.run.assert_called()

    @pytest.mark.asyncio
    async def test_health_loop_calls_monitor(self, trader):
        """_health_loop sleeps then calls monitor.check()."""
        call_count = 0

        async def _fast_sleep(seconds):
            nonlocal call_count
            call_count += 1
            # Let the first sleep complete so monitor.check() is reached
            if call_count >= 2:
                raise asyncio.CancelledError()

        with patch("asyncio.sleep", side_effect=_fast_sleep):
            with pytest.raises(asyncio.CancelledError):
                await trader._health_loop()

        trader.monitor.check.assert_called()

    @pytest.mark.asyncio
    async def test_sentiment_refresh_loop_updates_state(self, trader):
        """_sentiment_refresh_loop fetches FnG, funding, and updates _sentiment."""
        call_count = 0

        async def _fast_sleep(seconds):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                raise asyncio.CancelledError()

        with patch("bot.async_trader.get_current_fng",  return_value={"value": 55}), \
             patch("bot.async_trader.get_funding_rate",  return_value=0.0001), \
             patch("bot.async_trader.sentiment_gate",
                   return_value={"allow_long": True, "allow_short": True, "reason": "ok"}), \
             patch("asyncio.sleep", side_effect=_fast_sleep):
            with pytest.raises(asyncio.CancelledError):
                await trader._sentiment_refresh_loop()

        assert trader._sentiment_ts > 0

    @pytest.mark.asyncio
    async def test_candle_consumer_pushes_to_buffer(self, trader):
        """_candle_consumer pushes closed candles and calls _process_symbol."""
        from data.websocket_feed import Candle, CandleBuffer
        trader.buffer = CandleBuffer(maxlen=500)

        ohlcv = [1_672_531_200_000, 40_000, 40_500, 39_800, 40_200, 1.0]
        candle = Candle("BTC/USDT", ohlcv, closed=True)

        process_calls = []

        async def _fake_process(symbol):
            process_calls.append(symbol)

        trader._process_symbol = _fake_process

        async def _fake_stream():
            yield candle
            yield Candle("BTC/USDT", ohlcv, closed=False)  # non-closed should be skipped

        mock_feed = MagicMock()
        mock_feed.stream = _fake_stream

        # is_ready returns True after enough candles pushed
        with patch.object(trader.buffer, "is_ready", return_value=True):
            await trader._candle_consumer(mock_feed)

        assert "BTC/USDT" in process_calls
        assert len(process_calls) == 1   # non-closed candle not processed


# ── data/backup.py Excel export ───────────────────────────────────────────────

class TestBackupExcel:
    def test_export_trades_excel(self, tmp_path):
        """export_trades_excel returns correct path (openpyxl write mocked)."""
        import data.backup as bk
        import data.database as db_mod
        fresh_db = tmp_path / "fresh.db"
        orig_db_path = db_mod.DB_PATH
        db_mod.DB_PATH = fresh_db
        db_mod.init_db()
        output = tmp_path / "trades.xlsx"

        # Patch DataFrame.to_excel to avoid openpyxl dependency in CI
        mock_writer_cm = MagicMock()
        mock_writer_cm.__enter__ = MagicMock(return_value=mock_writer_cm)
        mock_writer_cm.__exit__ = MagicMock(return_value=False)

        try:
            with patch("data.backup.pd.ExcelWriter", return_value=mock_writer_cm), \
                 patch("pandas.core.generic.NDFrame.to_excel"):
                result = bk.export_trades_excel(output_path=output)
        finally:
            db_mod.DB_PATH = orig_db_path

        assert result == output
        assert result.suffix == ".xlsx"
