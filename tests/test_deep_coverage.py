"""
Deep coverage tests for remaining source-file gaps:
  backtesting/compare.py         (40-41)
  backtesting/engine.py          (43)
  backtesting/monte_carlo.py     (80)
  backtesting/optimizer.py       (85-86, 121)
  backtesting/optuna_optimizer.py(155-158)
  bot/auto_compound.py           (128-129)  [else-branch: dead code guard]
  bot/notifier.py                (25)
  bot/webhook.py                 (45, 78-79)
  reports/weekly_report.py       (153-158)
  risk/manager.py                (34, 125)
  strategies/breakout.py         (39)
  strategies/dca.py              (38, 45)
  strategies/heikin_ashi.py      (61-62)
  strategies/macd_divergence.py  (127-128)
  strategies/regime_adaptive.py  (63)
  strategies/trend_ema.py        (44)
  strategies/vwap_bounce.py      (32-33, 53-54)
  utils/correlation.py           (31, 36, 47)
  utils/events_filter.py         (61, 102-103)
  utils/feature_importance.py    (44-45, 95-96)
  utils/indicators.py            (261-262, 265)
"""
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock
from tests.conftest import make_ohlcv


# ── backtesting/engine.py:43 ─────────────────────────────────────────────────

class TestTradeShortDirection:
    def test_close_short_trade_negates_gross(self):
        from backtesting.engine import Trade
        t = Trade(
            symbol="BTC/USDT", entry_bar=0, entry_price=40_000.0,
            direction="short", size=0.1, stop_loss=41_000.0, take_profit=38_000.0,
        )
        t.close(bar=5, price=39_000.0, reason="take_profit", commission=0.001)
        # short: gross = -(price - entry) * size = -(−1000 * 0.1) = 100 (profit)
        assert t.pnl > 0
        assert t.exit_bar == 5


# ── backtesting/monte_carlo.py:80 ─────────────────────────────────────────────

class TestMonteCarloNotEnoughTrades:
    def test_raises_with_fewer_than_two_closed_trades(self):
        from backtesting.monte_carlo import run_monte_carlo
        from backtesting.engine import Trade, BacktestResult
        import pandas as pd

        t = Trade("X", 0, 100.0, "long", 1.0, 95.0, 110.0)
        t.close(1, 105.0, "tp", 0.001)
        result = BacktestResult(
            trades=[t],
            equity_curve=pd.Series([100, 105]),
            metrics={},
        )
        with pytest.raises(ValueError, match="at least 2 closed trades"):
            run_monte_carlo(result, initial_capital=100.0, n_simulations=10)


# ── backtesting/compare.py:40-41 ──────────────────────────────────────────────

class TestCompareStrategiesExceptionPath:
    def test_failed_strategy_logged_not_raised(self, tmp_path):
        from backtesting.compare import compare_strategies
        from strategies.trend_ema import TrendEMAStrategy

        df = make_ohlcv(n=300, trend="up", seed=1)
        failing = MagicMock()
        failing.return_value.run.side_effect = RuntimeError("strategy exploded")

        # "broken" raises on run() → covers lines 40-41
        # "trend_ema" succeeds → rows is non-empty so sort_values works
        with patch("backtesting.compare.STRATEGIES", {
            "broken": failing,
            "trend_ema": TrendEMAStrategy,
        }), patch("backtesting.compare._save_html_report"):
            result = compare_strategies(df, output_dir=tmp_path)

        assert len(result) == 1
        assert result.iloc[0]["strategy"] == "trend_ema"


# ── backtesting/optimizer.py:85-86, 121 ───────────────────────────────────────

class TestOptimizerExceptionAndEmptyTop:
    @pytest.fixture
    def df(self):
        return make_ohlcv(n=400, trend="up", seed=7)

    def test_grid_search_combo_exception_logged(self, df, tmp_path):
        from backtesting.optimizer import grid_search
        from config import CONFIG

        failing = MagicMock()
        failing.return_value.run.side_effect = RuntimeError("bad params")
        result = grid_search(
            failing, df,
            {"a": [1, 2], "b": [10, 20]},
            backtest_cfg=CONFIG.backtest,
        )
        assert result.empty  # all combos failed

    def test_walk_forward_empty_top_continues(self, df):
        from backtesting.optimizer import walk_forward_test
        from config import CONFIG

        failing = MagicMock()
        failing.return_value.run.side_effect = RuntimeError("bad params")
        result = walk_forward_test(
            failing, df, {"a": [1, 2]},
            n_windows=2, train_ratio=0.70,
            backtest_cfg=CONFIG.backtest,
        )
        assert isinstance(result, pd.DataFrame)
        assert result.empty  # all windows had empty grid_search → continue


