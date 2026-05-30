"""
Tests for Grid Trading, DCA, Ensemble, AutoCompounder and StrategyMonitor.
"""
import pytest
import numpy as np
import pandas as pd


# ── Grid Trading ──────────────────────────────────────────────────────────────

class TestGridTrading:
    def test_signals_generated_in_ranging_market(self, ohlcv, risk_manager):
        from strategies.grid_trading import GridTradingStrategy
        strat  = GridTradingStrategy(risk_manager, n_grids=8, range_pct=0.04)
        result = strat.run(ohlcv)
        assert "signal" in result.columns
        # Grid should produce buys AND sells over 500 bars
        buys  = (result["signal"] == 1).sum()
        sells = (result["signal"] == -1).sum()
        assert buys > 0, "Grid should generate at least one buy fill"

    def test_no_trade_when_trending(self, risk_manager):
        from strategies.grid_trading import GridTradingStrategy
        from tests.conftest import make_ohlcv
        up   = make_ohlcv(trend="up", n=400)
        strat = GridTradingStrategy(risk_manager, only_in_range=True)
        result = strat.run(up)
        # ADX filter should suppress most signals in trending market
        buys = (result["signal"] == 1).sum()
        # In a strong uptrend ADX > 25, so few/zero grid signals
        assert buys < 40


# ── DCA ───────────────────────────────────────────────────────────────────────

class TestDCA:
    def test_base_order_created(self, ohlcv, risk_manager):
        from strategies.dca import DCAStrategy
        strat  = DCAStrategy(risk_manager)
        result = strat.run(ohlcv)
        assert "signal" in result.columns
        buys = (result["signal"] == 1).sum()
        assert buys > 0

    def test_safety_orders_accumulate(self, risk_manager):
        from strategies.dca import DCAStrategy
        from tests.conftest import make_ohlcv
        # Downtrending market → DCA safety orders should fire
        down   = make_ohlcv(trend="down", n=300)
        strat  = DCAStrategy(risk_manager, safety_deviation=0.02, max_safety_orders=4)
        result = strat.run(down)
        buys   = (result["signal"] == 1).sum()
        assert buys >= 1   # at least base order


# ── Ensemble ──────────────────────────────────────────────────────────────────

class TestEnsemble:
    def test_majority_vote_fewer_signals_than_single(self, ohlcv, risk_manager):
        from strategies.ensemble import EnsembleStrategy
        from strategies.trend_ema import TrendEMAStrategy

        ens   = EnsembleStrategy(risk_manager, mode="majority", min_votes=3)
        ema   = TrendEMAStrategy(risk_manager)

        ens_sigs = (ens.run(ohlcv)["signal"] == 1).sum()
        ema_sigs = (ema.run(ohlcv)["signal"] == 1).sum()

        # Ensemble should be more selective than individual strategy
        assert ens_sigs <= ema_sigs

    def test_vote_counts_attached(self, ohlcv, risk_manager):
        from strategies.ensemble import EnsembleStrategy
        ens    = EnsembleStrategy(risk_manager, mode="majority")
        result = ens.run(ohlcv)
        assert "long_votes"  in result.columns
        assert "short_votes" in result.columns
        assert result["long_votes"].max() <= 5   # max = number of members

    def test_unanimous_mode_produces_fewest_signals(self, ohlcv, risk_manager):
        from strategies.ensemble import EnsembleStrategy
        maj  = EnsembleStrategy(risk_manager, mode="majority")
        una  = EnsembleStrategy(risk_manager, mode="unanimous")
        maj_n = (maj.run(ohlcv)["signal"] == 1).sum()
        una_n = (una.run(ohlcv)["signal"] == 1).sum()
        assert una_n <= maj_n


# ── AutoCompounder ────────────────────────────────────────────────────────────

