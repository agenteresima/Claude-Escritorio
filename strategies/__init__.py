from .trend_ema import TrendEMAStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy
from .hybrid_ml import HybridMLStrategy

STRATEGIES = {
    "trend_ema":      TrendEMAStrategy,
    "mean_reversion": MeanReversionStrategy,
    "breakout":       BreakoutStrategy,
    "hybrid_ml":      HybridMLStrategy,
}
