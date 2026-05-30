from .trend_ema import TrendEMAStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy
from .hybrid_ml import HybridMLStrategy
from .supertrend import SuperTrendStrategy
from .mtf import MultiTimeframeStrategy
from .vwap_bounce import VWAPBounceStrategy
from .ichimoku import IchimokuStrategy
from .regime_adaptive import RegimeAdaptiveStrategy
from .ensemble import EnsembleStrategy
from .grid_trading import GridTradingStrategy
from .dca import DCAStrategy

STRATEGIES = {
    "trend_ema":       TrendEMAStrategy,
    "mean_reversion":  MeanReversionStrategy,
    "breakout":        BreakoutStrategy,
    "hybrid_ml":       HybridMLStrategy,
    "supertrend":      SuperTrendStrategy,
    "mtf":             MultiTimeframeStrategy,
    "vwap_bounce":     VWAPBounceStrategy,
    "ichimoku":        IchimokuStrategy,
    "regime_adaptive": RegimeAdaptiveStrategy,
    "ensemble":        EnsembleStrategy,
    "grid_trading":    GridTradingStrategy,
    "dca":             DCAStrategy,
}
