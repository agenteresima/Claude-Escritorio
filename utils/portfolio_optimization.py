import numpy as np
import pandas as pd
from loguru import logger


def _equal_weights(n: int, index: pd.Index) -> pd.Series:
    return pd.Series(np.ones(n) / n, index=index)


def _cov_matrix(returns: pd.DataFrame) -> np.ndarray:
    return returns.cov().values


def min_variance_weights(returns: pd.DataFrame, risk_free: float = 0.0) -> pd.Series:
    tickers = returns.columns
    n = len(tickers)
    if n == 0 or returns.empty:
        return pd.Series(dtype=float)

    if n == 1:
        return pd.Series([1.0], index=tickers)

    try:
        cov = _cov_matrix(returns.dropna())
        if np.any(np.isnan(cov)) or np.any(np.isinf(cov)):
            raise ValueError("Covariance matrix contains NaN/Inf")

        inv_cov = np.linalg.pinv(cov)
        ones = np.ones(n)
        raw_w = inv_cov @ ones
        raw_w = np.clip(raw_w, 0.0, None)
        total = raw_w.sum()
        if total <= 0:
            raise ValueError("All weights zero after clipping")
        weights = raw_w / total
        weights = np.clip(weights, 0.0, 1.0)
        weights = weights / weights.sum()
        return pd.Series(weights, index=tickers)
    except Exception as e:
        logger.warning(f"min_variance_weights failed ({e}), falling back to equal weights")
        return _equal_weights(n, tickers)


def max_sharpe_weights(returns: pd.DataFrame, risk_free: float = 0.0) -> pd.Series:
    tickers = returns.columns
    n = len(tickers)
    if n == 0 or returns.empty:
        return pd.Series(dtype=float)

    if n == 1:
        return pd.Series([1.0], index=tickers)

    try:
        clean = returns.dropna()
        if len(clean) < 2:
            raise ValueError("Not enough data rows")

        mean_r = clean.mean().values
        cov = _cov_matrix(clean)
        if np.any(np.isnan(cov)) or np.any(np.isnan(mean_r)):
            raise ValueError("NaN in mean/cov")

        n_sim = 2000
        rng = np.random.default_rng(42)
        best_sharpe = -np.inf
        best_w = np.ones(n) / n

        for _ in range(n_sim):
            raw = rng.exponential(1.0, n)
            w = raw / raw.sum()
            port_ret = w @ mean_r
            port_var = w @ cov @ w
            if port_var <= 0:
                continue
            sharpe = (port_ret - risk_free) / np.sqrt(port_var)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_w = w

        best_w = np.clip(best_w, 0.0, 1.0)
        best_w = best_w / best_w.sum()
        return pd.Series(best_w, index=tickers)
    except Exception as e:
        logger.warning(f"max_sharpe_weights failed ({e}), falling back to equal weights")
        return _equal_weights(n, tickers)


def risk_parity_weights(returns: pd.DataFrame) -> pd.Series:
    tickers = returns.columns
    n = len(tickers)
    if n == 0 or returns.empty:
        return pd.Series(dtype=float)

    if n == 1:
        return pd.Series([1.0], index=tickers)

    try:
        window = min(252, len(returns))
        recent = returns.tail(window).dropna()
        if recent.empty:
            raise ValueError("No data after dropna")

        vols = recent.std().values
        vols = np.where(vols <= 0, np.nan, vols)
        if np.all(np.isnan(vols)):
            raise ValueError("All volatilities are zero")

        inv_vol = np.where(np.isnan(vols), 0.0, 1.0 / vols)
        total = inv_vol.sum()
        if total <= 0:
            raise ValueError("Sum of inverse vols is zero")

        weights = inv_vol / total
        weights = np.clip(weights, 0.0, 1.0)
        weights = weights / weights.sum()
        return pd.Series(weights, index=tickers)
    except Exception as e:
        logger.warning(f"risk_parity_weights failed ({e}), falling back to equal weights")
        return _equal_weights(n, tickers)


