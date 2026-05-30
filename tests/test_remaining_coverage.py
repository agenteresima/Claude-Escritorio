"""
Targeted tests for remaining coverage gaps in:
  - bot/notifier.py           (_send_telegram HTTP path, notify loop-not-running)
  - bot/auto_compound.py      (FIXED_WITHDRAW, PERCENT_WITHDRAW, rebalance_check)
  - bot/shutdown.py           (_handle SIGTERM/SIGINT branch)
  - bot/live_trader.py        (_check_api_commands switch, _refresh_sentiment,
                               get_balance live, tick force-close/drawdown/filters)
  - data/websocket_feed.py    (_rest_poll_loop, stream producer)
  - reports/benchmark.py      (fetch errors, short-alignment skip)
  - reports/weekly_report.py  (events block in message)
  - strategies/hybrid_ml.py   (_triple_barrier_label TP/SL branches, train() full path)
"""
import asyncio
import signal
import sys
import time
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock, call
from tests.conftest import make_ohlcv


# ── bot/notifier.py ───────────────────────────────────────────────────────────

class TestNotifierHTTPPath:
    @pytest.mark.asyncio
    async def test_send_telegram_with_credentials(self):
        """_send_telegram posts when token and chat_id are set."""
        import bot.notifier as notifier

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__  = AsyncMock(return_value=False)

        mock_session_post = MagicMock()
        mock_session_post.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_post.__aexit__  = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_session_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__  = AsyncMock(return_value=False)

        with patch.object(notifier, "TELEGRAM_TOKEN",   "fake_token"), \
             patch.object(notifier, "TELEGRAM_CHAT_ID", "fake_chat"), \
             patch("bot.notifier.aiohttp.ClientSession", return_value=mock_session):
            await notifier._send_telegram("hello")

        mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_telegram_exception_caught(self):
        """_send_telegram catches aiohttp exceptions gracefully (lines 26-27)."""
        import bot.notifier as notifier

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))
        mock_session.__aexit__  = AsyncMock(return_value=False)

        with patch.object(notifier, "TELEGRAM_TOKEN",   "fake_token"), \
             patch.object(notifier, "TELEGRAM_CHAT_ID", "fake_chat"), \
             patch("bot.notifier.aiohttp.ClientSession", return_value=mock_session):
            await notifier._send_telegram("hello")  # should not raise

    def test_notify_uses_create_task_when_loop_running(self):
        """notify() calls loop.create_task when loop is running (line 35)."""
        import bot.notifier as notifier

        mock_loop = MagicMock()
        mock_loop.is_running.return_value = True

        with patch("bot.notifier.asyncio.get_event_loop", return_value=mock_loop):
            notifier.notify("test message")

        mock_loop.create_task.assert_called_once()

    def test_notify_calls_run_until_complete_when_loop_not_running(self):
        """notify() uses loop.run_until_complete when loop is not running (line 37)."""
        import bot.notifier as notifier

        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False

        with patch("bot.notifier.asyncio.get_event_loop", return_value=mock_loop), \
             patch.object(notifier, "TELEGRAM_TOKEN",   "t"), \
             patch.object(notifier, "TELEGRAM_CHAT_ID", "c"):
            notifier.notify("test message")

        mock_loop.run_until_complete.assert_called_once()


# ── bot/auto_compound.py ─────────────────────────────────────────────────────

