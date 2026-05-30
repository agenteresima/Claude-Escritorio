"""
End-to-end pipeline smoke tests.
Verifies: Data → Indicators → Strategy → Backtest → Report → DB persistence.
Marked @pytest.mark.integration so they run separately from unit tests.

These do NOT require network access; all data is synthetic.
Run with:  pytest tests/test_full_pipeline.py -v
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from tests.conftest import make_ohlcv


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_uptrend(n: int = 600) -> pd.DataFrame:
    return make_ohlcv(n, trend="up", seed=7)


# ─── Full backtest pipeline ───────────────────────────────────────────────────

class TestFullBacktestPipeline:
    """Strategy → Indicators → Signals → Engine → Report."""

    @pytest.mark.parametrize("strategy_name", [
        "trend_ema", "mean_reversion", "breakout", "supertrend",
        "vwap_bounce", "macd_divergence", "heikin_ashi", "volume_profile",
    ])
    def test_strategy_produces_valid_signals(self, strategy_name):
        from strategies import STRATEGIES
        from risk.manager import RiskManager

        df = _make_uptrend(400)
        rm = RiskManager(initial_capital=10_000)
        strat = STRATEGIES[strategy_name](rm)
        out = strat.run(df)

        assert "signal" in out.columns, f"{strategy_name} missing signal column"
        assert set(out["signal"].unique()).issubset({-1, 0, 1}), \
            f"{strategy_name} signals outside {{-1,0,1}}"
        assert len(out) == len(df), f"{strategy_name} changed row count"

    def test_backtest_engine_full_run(self):
        from strategies.trend_ema import TrendEMAStrategy
        from backtesting.engine import BacktestEngine
        from risk.manager import RiskManager
        from config import BacktestConfig

        df = _make_uptrend(600)
        rm = RiskManager(initial_capital=10_000)
        strat = TrendEMAStrategy(rm)
        sig = strat.run(df)
        cfg = BacktestConfig(initial_capital=10_000, commission=0.001)
        result = BacktestEngine(cfg, rm).run(sig, symbol="BTC/USDT")

        assert len(result.equity_curve) == len(df)
        assert "sharpe" in result.metrics
        assert "total_return_pct" in result.metrics
        assert isinstance(result.trades, list)

    def test_backtest_summary_prints(self):
        from strategies.mean_reversion import MeanReversionStrategy
        from backtesting.engine import BacktestEngine
        from risk.manager import RiskManager
        from config import BacktestConfig

        df = make_ohlcv(400)
        rm = RiskManager(initial_capital=10_000)
        sig = MeanReversionStrategy(rm).run(df)
        result = BacktestEngine(BacktestConfig(), rm).run(sig)
        s = result.summary()
        assert isinstance(s, str)
        assert "=" in s

    def test_report_generated(self, tmp_path):
        from strategies.trend_ema import TrendEMAStrategy
        from backtesting.engine import BacktestEngine
        from risk.manager import RiskManager
        from config import BacktestConfig
        from reports.report_generator import generate_report

        df = _make_uptrend(400)
        rm = RiskManager(initial_capital=10_000)
        sig = TrendEMAStrategy(rm).run(df)
        result = BacktestEngine(BacktestConfig(), rm).run(sig)
        path = generate_report(result, "trend_ema", "BTC/USDT", output_dir=tmp_path)

        assert path.exists()
        content = path.read_text()
        assert "trend_ema" in content
        assert "BTC" in content


# ─── Indicator correctness ────────────────────────────────────────────────────

class TestIndicatorIntegrity:
    def test_rsi_range(self):
        from utils.indicators import add_momentum_indicators
        df = _make_uptrend(300)
        out = add_momentum_indicators(df)
        rsi = out["rsi_14"].dropna()
        assert (rsi >= 0).all() and (rsi <= 100).all()

    def test_atr_positive(self):
        from utils.indicators import add_volatility_indicators
        df = _make_uptrend(300)
        out = add_volatility_indicators(df)
        assert (out["atr_14"].dropna() > 0).all()

    def test_ema_monotone_on_constant(self):
        """EMA of constant series equals the constant."""
        from utils.indicators import add_trend_indicators
        n = 200
        df = pd.DataFrame({
            "open": [100.0] * n, "high": [100.0] * n,
            "low":  [100.0] * n, "close": [100.0] * n,
            "volume": [1000.0] * n,
        }, index=pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC"))
        out = add_trend_indicators(df)
        assert out["ema_21"].iloc[-1] == pytest.approx(100.0, abs=0.1)

    def test_bollinger_band_order(self):
        from utils.indicators import add_volatility_indicators
        df = _make_uptrend(300)
        out = add_volatility_indicators(df).dropna(subset=["BBL_20_2.0", "BBM_20_2.0", "BBU_20_2.0"])
        assert (out["BBL_20_2.0"] <= out["BBM_20_2.0"]).all()
        assert (out["BBM_20_2.0"] <= out["BBU_20_2.0"]).all()

    def test_supertrend_direction_binary(self):
        from utils.indicators import add_trend_indicators
        df = _make_uptrend(300)
        out = add_trend_indicators(df)
        d_col = next((c for c in out.columns if c.startswith("SUPERTd_")), None)
        assert d_col is not None
        vals = out[d_col].dropna().unique()
        assert set(vals).issubset({-1, 1})


# ─── Risk management pipeline ─────────────────────────────────────────────────

class TestRiskPipeline:
    def test_portfolio_heat_prevents_overexposure(self):
        from risk.portfolio_heat import PortfolioHeatManager

        mgr = PortfolioHeatManager(max_heat_pct=0.05)
        # Fill 4.5% heat
        mgr.update_position("BTC/USDT", "long",
                             entry=40_000, current=40_000,
                             stop=39_000, size=0.45)   # 0.45 × $1000 = $450 risk
        # Adding $100 (1%) would exceed 5%
        ok, reason = mgr.can_add_position(total_capital=10_000, new_risk=100.0)
        assert ok is False

    def test_kelly_fraction_with_positive_edge(self):
        from risk.manager import RiskManager
        rm = RiskManager(initial_capital=10_000)
        # 60% win rate, avg win = 2x avg loss → positive edge
        size = rm.kelly_size(win_rate=0.60, avg_win=100.0, avg_loss=50.0)
        assert 0 < size <= 0.10

    def test_circuit_breaker_halts_trading(self):
        from risk.manager import RiskManager, TradeSignal
        rm = RiskManager(initial_capital=10_000)
        rm.portfolio.capital    = 8_400   # 16% drawdown
        rm.portfolio.peak_equity = 10_000
        sig = TradeSignal("BTC/USDT", "long", 40_000, 39_000, 42_000)
        assert rm.validate_signal(sig) is False


# ─── Database persistence ─────────────────────────────────────────────────────

class TestDatabasePipeline:
    @pytest.fixture
    def db(self, tmp_path):
        import data.database as db_module
        from unittest.mock import patch
        db_path = tmp_path / "test_pipeline.db"
        with patch.object(db_module, "DB_PATH", db_path):
            db_module.init_db()
            yield db_module

    def test_full_trade_lifecycle(self, db):
        # Open a trade
        db.insert_trade(
            symbol="BTC/USDT", direction="long", strategy="trend_ema",
            entry_price=40_000.0, size=0.01,
            stop_loss=39_000.0, take_profit=42_000.0,
        )
        open_trades = db.get_open_trades()
        assert len(open_trades) == 1

        # Close it with profit
        db.close_trade(
            trade_id=open_trades[0]["id"],
            exit_price=41_000.0,
            pnl=10.0,
            pnl_pct=0.025,
            exit_reason="take_profit",
            bars_held=12,
        )
        assert len(db.get_open_trades()) == 0

        # Verify stats
        stats = db.trade_stats("trend_ema")
        assert stats["total_trades"] == 1
        assert stats["win_rate"] == pytest.approx(100.0, abs=0.1)

    def test_equity_history_tracks_growth(self, db):
        for equity in [10_000, 10_500, 11_000]:
            db.save_equity("trend_ema", equity)
        history = db.get_equity_history("trend_ema", limit=10)
        assert len(history) == 3
        equities = [h["equity"] for h in history]
        # get_equity_history returns most-recent-first
        assert max(equities) == pytest.approx(11_000.0)
        assert min(equities) == pytest.approx(10_000.0)


# ─── Compare strategies ───────────────────────────────────────────────────────

class TestCompareStrategies:
    def test_compare_returns_ranked_dataframe(self):
        from backtesting.compare import compare_strategies

        df = _make_uptrend(400)
        result = compare_strategies(df, symbol="BTC/USDT")

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 3   # at least 3 strategies succeeded
        # Should have standard metric columns
        assert "strategy" in result.columns or result.index.name == "strategy"
        assert "sharpe" in result.columns


# ─── Portfolio backtest ───────────────────────────────────────────────────────

class TestPortfolioBacktest:
    def test_multi_pair_portfolio(self):
        from backtesting.portfolio_backtest import PortfolioBacktester
        from strategies.trend_ema import TrendEMAStrategy
        from config import BacktestConfig

        data = {
            "BTC/USDT": _make_uptrend(400),
            "ETH/USDT": make_ohlcv(400, seed=5),
            "SOL/USDT": make_ohlcv(400, seed=6),
        }
        bt = PortfolioBacktester(BacktestConfig(initial_capital=30_000))
        result = bt.run(data, TrendEMAStrategy)

        assert hasattr(result, "pair_results")
        assert hasattr(result, "combined_equity")
        assert len(result.pair_results) == 3
        assert len(result.combined_equity) > 0