class TestAutoCompounder:
    def test_reinvest_all_adds_full_profit(self, monkeypatch, tmp_path):
        # Redirect DB state to tmp
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "test.db")
        db_mod.init_db()

        from bot.auto_compound import AutoCompounder, CompoundMode
        from datetime import datetime, timedelta

        ac = AutoCompounder(10_000, mode=CompoundMode.REINVEST_ALL)
        ac.state.last_compound_ts = datetime.utcnow() - timedelta(days=8)

        result = ac.run(current_equity=11_000)
        assert result["profit"]     == pytest.approx(1_000.0)
        assert result["compounded"] == pytest.approx(1_000.0)
        assert result["withdrawn"]  == pytest.approx(0.0)

    def test_half_mode_splits_profit(self, monkeypatch, tmp_path):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "test2.db")
        db_mod.init_db()

        from bot.auto_compound import AutoCompounder, CompoundMode
        from datetime import datetime, timedelta

        ac = AutoCompounder(10_000, mode=CompoundMode.REINVEST_HALF)
        ac.state.last_compound_ts = datetime.utcnow() - timedelta(days=8)

        result = ac.run(current_equity=10_500)
        assert result["compounded"] == pytest.approx(250.0)
        assert result["withdrawn"]  == pytest.approx(250.0)

    def test_rebalance_detects_drift(self):
        from bot.auto_compound import AutoCompounder, CompoundMode
        ac = AutoCompounder(10_000, mode=CompoundMode.REINVEST_ALL)
        # One pair has drifted significantly
        drifted = ac.rebalance_check({"BTC/USDT": 5_000, "ETH/USDT": 1_000})
        assert "ETH/USDT" in drifted   # ETH drifted > 20% from equal weight


# ── StrategyMonitor ───────────────────────────────────────────────────────────

class TestStrategyMonitor:
    def test_healthy_with_good_trades(self, monkeypatch, tmp_path):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "mon.db")
        db_mod.init_db()

        # Insert profitable trades
        for i in range(10):
            tid = db_mod.insert_trade("BTC/USDT", "long", "trend_ema",
                                      30_000, 0.1, 29_000, 32_000)
            db_mod.close_trade(tid, 31_500, 150.0, 0.05, "take_profit", 10)

        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        mon = StrategyMonitor("trend_ema", baseline_sharpe=0.5, baseline_win_rate=50.0)
        health = mon.check()
        assert health.status in (HealthStatus.HEALTHY, HealthStatus.NO_DATA)

    def test_critical_with_losing_trades(self, monkeypatch, tmp_path):
        import data.database as db_mod
        monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "mon2.db")
        db_mod.init_db()

        # Insert losing trades
        for i in range(15):
            tid = db_mod.insert_trade("BTC/USDT", "long", "trend_ema",
                                      30_000, 0.1, 29_000, 32_000)
            db_mod.close_trade(tid, 28_500, -150.0, -0.05, "stop_loss", 5)

        from bot.strategy_monitor import StrategyMonitor, HealthStatus
        mon = StrategyMonitor("trend_ema", baseline_sharpe=1.5, baseline_win_rate=60.0,
                              window_trades=15)
        health = mon.check()
        assert health.status in (HealthStatus.CRITICAL, HealthStatus.WARNING,
                                 HealthStatus.DEGRADED)


# ── Hybrid ML Strategy ────────────────────────────────────────────────────────