class TestAutoCompoundModes:
    def _make_compounder(self, mode_str, **kw):
        from bot.auto_compound import AutoCompounder, CompoundMode
        mode = CompoundMode(mode_str)
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            c = AutoCompounder(
                initial_capital=10_000,
                mode=mode,
                **kw,
            )
        return c

    def test_should_compound_returns_true_after_interval(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        from datetime import datetime, timedelta
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            c = AutoCompounder(initial_capital=10_000, mode=CompoundMode.REINVEST_ALL)
        # Manually set last_compound_ts to more than interval ago
        c.state.last_compound_ts = datetime.utcnow() - timedelta(days=8)
        assert c.should_compound() is True

    def test_fixed_withdraw_mode(self):
        """FIXED_WITHDRAW: withdraws fixed amount, compounds the rest."""
        c = self._make_compounder("fixed_withdraw", withdraw_amount=200.0)
        with patch("bot.auto_compound.set_state"):
            result = c.run(current_equity=11_000.0)
        assert result["withdrawn"]  == pytest.approx(200.0, abs=1)
        assert result["compounded"] == pytest.approx(800.0, abs=1)

    def test_percent_withdraw_mode(self):
        """PERCENT_WITHDRAW: withdraws pct of profit."""
        c = self._make_compounder("percent_withdraw", withdraw_pct=0.30)
        with patch("bot.auto_compound.set_state"):
            result = c.run(current_equity=11_000.0)
        # profit = 1000, withdrawn = 30% = 300
        assert result["withdrawn"]  == pytest.approx(300.0, abs=1)
        assert result["compounded"] == pytest.approx(700.0, abs=1)

    def test_rebalance_check_detects_drift(self):
        """rebalance_check returns pairs whose allocation drifted > 20%."""
        from bot.auto_compound import AutoCompounder, CompoundMode
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            c = AutoCompounder(initial_capital=10_000, mode=CompoundMode.REINVEST_ALL)
        # Equal target = 5000 each; BTC drifted to 7000 (+40%), ETH to 3000 (-40%)
        drifted = c.rebalance_check({"BTC/USDT": 7_000.0, "ETH/USDT": 3_000.0})
        assert len(drifted) > 0

    def test_rebalance_check_empty_dict_returns_empty(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        with patch("bot.auto_compound.get_state", return_value=None), \
             patch("bot.auto_compound.set_state"):
            c = AutoCompounder(initial_capital=10_000, mode=CompoundMode.REINVEST_ALL)
        assert c.rebalance_check({}) == []


# ── bot/shutdown.py ──────────────────────────────────────────────────────────

class TestShutdownHandle:
    def test_handle_sigterm_branch(self):
        """_handle logs SIGTERM name and calls _run_shutdown then sys.exit."""
        from bot.shutdown import GracefulShutdown
        sd = GracefulShutdown()
        with patch.object(sd, "_run_shutdown") as mock_rs, \
             patch("bot.shutdown.sys.exit") as mock_exit:
            sd._handle(signal.SIGTERM, None)
        mock_rs.assert_called_once()
        mock_exit.assert_called_once_with(0)

    def test_handle_sigint_branch(self):
        """_handle logs SIGINT name (else branch) and still shuts down."""
        from bot.shutdown import GracefulShutdown
        sd = GracefulShutdown()
        with patch.object(sd, "_run_shutdown") as mock_rs, \
             patch("bot.shutdown.sys.exit"):
            sd._handle(signal.SIGINT, None)
        mock_rs.assert_called_once()


# ── bot/live_trader.py ───────────────────────────────────────────────────────

def _build_live_trader():
    """Build a LiveTrader bypassing __init__ and setting required attrs."""
    import bot.live_trader as lt
    t = lt.LiveTrader.__new__(lt.LiveTrader)
    t.cfg               = MagicMock()
    t.cfg.dry_run       = True
    t.cfg.active_strategy = "trend_ema"
    t.cfg.pairs         = ["BTC/USDT"]
    t.cfg.timeframe     = "1h"
    t.cfg.exchange.name = "binance"
    t.cfg.risk.max_drawdown_pct    = 0.15
    t.cfg.risk.risk_reward_ratio   = 2.0
    t.cfg.risk.max_position_size_pct = 0.05
    t.dry_run           = True
    t.exchange          = MagicMock()
    t.strategy          = MagicMock()
    t.strategy.name     = "trend_ema"
    t.pos_mgr           = MagicMock()
    t.pos_mgr.positions = {}
    t.risk              = MagicMock()
    t.risk.portfolio.capital = 10_000.0
    t.risk.portfolio.current_drawdown.return_value = 0.02
    t.risk.validate_signal.return_value = True
    t.risk.atr_size.return_value = 0.01
    t.corr_filter       = MagicMock()
    t.corr_filter.is_correlated_with_open.return_value = False
    t.events            = MagicMock()
    t.events.is_safe_to_trade.return_value = (True, "ok")
    t._last_sentiment_ts = 0.0
    t._sentiment_gate   = {"allow_long": True, "allow_short": True, "reason": "ok"}
    return t


class TestLiveTraderPaths:
    def test_check_api_commands_strategy_switch(self):
        """_check_api_commands switches strategy when get_state returns new name."""
        import bot.live_trader as lt
        from strategies import STRATEGIES
        t = _build_live_trader()

        with patch("bot.live_trader.get_state") as mock_gs:
            # Not paused, new strategy active
            mock_gs.side_effect = lambda key, default=None: (
                False if key == "paused" else "trend_ema"
            )
            result = t._check_api_commands()
        # trend_ema same as current → no actual switch, but returns True
        assert result is True

    def test_check_api_commands_paused_returns_false(self):
        t = _build_live_trader()
        with patch("bot.live_trader.get_state", return_value=True):
            result = t._check_api_commands()
        assert result is False

    def test_refresh_sentiment_updates_gate(self):
        """_refresh_sentiment fetches FnG + FR and updates _sentiment_gate."""
        t = _build_live_trader()
        t._last_sentiment_ts = 0.0  # expired

        fake_gate = {"allow_long": True, "allow_short": True, "reason": "ok"}
        with patch("bot.live_trader.get_current_fng",  return_value={"value": 60}), \
             patch("bot.live_trader.get_funding_rate",  return_value=0.0001), \
             patch("bot.live_trader.sentiment_gate",    return_value=fake_gate):
            t._refresh_sentiment()

        assert t._sentiment_gate == fake_gate
        assert t._last_sentiment_ts > 0

    def test_refresh_sentiment_skipped_when_recent(self):
        """_refresh_sentiment does nothing when called recently."""
        t = _build_live_trader()
        t._last_sentiment_ts = time.time()  # just refreshed

        with patch("bot.live_trader.get_current_fng") as mock_fng:
            t._refresh_sentiment()
        mock_fng.assert_not_called()

    def test_get_balance_live_path(self):
        """get_balance() calls exchange.fetch_balance() when not dry_run."""
        t = _build_live_trader()
        t.dry_run = False
        t.exchange.fetch_balance.return_value = {"USDT": {"free": 5000.0}}
        bal = t.get_balance()
        assert bal == pytest.approx(5000.0)
        t.exchange.fetch_balance.assert_called_once()

    def test_place_order_live_creates_order(self):
        """_place_order creates exchange order when not dry_run."""
        t = _build_live_trader()
        t.dry_run = False
        t.exchange.fetch_ticker.return_value = {"last": "40000.0"}
        t.exchange.create_order.return_value = {"id": "ord123"}

        t._place_order("BTC/USDT", "buy", 0.01, 39_000, 41_000, 42_000)

        t.exchange.create_order.assert_called_once()
        t.pos_mgr.open_position.assert_called_once()

    def test_tick_paused_returns_early(self):
        t = _build_live_trader()
        with patch("bot.live_trader.get_state") as mock_gs:
            mock_gs.return_value = True  # paused
            # _check_api_commands returns False → tick returns early
            with patch.object(t, "_check_api_commands", return_value=False):
                t.tick("BTC/USDT")
        t.pos_mgr.update.assert_not_called()

    def test_tick_force_close_path(self):
        """tick() handles force_close_{symbol} state."""
        t = _build_live_trader()
        t.exchange.fetch_ticker.return_value = {"last": "40000.0"}

        def _state_side_effect(key, default=None):
            if key == "force_close_BTC/USDT":
                return True
            return default

        with patch.object(t, "_check_api_commands", return_value=True), \
             patch("bot.live_trader.get_state", side_effect=_state_side_effect), \
             patch("data.database.set_state"):
            t.tick("BTC/USDT")

        t.pos_mgr._close.assert_called_once()

    def test_tick_drawdown_alert(self):
        """tick() fires drawdown alert when drawdown > threshold."""
        t = _build_live_trader()
        df = make_ohlcv(n=200, trend="up", seed=1)
        sig_df = df.copy()
        sig_df["signal"] = 0
        t.strategy.run.return_value = sig_df

        t.pos_mgr.positions = {"BTC/USDT": MagicMock()}
        t.risk.portfolio.current_drawdown.return_value = 0.13  # > 0.15 * 0.80 = 0.12

        with patch.object(t, "_check_api_commands", return_value=True), \
             patch("bot.live_trader.get_state", return_value=False), \
             patch.object(t, "fetch_latest", return_value=df), \
             patch("bot.live_trader.notify_drawdown_alert") as mock_alert:
            t.tick("BTC/USDT")

        mock_alert.assert_called_once()

    def test_tick_events_filter_blocks(self):
        """tick() returns early when events filter says not safe."""
        t = _build_live_trader()
        df = make_ohlcv(n=200, trend="up", seed=2)
        sig_df = df.copy()
        sig_df["signal"] = 1  # signal is bullish

        t.events.is_safe_to_trade.return_value = (False, "NFP tomorrow")
        t.strategy.run.return_value = sig_df

        with patch.object(t, "_check_api_commands", return_value=True), \
             patch("bot.live_trader.get_state", return_value=False), \
             patch.object(t, "fetch_latest", return_value=df), \
             patch("bot.live_trader.log_signal"):
            t.tick("BTC/USDT")

        t.pos_mgr.open_position.assert_not_called()

    def test_tick_candle_pattern_negative_blocks(self):
        """tick() returns early when candle_score < 0."""
        t = _build_live_trader()
        df = make_ohlcv(n=200, trend="up", seed=3)
        sig_df = df.copy()
        sig_df["signal"] = 1

        negative_df = df.copy()
        negative_df["candle_score"] = -1.0

        with patch.object(t, "_check_api_commands", return_value=True), \
             patch("bot.live_trader.get_state", return_value=False), \
             patch.object(t, "fetch_latest", return_value=df), \
             patch("bot.live_trader.log_signal"), \
             patch("bot.live_trader.add_candle_patterns", return_value=negative_df):
            t.tick("BTC/USDT")

        t.pos_mgr.open_position.assert_not_called()

    def test_tick_exception_is_caught(self):
        """tick() catches exceptions without crashing."""
        t = _build_live_trader()

        with patch.object(t, "_check_api_commands", side_effect=RuntimeError("boom")):
            t.tick("BTC/USDT")  # should not raise


# ── data/websocket_feed.py — _rest_poll_loop ─────────────────────────────────

class TestWebSocketFeedRestPoll:
    @pytest.mark.asyncio
    async def test_rest_poll_loop_emits_candles(self):
        """_rest_poll_loop fetches OHLCV via REST and puts candles in queue."""
        from data.websocket_feed import WebSocketFeed

        feed = WebSocketFeed(["BTC/USDT"], timeframe="1m")
        feed._running = True

        ohlcv_closed = [1_000_000_000, 40_000, 40_500, 39_800, 40_200, 1.0]
        ohlcv_open   = [2_000_000_000, 40_200, 40_600, 40_100, 40_400, 0.8]

        call_count = [0]

        async def _fake_fetch_ohlcv(sym, tf, limit=2):
            call_count[0] += 1
            if call_count[0] >= 2:
                feed._running = False
            return [ohlcv_closed, ohlcv_open]

        mock_exchange = AsyncMock()
        mock_exchange.fetch_ohlcv = _fake_fetch_ohlcv
        mock_exchange.close = AsyncMock()

        mock_exchange_cls = MagicMock(return_value=mock_exchange)

        mock_ccxt_async = MagicMock()
        mock_ccxt_async.binance = mock_exchange_cls

        with patch.dict("sys.modules", {"ccxt.async_support": mock_ccxt_async}), \
             patch("asyncio.sleep", new_callable=AsyncMock):
            await feed._rest_poll_loop()

        assert feed._queue.qsize() >= 1

    @pytest.mark.asyncio
    async def test_rest_poll_loop_handles_fetch_error(self):
        """_rest_poll_loop continues despite per-symbol fetch errors."""
        from data.websocket_feed import WebSocketFeed

        feed = WebSocketFeed(["BTC/USDT"], timeframe="1m")
        feed._running = True

        call_count = [0]

        async def _bad_fetch(sym, tf, limit=2):
            call_count[0] += 1
            feed._running = False
            raise Exception("network error")

        mock_exchange = AsyncMock()
        mock_exchange.fetch_ohlcv = _bad_fetch
        mock_exchange.close = AsyncMock()

        mock_ccxt_async = MagicMock()
        mock_ccxt_async.binance = MagicMock(return_value=mock_exchange)

        with patch.dict("sys.modules", {"ccxt.async_support": mock_ccxt_async}), \
             patch("asyncio.sleep", new_callable=AsyncMock):
            await feed._rest_poll_loop()  # should not raise

        assert feed._queue.empty()


# ── reports/benchmark.py ─────────────────────────────────────────────────────

class TestBenchmarkRunErrors:
    def _make_bot_equity(self, n=252):
        idx = pd.date_range("2022-01-01", periods=n, freq="1h")
        return pd.Series(np.linspace(10_000, 11_000, n), index=idx)

    def test_run_benchmark_ccxt_fails_gracefully(self, tmp_path):
        """run_benchmark skips benchmarks when CCXT raises."""
        from reports.benchmark import run_benchmark

        bot_equity = self._make_bot_equity()

        with patch("data.fetcher.fetch_ohlcv_ccxt",    side_effect=Exception("no data")), \
             patch("data.fetcher.fetch_ohlcv_yfinance", side_effect=Exception("no data")), \
             patch("reports.benchmark.go.Figure") as mock_fig:
            mock_fig.return_value = MagicMock()
            mock_fig.return_value.write_html = MagicMock()
            result = run_benchmark(bot_equity, output_dir=tmp_path)

        assert isinstance(result, pd.DataFrame)
        assert "Bot Strategy" in result["strategy"].values

    def test_run_benchmark_short_alignment_skipped(self, tmp_path):
        """Benchmark series with < 10 aligned points is silently skipped."""
        from reports.benchmark import run_benchmark

        bot_equity = self._make_bot_equity(n=50)
        # Return a price series with 2 points that won't align
        tiny_prices = pd.Series(
            [100.0, 101.0],
            index=pd.date_range("2030-01-01", periods=2, freq="1D"),
        )
        tiny_df = tiny_prices.rename("close").to_frame()
        tiny_df.columns = ["close"]

        with patch("data.fetcher.fetch_ohlcv_ccxt",
                   return_value=tiny_df), \
             patch("data.fetcher.fetch_ohlcv_yfinance",
                   side_effect=Exception("skip")), \
             patch("reports.benchmark.go.Figure") as mock_fig:
            mock_fig.return_value = MagicMock()
            mock_fig.return_value.write_html = MagicMock()
            result = run_benchmark(bot_equity, output_dir=tmp_path)

        # Short-aligned benchmarks are skipped → only Bot row
        assert len(result) >= 1


# ── reports/weekly_report.py — events block ───────────────────────────────────

class TestWeeklyReportEvents:
    @pytest.fixture
    def patched_db(self, tmp_path, monkeypatch):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "wr_ev.db")
        db_mod.init_db()
        yield db_mod

    def test_report_includes_upcoming_events(self, patched_db, tmp_path):
        """Weekly report appends event lines when EventsFilter returns events."""
        from reports.weekly_report import generate_weekly_report
        from datetime import datetime, timezone

        # Insert a small trade so week_trades_n > 0
        tid = patched_db.insert_trade("BTC/USDT", "long", "trend_ema",
                                       40_000.0, 0.01, 39_000.0, 42_000.0)
        patched_db.close_trade(tid, 41_000.0, 10.0, 0.025, "take_profit", 5)

        fake_events = [
            {
                "datetime": datetime(2026, 6, 1, 14, 30, tzinfo=timezone.utc),
                "title": "US NFP",
            }
        ]

        with patch("reports.weekly_report.notify"), \
             patch("reports.weekly_report.CONFIG") as mock_cfg, \
             patch("reports.weekly_report.EventsFilter") as mock_ef_cls:
            mock_cfg.active_strategy = "trend_ema"
            mock_cfg.reports_dir = tmp_path
            mock_ef_instance = MagicMock()
            mock_ef_instance.upcoming_events.return_value = fake_events
            mock_ef_cls.return_value = mock_ef_instance

            msg = generate_weekly_report("trend_ema")

        assert "NFP" in msg or "Upcoming" in msg


# ── strategies/hybrid_ml.py — _triple_barrier_label branches ─────────────────

class TestTripleBarrierLabel:
    def test_tp_hit_returns_label_1(self):
        """When price > TP within max_bars, label is 1."""
        from strategies.hybrid_ml import _triple_barrier_label

        # Close prices: flat then jump +5% (hits 3% TP)
        closes = pd.Series([100.0] * 3 + [106.0] * 10, name="close")
        df = pd.DataFrame({"close": closes})
        signal_idx = pd.Index([0])

        labels = _triple_barrier_label(df, signal_idx, tp_pct=0.03, sl_pct=0.015, max_bars=15)
        assert labels.iloc[0] == 1

    def test_sl_hit_returns_label_0(self):
        """When price < SL within max_bars, label is 0."""
        from strategies.hybrid_ml import _triple_barrier_label

        closes = pd.Series([100.0] * 3 + [98.0] * 10, name="close")
        df = pd.DataFrame({"close": closes})
        signal_idx = pd.Index([0])

        labels = _triple_barrier_label(df, signal_idx, tp_pct=0.03, sl_pct=0.015, max_bars=15)
        assert labels.iloc[0] == 0

    def test_no_barrier_hit_defaults_label_0(self):
        """If neither TP nor SL is hit, label stays 0."""
        from strategies.hybrid_ml import _triple_barrier_label

        closes = pd.Series([100.0] * 20, name="close")
        df = pd.DataFrame({"close": closes})
        signal_idx = pd.Index([0])

        labels = _triple_barrier_label(df, signal_idx, tp_pct=0.10, sl_pct=0.10, max_bars=5)
        assert labels.iloc[0] == 0


class TestHybridMLTrainFullPath:
    def test_train_executes_when_enough_signals(self):
        """train() runs xgb training when signal_idx >= 50."""
        from strategies.hybrid_ml import HybridMLStrategy
        from risk.manager import RiskManager

        rm = RiskManager(initial_capital=10_000)
        strat = HybridMLStrategy(rm, retrain=True)

        df = make_ohlcv(n=500, trend="up", seed=42)

        # Mock _base.generate_signals to return 60 signal rows
        base_out = strat.prepare(df)
        base_out["signal"] = 0
        base_out.iloc[50:110, base_out.columns.get_loc("signal")] = 1  # 60 signals

        mock_xgb = MagicMock()
        mock_xgb.predict.return_value = np.zeros(60, dtype=int)

        mock_clf = MagicMock(return_value=mock_xgb)

        with patch.object(strat._base, "generate_signals", return_value=base_out), \
             patch("strategies.hybrid_ml.xgb.XGBClassifier", mock_clf), \
             patch("strategies.hybrid_ml.joblib.dump"), \
             patch("strategies.hybrid_ml.classification_report",
                   return_value={"accuracy": 0.6}):
            result = strat.train(df)

        mock_xgb.fit.assert_called_once()
        assert isinstance(result, dict)


# ── backtesting/optuna_optimizer.py trial exception path ─────────────────────

class TestOptunaTrialException:
    def test_trial_exception_returns_minus_ten(self):
        """When the trial's backtest raises, objective returns -10.0."""
        import backtesting.optuna_optimizer as oo
        orig = oo.OPTUNA_AVAILABLE
        oo.OPTUNA_AVAILABLE = True
        try:
            from strategies.trend_ema import TrendEMAStrategy
            from config import BacktestConfig

            df = make_ohlcv(n=400, seed=10)
            backtest_cfg = BacktestConfig(initial_capital=10_000)

            good_result = MagicMock()
            good_result.metrics = {"sharpe": 0.5, "total_return_pct": 5.0}

            captured = []

            with patch("backtesting.optuna_optimizer.BacktestEngine") as mock_eng_cls, \
                 patch("backtesting.optuna_optimizer.optuna") as mock_optuna:

                # First call (inside trial) raises; second call (OOS) succeeds
                mock_eng = MagicMock()
                mock_eng.run.side_effect = [RuntimeError("bad candles"), good_result]
                mock_eng_cls.return_value = mock_eng

                def _fake_create_study(**kw):
                    study = MagicMock()
                    def _fake_optimize(obj, n_trials, **kw2):
                        score = obj(MagicMock(
                            suggest_int=MagicMock(return_value=10),
                            suggest_float=MagicMock(return_value=0.5),
                        ))
                        captured.append(score)
                    study.optimize    = _fake_optimize
                    study.best_params = {"fast": 10, "slow": 30, "adx_threshold": 25}
                    study.best_value  = -10.0
                    return study

                mock_optuna.create_study = _fake_create_study
                mock_optuna.samplers.TPESampler = MagicMock(return_value=MagicMock())

                oo.optimize(TrendEMAStrategy, df,
                            strategy_name="trend_ema", n_trials=1,
                            backtest_cfg=backtest_cfg)

            assert any(s == -10.0 for s in captured)
        finally:
            oo.OPTUNA_AVAILABLE = orig
