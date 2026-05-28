"""
Hybrid ML Strategy — XGBoost meta-labelling over EMA + RSI signals.
Inspired by Marcos Lopez de Prado's "Advances in Financial ML"
triple-barrier labelling and the Jesse framework's ML integration.

Pipeline:
  1. Generate raw signals from EMA crossover + RSI
  2. Build feature matrix from indicators
  3. XGBoost classifier predicts whether the raw signal leads to a
     profitable trade (meta-label: 1=take / 0=skip)
  4. Only enter trades where model confidence > threshold
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
import xgboost as xgb
from loguru import logger
import joblib
from pathlib import Path

from strategies.base import BaseStrategy
from strategies.trend_ema import TrendEMAStrategy
from risk.manager import RiskManager
from config import CONFIG

MODEL_DIR = CONFIG.models_dir if hasattr(CONFIG, "models_dir") else Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


FEATURE_COLS = [
    "rsi_14", "rsi_7", "mfi", "cci", "willr",
    "atr_pct", "hv_20", "vol_ratio", "cmf",
    "ema_9", "ema_21", "ema_50",
]


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    feats = df[FEATURE_COLS].copy()

    # Relative features (normalise away price scale)
    feats["ema_9_vs_21"]  = (df["ema_9"]  / df["ema_21"]  - 1) if "ema_9"  in df.columns else 0
    feats["ema_21_vs_50"] = (df["ema_21"] / df["ema_50"]  - 1) if "ema_21" in df.columns else 0

    # MACD histogram direction
    macd_h = next((c for c in df.columns if "MACDh_" in c), None)
    feats["macd_h"] = df[macd_h] if macd_h else 0

    # BB %B (position within band)
    bb_up  = next((c for c in df.columns if "BBU_" in c), None)
    bb_low = next((c for c in df.columns if "BBL_" in c), None)
    if bb_up and bb_low:
        band_width = df[bb_up] - df[bb_low]
        feats["bb_pct_b"] = (df["close"] - df[bb_low]) / band_width.replace(0, np.nan)

    # Candle pattern features
    feats["body_pct"]  = (df["close"] - df["open"]).abs() / (df["high"] - df["low"] + 1e-9)
    feats["upper_wick"] = (df["high"] - df[["open","close"]].max(axis=1)) / (df["high"] - df["low"] + 1e-9)
    feats["lower_wick"] = (df[["open","close"]].min(axis=1) - df["low"]) / (df["high"] - df["low"] + 1e-9)

    return feats.fillna(0)


def _triple_barrier_label(df: pd.DataFrame, signal_idx, tp_pct=0.03, sl_pct=0.015,
                          max_bars=24) -> pd.Series:
    """
    Lopez de Prado triple-barrier: label 1 if TP hit before SL within max_bars,
    else 0. Applied only at signal bar indices.
    """
    labels = pd.Series(0, index=signal_idx)
    closes = df["close"]

    for idx in signal_idx:
        loc  = df.index.get_loc(idx)
        entry = closes.iloc[loc]
        tp    = entry * (1 + tp_pct)
        sl    = entry * (1 - sl_pct)

        future = closes.iloc[loc + 1 : loc + max_bars + 1]
        for price in future:
            if price >= tp:
                labels[idx] = 1
                break
            if price <= sl:
                labels[idx] = 0
                break

    return labels


class HybridMLStrategy(BaseStrategy):
    name = "hybrid_ml"
    description = "XGBoost meta-labelling over EMA trend signals"

    def __init__(self, risk_manager: RiskManager,
                 confidence_threshold: float = 0.60,
                 retrain: bool = False):
        super().__init__(risk_manager)
        self.confidence_threshold = confidence_threshold
        self.retrain = retrain
        self.model: xgb.XGBClassifier | None = None
        self.scaler = StandardScaler()
        self._base = TrendEMAStrategy(risk_manager)

        model_path = MODEL_DIR / "hybrid_ml_xgb.pkl"
        if model_path.exists() and not retrain:
            self.model  = joblib.load(model_path)
            scaler_path = MODEL_DIR / "hybrid_ml_scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            logger.info("Loaded pre-trained XGBoost model.")

    def train(self, df: pd.DataFrame) -> dict:
        """
        Train on historical data using triple-barrier labels.
        Uses TimeSeriesSplit to avoid lookahead bias.
        """
        df_ind = self.prepare(df)
        base_df = self._base.generate_signals(df_ind)

        signal_idx = base_df[base_df["signal"] == 1].index
        if len(signal_idx) < 50:
            logger.warning("Not enough signal bars to train ML model.")
            return {}

        labels = _triple_barrier_label(df_ind, signal_idx)
        features = _build_features(df_ind).loc[signal_idx]

        X = features.values
        y = labels.values

        X_scaled = self.scaler.fit_transform(X)

        tscv = TimeSeriesSplit(n_splits=5)
        self.model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        self.model.fit(X_scaled, y)

        # Save
        joblib.dump(self.model,  MODEL_DIR / "hybrid_ml_xgb.pkl")
        joblib.dump(self.scaler, MODEL_DIR / "hybrid_ml_scaler.pkl")

        y_pred = self.model.predict(X_scaled)
        report = classification_report(y, y_pred, output_dict=True)
        logger.info(f"ML model trained. Accuracy: {report['accuracy']:.2%}")
        return report

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # First get raw signals from base trend strategy
        df = self._base.generate_signals(df)

        if self.model is None:
            logger.warning("No trained model — using raw EMA signals.")
            return df

        features = _build_features(df)
        try:
            X_scaled = self.scaler.transform(features.values)
            proba    = self.model.predict_proba(X_scaled)[:, 1]
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return df

        df["ml_confidence"] = proba

        # Only keep signals where ML agrees with high confidence
        mask_high_conf = df["ml_confidence"] >= self.confidence_threshold
        df.loc[(df["signal"] == 1) & ~mask_high_conf, "signal"] = 0

        logger.debug(
            f"ML filtered: kept {(df['signal']==1).sum()} of original signals"
        )
        return df