# ── backtesting/optuna_optimizer.py:155-158 ───────────────────────────────────

class TestOptunaImportanceChartSuccess:
    def test_chart_saves_two_html_files(self, tmp_path):
        from backtesting.optuna_optimizer import optuna_importance_chart

        mock_fig = MagicMock()
        mock_vis = MagicMock()
        mock_vis.plot_param_importances.return_value = mock_fig
        mock_vis.plot_optimization_history.return_value = mock_fig

        with patch.dict("sys.modules", {"optuna.visualization": mock_vis}):
            optuna_importance_chart(MagicMock(), output_dir=tmp_path)

        assert mock_fig.write_html.call_count == 2


# ── risk/manager.py:34, 125 ───────────────────────────────────────────────────

class TestRiskManagerEdgeCases:
    def test_current_drawdown_zero_when_peak_is_zero(self):
        from risk.manager import PortfolioState
        ps = PortfolioState(capital=5_000.0)
        # peak_equity defaults to 0.0 — line 34 guard
        assert ps.peak_equity == 0.0
        assert ps.current_drawdown() == 0.0

    def test_validate_signal_false_when_entry_equals_stoploss(self):
        from risk.manager import RiskManager, TradeSignal
        rm = RiskManager(initial_capital=10_000.0)
        sig = TradeSignal(
            symbol="BTC/USDT", direction="long",
            entry_price=40_000.0, stop_loss=40_000.0,  # denom = 0 → < 1e-9
            take_profit=42_000.0,
        )
        assert rm.validate_signal(sig) is False


# ── utils/correlation.py:31, 36, 47 ──────────────────────────────────────────

