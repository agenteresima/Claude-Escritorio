"""
Bayesian hyperparameter optimization with Optuna.
Superior to grid search: samples smarter, converges faster.

Optuna uses Tree-structured Parzen Estimators (TPE) to focus
trials on the most promising parameter regions.

Usage:
    from backtesting.optuna_optimizer import optimize
    best = optimize(TrendEMAStrategy, df, n_trials=200)
    print(best)
"""
import pandas as pd
import numpy as np
from typing import Callable, Optional
from loguru import logger

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logger.warning("Optuna not installed — run: pip install optuna")

from config import CONFIG
from risk.manager import RiskManager
from backtesting.engine import BacktestEngine


def _score(metrics: dict) -> float:
    """Composite objective: Sharpe × win_rate × (1 - |DD|) × min(PF,3)/3"""
    sharpe = metrics.get("sharpe", 0.0)
    if sharpe <= 0:
        return -10.0
    wr  = metrics.get("win_rate", 0) / 100
    dd  = abs(metrics.get("max_drawdown_pct", 100)) / 100
    pf  = min(metrics.get("profit_factor", 0), 3) / 3
    n   = max(metrics.get("total_trades", 0), 1)
    trade_penalty = 1 / (1 + np.exp(-0.01 * (n - 30)))   # penalise < 30 trades
    return sharpe * wr * (1 - dd) * pf * trade_penalty


# ── Strategy-specific param samplers ─────────────────────────────────────────

PARAM_SPACES = {
    "trend_ema": lambda t: {
        "fast":          t.suggest_int("fast",          5,  15),
        "slow":          t.suggest_int("slow",         18,  60),
        "adx_threshold": t.suggest_float("adx_threshold", 15, 35),
    },
    "mean_reversion": lambda t: {
        "rsi_oversold":   t.suggest_float("rsi_oversold",  20, 35),
        "rsi_overbought": t.suggest_float("rsi_overbought", 65, 80),
        "adx_max":        t.suggest_float("adx_max",       15, 30),
    },
    "breakout": lambda t: {
        "donchian_period": t.suggest_int("donchian_period", 10, 30),
        "squeeze_bars":    t.suggest_int("squeeze_bars",     2, 10),
    },
    "supertrend": lambda t: {
        "period":     t.suggest_int("period",      7, 20),
        "multiplier": t.suggest_float("multiplier", 1.5, 5.0),
    },
    "dca": lambda t: {
        "safety_deviation":  t.suggest_float("safety_deviation",  0.01, 0.06),
        "max_safety_orders": t.suggest_int("max_safety_orders",   2,    6),
        "take_profit_pct":   t.suggest_float("take_profit_pct",   0.01, 0.08),
        "volume_scale":      t.suggest_float("volume_scale",      1.0,  3.0),
    },
    "grid_trading": lambda t: {
        "n_grids":   t.suggest_int("n_grids",    5,  20),
        "range_pct": t.suggest_float("range_pct", 0.02, 0.15),
    },
}


def optimize(
    strategy_cls,
    df: pd.DataFrame,
    strategy_name: Optional[str] = None,
    n_trials: int = 200,
    n_jobs: int = 1,
    walk_forward_split: float = 0.70,
    backtest_cfg=CONFIG.backtest,
) -> dict:
    """
    Run Bayesian optimization and return best params + metrics.
    Uses walk-forward validation (train 70%, test 30%).
    """
    if not OPTUNA_AVAILABLE:
        raise RuntimeError("Install optuna: pip install optuna")

    name = strategy_name or getattr(strategy_cls, "name", "unknown")
    if name not in PARAM_SPACES:
        raise ValueError(f"No param space defined for '{name}'. "
                         f"Available: {list(PARAM_SPACES.keys())}")

    split    = int(len(df) * walk_forward_split)
    train_df = df.iloc[:split]
    test_df  = df.iloc[split:]

    def objective(trial):
        params = PARAM_SPACES[name](trial)
        try:
            rm     = RiskManager(initial_capital=backtest_cfg.initial_capital)
            strat  = strategy_cls(rm, **params)
            engine = BacktestEngine(backtest_cfg, rm)
            sig_df = strat.run(train_df.copy())
            result = engine.run(sig_df)
            return _score(result.metrics)
        except Exception as e:
            logger.debug(f"Trial failed: {e}")
            return -10.0

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(),
    )
    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs, show_progress_bar=False)

    best_params = study.best_params
    logger.info(f"Optuna [{name}] best params: {best_params} (score={study.best_value:.4f})")

    # Validate best params on OOS test set
    rm     = RiskManager(initial_capital=backtest_cfg.initial_capital)
    strat  = strategy_cls(rm, **best_params)
    engine = BacktestEngine(backtest_cfg, rm)
    sig_df = strat.run(test_df.copy())
    oos    = engine.run(sig_df)

    logger.info(f"OOS Sharpe={oos.metrics.get('sharpe',0):.2f} "
                f"Return={oos.metrics.get('total_return_pct',0):.1f}%")

    return {
        "best_params":     best_params,
        "in_sample_score": study.best_value,
        "oos_metrics":     oos.metrics,
        "n_trials":        n_trials,
        "strategy":        name,
    }


def optuna_importance_chart(study, output_dir=CONFIG.reports_dir):
    """Plot Optuna parameter importance to see which params matter most."""
    if not OPTUNA_AVAILABLE:
        return
    try:
        import plotly.io as pio
        from optuna.visualization import plot_param_importances, plot_optimization_history

        output_dir.mkdir(parents=True, exist_ok=True)
        fig1 = plot_param_importances(study)
        fig1.write_html(str(output_dir / "optuna_param_importance.html"))
        fig2 = plot_optimization_history(study)
        fig2.write_html(str(output_dir / "optuna_history.html"))
        logger.info(f"Optuna charts saved to {output_dir}")
    except Exception as e:
        logger.debug(f"Optuna chart error: {e}")
