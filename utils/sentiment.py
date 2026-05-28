"""
Market sentiment indicators:
  1. Fear & Greed Index (alternative.me API)
  2. Funding rate (perps — indicates overleveraged longs/shorts)
  3. Long/Short ratio

Used as macro filters: avoid longs when Fear&Greed > 80 (extreme greed),
avoid shorts when < 20 (extreme fear). Contrarian at extremes.
"""
import time
from datetime import datetime
from typing import Optional
import requests
from loguru import logger


def get_fear_greed(limit: int = 30) -> list[dict]:
    """
    Returns list of {value, value_classification, timestamp} from
    the alternative.me API. Cached for 1 hour.
    """
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [
            {
                "value":          int(d["value"]),
                "classification": d["value_classification"],
                "timestamp":      datetime.fromtimestamp(int(d["timestamp"])),
            }
            for d in data
        ]
    except Exception as e:
        logger.warning(f"Fear & Greed API error: {e}")
        return []


def get_current_fng() -> Optional[dict]:
    data = get_fear_greed(limit=1)
    return data[0] if data else None


def fng_signal_filter(fng_value: int) -> str:
    """
    Returns trading bias based on Fear & Greed.
    Contrarian: extreme greed → cautious on longs.
    """
    if fng_value >= 80:
        return "avoid_longs"     # extreme greed — market overextended
    elif fng_value >= 60:
        return "neutral"
    elif fng_value >= 40:
        return "neutral"
    elif fng_value >= 20:
        return "neutral"
    else:
        return "avoid_shorts"    # extreme fear — potential capitulation


def get_funding_rate(symbol: str = "BTC/USDT:USDT",
                     exchange_name: str = "binance") -> Optional[float]:
    """
    Fetch perpetual funding rate from CCXT.
    Positive = longs pay shorts (market bullish/overextended).
    Negative = shorts pay longs (market bearish).
    """
    try:
        import ccxt
        exchange = getattr(ccxt, exchange_name)({"enableRateLimit": True})
        funding  = exchange.fetch_funding_rate(symbol)
        rate     = float(funding.get("fundingRate", 0))
        logger.debug(f"Funding rate {symbol}: {rate:.6f}")
        return rate
    except Exception as e:
        logger.debug(f"Funding rate unavailable: {e}")
        return None


def sentiment_gate(fng_value: Optional[int] = None,
                   funding_rate: Optional[float] = None) -> dict:
    """
    Aggregate sentiment gate.
    Returns {"allow_long": bool, "allow_short": bool, "reason": str}
    """
    allow_long  = True
    allow_short = True
    reasons     = []

    if fng_value is not None:
        bias = fng_signal_filter(fng_value)
        if bias == "avoid_longs":
            allow_long = False
            reasons.append(f"FnG extreme greed ({fng_value})")
        elif bias == "avoid_shorts":
            allow_short = False
            reasons.append(f"FnG extreme fear ({fng_value})")

    if funding_rate is not None:
        if funding_rate > 0.001:   # >0.1 % 8h funding
            allow_long = False
            reasons.append(f"High funding rate ({funding_rate:.4f}) — longs overextended")
        elif funding_rate < -0.001:
            allow_short = False
            reasons.append(f"Negative funding ({funding_rate:.4f}) — shorts overextended")

    return {
        "allow_long":  allow_long,
        "allow_short": allow_short,
        "reason":      " | ".join(reasons) if reasons else "ok",
    }