def compute_portfolio_metrics(
    weights: pd.Series,
    returns: pd.DataFrame,
    benchmark_returns: pd.Series | None = None,
    risk_free: float = 0.0,
    freq: int = 252,
) -> dict:
    metrics: dict = {}

    if weights.empty or returns.empty:
        return metrics

    try:
        aligned_tickers = [t for t in weights.index if t in returns.columns]
        if not aligned_tickers:
            return metrics

        w = weights[aligned_tickers]
        w = w / w.sum() if w.sum() > 0 else w

        port_ret = returns[aligned_tickers].dropna().dot(w)

        if port_ret.empty:
            return metrics

        ann_ret = port_ret.mean() * freq
        ann_vol = port_ret.std() * np.sqrt(freq)
        metrics["annual_return"] = float(ann_ret)
        metrics["annual_vol"] = float(ann_vol)

        metrics["sharpe"] = float(
            (ann_ret - risk_free) / ann_vol if ann_vol > 0 else 0.0
        )

        downside = port_ret[port_ret < risk_free / freq]
        downside_std = downside.std() * np.sqrt(freq) if len(downside) > 1 else 0.0
        metrics["sortino"] = float(
            (ann_ret - risk_free) / downside_std if downside_std > 0 else 0.0
        )

        equity = (1 + port_ret).cumprod()
        roll_max = equity.cummax()
        drawdown = (equity - roll_max) / roll_max
        max_dd = float(drawdown.min())
        metrics["max_drawdown"] = max_dd

        metrics["calmar"] = float(
            ann_ret / abs(max_dd) if max_dd != 0 else 0.0
        )

        if benchmark_returns is not None and not benchmark_returns.empty:
            try:
                bench = benchmark_returns.reindex(port_ret.index).dropna()
                port_aligned = port_ret.reindex(bench.index).dropna()

                if len(port_aligned) > 1:
                    cov_matrix = np.cov(port_aligned.values, bench.values)
                    beta = float(
                        cov_matrix[0, 1] / cov_matrix[1, 1]
                        if cov_matrix[1, 1] > 0
                        else 0.0
                    )
                    bench_ann = bench.mean() * freq
                    alpha = float(ann_ret - (risk_free + beta * (bench_ann - risk_free)))
                    active_ret = port_aligned.values - bench.values
                    tracking_err = float(active_ret.std() * np.sqrt(freq))
                    info_ratio = float(
                        active_ret.mean() * freq / tracking_err
                        if tracking_err > 0
                        else 0.0
                    )
                    metrics["alpha"] = alpha
                    metrics["beta"] = beta
                    metrics["tracking_error"] = tracking_err
                    metrics["information_ratio"] = info_ratio
            except Exception as e:
                logger.warning(f"Benchmark metrics failed: {e}")

    except Exception as e:
        logger.warning(f"compute_portfolio_metrics failed: {e}")

    return metrics


def rolling_rebalance(
    returns: pd.DataFrame,
    method: str = "risk_parity",
    lookback: int = 252,
    rebal_freq: int = 21,
) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)

    _method_map = {
        "risk_parity": risk_parity_weights,
        "min_variance": min_variance_weights,
        "max_sharpe": max_sharpe_weights,
    }

    weight_fn = _method_map.get(method)
    if weight_fn is None:
        logger.warning(f"Unknown method '{method}', defaulting to risk_parity")
        weight_fn = risk_parity_weights

    equity = 10_000.0
    equity_curve: list[float] = []
    index: list = []
    current_weights: pd.Series | None = None

    for i in range(len(returns)):
        row_date = returns.index[i]

        rebalance_due = (i % rebal_freq == 0) or (current_weights is None)
        if rebalance_due:
            start_idx = max(0, i - lookback)
            window = returns.iloc[start_idx:i]
            if len(window) >= 2:
                try:
                    new_w = weight_fn(window)
                    if not new_w.empty and new_w.sum() > 0:
                        current_weights = new_w
                    else:
                        raise ValueError("Empty or zero-sum weights")
                except Exception as e:
                    logger.debug(f"Weight computation at bar {i} failed: {e}")
                    if current_weights is None:
                        n = returns.shape[1]
                        current_weights = _equal_weights(n, returns.columns)
            else:
                n = returns.shape[1]
                current_weights = _equal_weights(n, returns.columns)

        if current_weights is not None:
            row_rets = returns.iloc[i]
            aligned = [t for t in current_weights.index if t in row_rets.index]
            if aligned:
                w = current_weights[aligned]
                w = w / w.sum() if w.sum() > 0 else w
                port_r = float(row_rets[aligned].fillna(0.0).dot(w))
                equity *= 1 + port_r

        equity_curve.append(equity)
        index.append(row_date)

    result = pd.Series(equity_curve, index=index, name=f"equity_{method}")
    logger.info(
        f"rolling_rebalance ({method}): {len(result)} bars, "
        f"final equity={equity:.2f}, return={((equity/10000)-1)*100:.1f}%"
    )
    return result
