"""
ML feature importance analysis.
Shows which indicators drive the XGBoost model's predictions
and helps prune irrelevant features.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from loguru import logger
import joblib

from config import CONFIG


def plot_feature_importance(
    model_path: Path = CONFIG.models_dir / "hybrid_ml_xgb.pkl",
    output_dir: Path = CONFIG.reports_dir,
    top_n: int = 20,
) -> dict:
    """
    Load trained XGBoost model and plot feature importances.
    Returns dict of {feature: importance}.
    """
    if not model_path.exists():
        logger.warning(f"No model found at {model_path}. Train first: python main.py train")
        return {}

    model = joblib.load(model_path)

    # XGBoost feature importance types
    importance_types = {
        "weight":  "Split count (how often feature is used)",
        "gain":    "Average gain per split (most reliable)",
        "cover":   "Average coverage per split",
    }

    results = {}
    for itype, description in importance_types.items():
        try:
            scores = model.get_booster().get_score(importance_type=itype)
            if scores:
                results[itype] = scores
        except Exception:
            pass

    # Use 'gain' as primary (most meaningful)
    primary = results.get("gain", results.get("weight", {}))
    if not primary:
        return {}

    sorted_feats = sorted(primary.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names, vals  = zip(*sorted_feats) if sorted_feats else ([], [])

    # Plot
    fig = go.Figure(go.Bar(
        x=list(vals)[::-1],
        y=list(names)[::-1],
        orientation="h",
        marker_color="#58a6ff",
    ))
    fig.update_layout(
        title=f"XGBoost Feature Importance (gain) — Top {top_n}",
        template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        xaxis_title="Importance (gain)", yaxis_title="Feature",
        font=dict(color="#c9d1d9"), height=max(400, top_n * 25),
        margin=dict(l=150, r=20, t=50, b=50),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "feature_importance.html"
    fig.write_html(str(out))
    logger.info(f"Feature importance chart: {out}")

    # Correlation matrix of features (detect redundancy)
    _plot_feature_correlation(list(names), output_dir)

    return dict(sorted_feats)


def _plot_feature_correlation(feature_names: list[str], output_dir: Path):
    """Stub — needs actual feature data; shows structure for future use."""
    logger.debug("Feature correlation matrix requires training data — skipping stub.")


def get_shap_values(model_path: Path, X: np.ndarray) -> np.ndarray | None:
    """
    Compute SHAP values for interpretability (requires shap package).
    Returns array of shape (n_samples, n_features) or None.
    """
    try:
        import shap
        model = joblib.load(model_path)
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X)
        return shap_vals
    except ImportError:
        logger.debug("shap not installed — pip install shap for SHAP analysis")
        return None
    except Exception as e:
        logger.error(f"SHAP computation failed: {e}")
        return None


def recommend_feature_pruning(importances: dict, threshold: float = 0.01) -> list[str]:
    """
    Return list of features with importance below threshold — candidates for removal.
    Pruning reduces overfitting and speeds up prediction.
    """
    total = sum(importances.values()) or 1
    return [f for f, v in importances.items() if v / total < threshold]