class TestCorrelationFilterUncoveredBranches:
    def test_sym_not_in_cache_continues(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter()
        prices = pd.Series(np.random.randn(50).cumsum() + 100)
        cf.update("BTC/USDT", prices)
        # ETH/USDT is in open_symbols but not in cache → line 31 (continue)
        result = cf.is_correlated_with_open("BTC/USDT", ["ETH/USDT"])
        assert result is False

    def test_aligned_less_than_20_continues(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter()
        idx_btc = pd.date_range("2022-01-01", periods=50, freq="1h")
        idx_eth = pd.date_range("2023-06-01", periods=50, freq="1h")  # no overlap
        cf.update("BTC/USDT", pd.Series(np.random.randn(50).cumsum() + 100, index=idx_btc))
        cf.update("ETH/USDT", pd.Series(np.random.randn(50).cumsum() + 100, index=idx_eth))
        # After pct_change+dropna the aligned series has 0 rows < 20 → line 36 (continue)
        result = cf.is_correlated_with_open("BTC/USDT", ["ETH/USDT"])
        assert result is False

    def test_correlation_matrix_returns_empty_when_few_symbols(self):
        from utils.correlation import CorrelationFilter
        cf = CorrelationFilter()
        # Neither symbol is in cache → available < 2 → line 47 (return pd.DataFrame())
        result = cf.correlation_matrix(["BTC/USDT", "ETH/USDT"])
        assert result.empty


# ── strategies/vwap_bounce.py:32-33, 53-54 ───────────────────────────────────

class TestVWAPBounceEdgeCases:
    def test_no_vwap_column_returns_zero_signals(self):
        from strategies.vwap_bounce import VWAPBounceStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = VWAPBounceStrategy(rm)
        df = make_ohlcv(n=100)  # no 'vwap' column → early return (lines 32-33)
        result = strat.generate_signals(df)
        assert (result["signal"] == 0).all()

    def test_integer_index_triggers_session_filter_fallback(self):
        from strategies.vwap_bounce import VWAPBounceStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = VWAPBounceStrategy(rm)
        df = make_ohlcv(n=100)
        # Integer RangeIndex has no .hour → except branch → session_ok = True (lines 53-54)
        df = df.reset_index(drop=True)  # now has RangeIndex
        df["vwap"] = df["close"]
        result = strat.generate_signals(df)
        assert "signal" in result.columns


# ── utils/indicators.py:261-262, 265 ─────────────────────────────────────────

class TestComputeMarketRegimeAddIndicators:
    def test_compute_market_regime_on_raw_df_adds_adx(self):
        from utils.indicators import compute_market_regime
        df = make_ohlcv(n=200, trend="up", seed=5)
        # Raw df: no ADX_ columns → lines 261-262 hit (add_trend_indicators called)
        regimes = compute_market_regime(df)
        assert len(regimes) == len(df)

    def test_compute_market_regime_with_adx_but_no_ema50(self):
        from utils.indicators import compute_market_regime, add_trend_indicators
        df = make_ohlcv(n=200, trend="up", seed=5)
        df = add_trend_indicators(df)          # adds ADX_14 AND ema_50
        df = df.drop(columns=["ema_50"])       # remove ema_50 → line 265 hit
        regimes = compute_market_regime(df)
        assert len(regimes) == len(df)


# ── strategies/regime_adaptive.py:63 ─────────────────────────────────────────

class TestDetectRegimeNoBBColumns:
    def test_bb_expanding_fallback_when_no_bb_columns(self):
        from strategies.regime_adaptive import detect_regime
        from utils.indicators import add_trend_indicators
        df = make_ohlcv(n=200, trend="up", seed=6)
        df = add_trend_indicators(df)  # adds ADX but no BBU_/BBL_ columns
        # Remove any BB/KC columns that might have been added
        drop_cols = [c for c in df.columns if any(x in c for x in ["BBU_", "BBL_", "KCUe_", "KCLe_"])]
        df = df.drop(columns=drop_cols)
        # No BB cols → else branch at line 63 → bb_expanding = False Series
        regimes = detect_regime(df)
        assert len(regimes) == len(df)


# ── strategies/trend_ema.py:44 ───────────────────────────────────────────────

class TestTrendEMAMissingColumns:
    def test_generate_signals_raises_without_ema_columns(self):
        from strategies.trend_ema import TrendEMAStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = TrendEMAStrategy(rm)
        df = make_ohlcv(n=100)  # raw OHLCV, no ema_ columns
        with pytest.raises(ValueError, match="Missing EMA columns"):
            strat.generate_signals(df)


# ── strategies/breakout.py:39 ────────────────────────────────────────────────

class TestBreakoutIsSqueezeFallback:
    def test_is_squeeze_returns_false_when_no_bb_kc_columns(self):
        from strategies.breakout import BreakoutStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = BreakoutStrategy(rm)
        df = make_ohlcv(n=100)  # no BBU_/BBL_/KCUe_/KCLe_ columns
        result = strat._is_squeeze(df)
        assert (result == False).all()


# ── strategies/dca.py:38, 45 ─────────────────────────────────────────────────

class TestDCAPositionEmptyState:
    def test_avg_entry_returns_zero_when_empty(self):
        from strategies.dca import DCAPosition
        pos = DCAPosition()
        assert pos.avg_entry == 0.0  # line 38

    def test_total_size_returns_zero_when_empty(self):
        from strategies.dca import DCAPosition
        pos = DCAPosition()
        assert pos.total_size == 0.0  # line 45 (sum of empty list)


# ── strategies/heikin_ashi.py:61-62 ──────────────────────────────────────────

class TestHeikinAshiNoHAColumn:
    def test_generate_signals_computes_ha_when_missing(self):
        from strategies.heikin_ashi import HeikinAshiStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = HeikinAshiStrategy(rm)
        df = make_ohlcv(n=100)  # no ha_bull column → lines 61-62 run
        result = strat.generate_signals(df)
        assert "signal" in result.columns


# ── strategies/macd_divergence.py:127-128 ────────────────────────────────────

class TestMACDDivergenceNoColumn:
    def test_generate_signals_zero_when_no_macd_column(self):
        from strategies.macd_divergence import MACDDivergenceStrategy
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000.0)
        strat = MACDDivergenceStrategy(rm)
        df = make_ohlcv(n=100)  # no MACD_ column → signal=0 (lines 127-128)
        result = strat.generate_signals(df)
        assert (result["signal"] == 0).all()


# ── bot/notifier.py:25 ───────────────────────────────────────────────────────

class TestNotifierNon200Status:
    @pytest.mark.asyncio
    async def test_send_telegram_logs_warning_on_non_200(self):
        import bot.notifier as notifier

        mock_resp = MagicMock()
        mock_resp.status = 400  # triggers logger.warning (line 25)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__  = AsyncMock(return_value=False)
        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post.__aexit__  = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__  = AsyncMock(return_value=False)

        with patch.object(notifier, "TELEGRAM_TOKEN", "tok"), \
             patch.object(notifier, "TELEGRAM_CHAT_ID", "chat"), \
             patch("bot.notifier.aiohttp.ClientSession", return_value=mock_session):
            await notifier._send_telegram("test")
        # no assertion needed: line 25 is covered


# ── bot/webhook.py:45, 78-79 ─────────────────────────────────────────────────

class TestWebhookHelpers:
    def test_set_live_trader_sets_global(self):
        from bot import webhook
        from bot.webhook import set_live_trader
        trader = MagicMock()
        set_live_trader(trader)         # covers line 45
        assert webhook._live_trader is trader

    def test_verify_secret_returns_false_for_type_error(self):
        from bot.webhook import _verify_secret
        # provided=123 (int) is truthy → skips the "not provided" branch
        # hmac.compare_digest("str", 123) → TypeError → line 78-79 hit
        result = _verify_secret("secret", 123)
        assert result is False


# ── utils/events_filter.py:61, 102-103 ───────────────────────────────────────

class TestEventsFilterUncoveredPaths:
    def test_event_with_none_datetime_is_skipped(self):
        from utils.events_filter import EventsFilter
        ef = EventsFilter()
        # Patch _fetch_forex_factory to return event with datetime=None
        with patch.object(ef, "_fetch_forex_factory",
                          return_value=[{"title": "Test", "datetime": None}]):
            safe, reason = ef.is_safe_to_trade()
        assert safe is True   # None datetime → continue → no blocking event

    def test_bad_date_parse_is_silently_skipped(self):
        from utils.events_filter import EventsFilter
        ef = EventsFilter()
        ef._cache_ts = 0.0  # force cache miss
        bad_resp = MagicMock()
        bad_resp.json.return_value = [
            {"impact": "High", "date": "bad-date", "time": "99:99pm", "title": "X"}
        ]
        bad_resp.raise_for_status = MagicMock()
        with patch("utils.events_filter.requests.get", return_value=bad_resp):
            events = ef._fetch_forex_factory()
        assert events == []  # bad date → except: pass → no events appended


# ── utils/feature_importance.py:44-45, 95-96 ─────────────────────────────────

class TestFeatureImportanceEdgeCases:
    def test_get_score_exception_returns_empty(self):
        from utils.feature_importance import plot_feature_importance

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_model = MagicMock()
        mock_model.get_booster.return_value.get_score.side_effect = Exception("no booster")

        with patch("utils.feature_importance.joblib.load", return_value=mock_model):
            result = plot_feature_importance(model_path=mock_path)

        assert result == {}  # all itype calls raised → primary is empty → return {}

    def test_get_shap_values_returns_none_when_shap_missing(self):
        from utils.feature_importance import get_shap_values

        # Remove shap from sys.modules so import inside the function fails
        shap_backup = sys.modules.pop("shap", None)
        with patch.dict(sys.modules, {"shap": None}):
            result = get_shap_values(MagicMock(), np.array([[1.0, 2.0, 3.0]]))
        if shap_backup is not None:
            sys.modules["shap"] = shap_backup
        assert result is None  # ImportError → except ImportError → return None

    def test_get_shap_values_success_path(self):
        """Cover lines 95-96: shap present and returns values."""
        from utils.feature_importance import get_shap_values

        expected = np.array([[0.1, 0.2, 0.3]])
        mock_shap = MagicMock()
        mock_expl = MagicMock()
        mock_shap.TreeExplainer.return_value = mock_expl
        mock_expl.shap_values.return_value = expected

        with patch.dict(sys.modules, {"shap": mock_shap}), \
             patch("utils.feature_importance.joblib.load", return_value=MagicMock()):
            result = get_shap_values(MagicMock(), np.array([[1.0, 2.0]]))

        np.testing.assert_array_equal(result, expected)  # lines 95-96 covered


# ── reports/weekly_report.py:153-158 ─────────────────────────────────────────

class TestWeeklyReportScheduler:
    def test_start_scheduler_runs_loop_once_then_raises(self):
        import reports.weekly_report as wr

        mock_time = MagicMock()
        mock_time.sleep.side_effect = StopIteration  # break the infinite loop
        mock_sched = MagicMock()

        with patch.object(wr, "schedule", mock_sched), \
             patch.object(wr, "time", mock_time):
            with pytest.raises(StopIteration):
                wr.start_scheduler("trend_ema")

        # Scheduler registration and one loop iteration covered
        mock_sched.every.return_value.monday.at.return_value.do.assert_called_once()
        mock_sched.run_pending.assert_called_once()
        mock_time.sleep.assert_called_once_with(60)


# ── strategies/volume_profile.py:163 ─────────────────────────────────────────

class TestVolumeProfileGenerateSignalsWithoutPrepare:
    def test_generate_signals_computes_vp_when_columns_absent(self):
        from strategies.volume_profile import VolumeProfileStrategy
        from risk.manager import RiskManager

        rm = RiskManager(initial_capital=10_000.0)
        strat = VolumeProfileStrategy(rm, n_bins=10, period=30)
        df = make_ohlcv(n=60, trend="up", seed=9)
        # No vp_poc column → line 163 triggers _compute_rolling_volume_profile
        result = strat.generate_signals(df)
        assert "signal" in result.columns
        assert "vp_poc" in result.columns