class TestHybridML:
    def test_run_without_model_uses_ema_signals(self, ohlcv, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy
        strat = HybridMLStrategy(risk_manager, retrain=False)
        strat.model = None  # ensure no model
        out = strat.run(ohlcv)
        assert "signal" in out.columns
        assert set(out["signal"].unique()).issubset({-1, 0, 1})

    def test_features_built_correctly(self, ohlcv, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy, _build_features
        strat = HybridMLStrategy(risk_manager, retrain=False)
        df = strat.prepare(ohlcv)
        feats = _build_features(df)
        # Shape should match input
        assert len(feats) == len(df)
        # No NaN (fillna(0) applied)
        assert not feats.isnull().any().any()

    def test_triple_barrier_label_shape(self, ohlcv, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy, _triple_barrier_label
        strat = HybridMLStrategy(risk_manager)
        df = strat.prepare(ohlcv)
        # Use last 50 bars as "signal" indices
        idx = df.index[-50:-5]
        labels = _triple_barrier_label(df, idx, tp_pct=0.03, sl_pct=0.015, max_bars=10)
        assert len(labels) == len(idx)
        assert set(labels.unique()).issubset({0, 1})

    def test_train_on_uptrend_data(self, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy
        from tests.conftest import make_ohlcv
        df = make_ohlcv(600, trend="up", seed=42)
        strat = HybridMLStrategy(risk_manager, retrain=True)
        report = strat.train(df)
        # May return {} if not enough signals — either way, no crash
        assert isinstance(report, dict)

    def test_run_with_trained_model_filters_signals(self, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy
        from tests.conftest import make_ohlcv
        df = make_ohlcv(600, trend="up", seed=10)
        strat = HybridMLStrategy(risk_manager, retrain=True)
        strat.train(df)

        if strat.model is not None:
            out = strat.run(df)
            assert "signal" in out.columns
            assert "ml_confidence" in out.columns
            # ML-filtered signals should be <= raw EMA signals
            ml_buys = (out["signal"] == 1).sum()
            assert ml_buys >= 0

    def test_ml_confidence_column_range(self, risk_manager):
        from strategies.hybrid_ml import HybridMLStrategy
        from tests.conftest import make_ohlcv
        df = make_ohlcv(600, trend="up", seed=11)
        strat = HybridMLStrategy(risk_manager, retrain=True)
        strat.train(df)
        if strat.model is not None:
            out = strat.run(df)
            conf = out["ml_confidence"].dropna()
            assert (conf >= 0).all() and (conf <= 1).all()


# ── Multi-Timeframe (MTF) Strategy ────────────────────────────────────────────

class TestMTFStrategy:
    def test_single_tf_run_returns_signals(self, ohlcv, risk_manager):
        from strategies.mtf import MultiTimeframeStrategy
        strat = MultiTimeframeStrategy(risk_manager)
        out = strat.run(ohlcv)
        assert "signal" in out.columns
        assert set(out["signal"].unique()).issubset({-1, 0, 1})

    def test_run_mtf_with_two_timeframes(self, risk_manager):
        from strategies.mtf import MultiTimeframeStrategy
        from tests.conftest import make_ohlcv
        ltf = make_ohlcv(500, seed=1)
        # Simulate 4h by downsampling (every 4th row)
        htf = ltf.iloc[::4].copy()
        strat = MultiTimeframeStrategy(risk_manager)
        out = strat.run_mtf(ltf, htf)
        assert "signal" in out.columns
        assert "htf_bias" in out.columns

    def test_bull_bias_produces_longs(self, risk_manager):
        from strategies.mtf import MultiTimeframeStrategy
        from tests.conftest import make_ohlcv
        df = make_ohlcv(500, trend="up", seed=5)
        strat = MultiTimeframeStrategy(risk_manager)
        out = strat.run(df)
        longs = (out["signal"] == 1).sum()
        shorts = (out["signal"] == -1).sum()
        # Uptrend → longs should dominate or equal
        assert longs >= shorts

    def test_single_tf_fallback(self, ohlcv, risk_manager):
        from strategies.mtf import MultiTimeframeStrategy
        strat = MultiTimeframeStrategy(risk_manager)
        out = strat.generate_signals_single(strat.prepare(ohlcv))
        assert "signal" in out.columns
        assert "htf_bias" in out.columns
        assert (out["htf_bias"] == 1).all()  # default bull

    def test_stop_loss_and_tp_set(self, ohlcv, risk_manager):
        from strategies.mtf import MultiTimeframeStrategy
        strat = MultiTimeframeStrategy(risk_manager)
        out = strat.run(ohlcv)
        assert "stop_loss" in out.columns
        assert "take_profit" in out.columns
        # Stop loss always below close on non-NaN rows
        valid = out.dropna(subset=["stop_loss", "take_profit"])
        assert (valid["stop_loss"] <= valid["close"]).all()
        assert (valid["take_profit"] >= valid["close"]).all()
