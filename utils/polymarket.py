"""
Polymarket prediction market client.

Fetches real-time probabilities for macro market events:
  - US recession probability
  - Federal Reserve rate decisions
  - Inflation / CPI outcomes
  - S&P 500 price targets

API: https://gamma-api.polymarket.com (no API key required)
Cache TTL: 1 hour (markets move slowly)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from loguru import logger

# ─── Config ──────────────────────────────────────────────────────────
_BASE    = "https://gamma-api.polymarket.com"
_HEADERS = {"User-Agent": "ProfessionalTradingBot/2.0 (educational use)"}
_TTL     = 3600  # 1 hour cache

# Macro search queries and their weights in the risk score
_MACRO_QUERIES: list[tuple[str, float]] = [
    ("US recession 2025",              0.45),  # highest weight
    ("Federal Reserve rate cut 2025",  0.25),
    ("Federal Reserve rate hike 2025", 0.20),
    ("US inflation CPI",               0.10),
]

# ─── Cache ───────────────────────────────────────────────────────────
_cache: dict[str, dict] = {}


# ─── Data model ──────────────────────────────────────────────────────
@dataclass
class PolyMarket:
    question:  str
    yes_prob:  float       # 0.0 – 1.0
    volume:    float       # USD volume (higher = more reliable)
    slug:      str = ""
    source:    str = "polymarket"


@dataclass
class MacroRiskReport:
    score:            float              # 0–100: higher = more risk
    recession_prob:   Optional[float]   # 0–1
    fed_cut_prob:     Optional[float]   # 0–1 (rate CUT)
    fed_hike_prob:    Optional[float]   # 0–1 (rate HIKE)
    inflation_prob:   Optional[float]   # 0–1 (CPI above target)
    top_markets:      list[PolyMarket] = field(default_factory=list)
    fetched_at:       float = field(default_factory=time.time)

    def risk_label(self) -> str:
        if self.score >= 75: return "HIGH"
        if self.score >= 50: return "ELEVATED"
        if self.score >= 25: return "MODERATE"
        return "LOW"

    def as_dict(self) -> dict:
        return {
            "score":          round(self.score, 1),
            "risk_label":     self.risk_label(),
            "recession_prob": round(self.recession_prob or 0, 3),
            "fed_cut_prob":   round(self.fed_cut_prob   or 0, 3),
            "fed_hike_prob":  round(self.fed_hike_prob  or 0, 3),
            "inflation_prob": round(self.inflation_prob or 0, 3),
        }


# ─── HTTP helper ─────────────────────────────────────────────────────
def _get(endpoint: str, params: dict | None = None) -> Optional[list | dict]:
    key = f"{endpoint}:{params}"
    if key in _cache and time.time() - _cache[key]["ts"] < _TTL:
        return _cache[key]["data"]
    try:
        r = requests.get(
            f"{_BASE}{endpoint}",
            params=params,
            headers=_HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        _cache[key] = {"data": data, "ts": time.time()}
        return data
    except requests.Timeout:
        logger.warning("Polymarket API timeout")
        return None
    except requests.HTTPError as e:
        logger.warning(f"Polymarket HTTP error: {e}")
        return None
    except Exception as e:
        logger.warning(f"Polymarket error: {e}")
        return None


# ─── Market search ───────────────────────────────────────────────────
def search_markets(query: str, limit: int = 5) -> list[PolyMarket]:
    """Search Polymarket for active markets matching a query string."""
    data = _get("/markets", {"search": query, "limit": limit, "active": "true"})
    if not data:
        return []

    results: list[PolyMarket] = []
    for m in data:
        try:
            prices   = m.get("outcomePrices") or []
            outcomes = m.get("outcomes")      or []
            if not prices or not outcomes:
                continue

            # Find the YES outcome (binary markets)
            yes_idx  = next((i for i, o in enumerate(outcomes) if str(o).lower() == "yes"), 0)
            yes_prob = float(prices[yes_idx]) if yes_idx < len(prices) else 0.5
            volume   = float(m.get("volume") or 0)

            results.append(PolyMarket(
                question = m.get("question", query),
                yes_prob = yes_prob,
                volume   = volume,
                slug     = m.get("slug", ""),
            ))
        except (ValueError, IndexError, KeyError, TypeError):
            continue

    return results


def _volume_weighted_prob(markets: list[PolyMarket]) -> Optional[float]:
    """Return volume-weighted average YES probability across markets."""
    if not markets:
        return None
    total_vol = sum(m.volume for m in markets)
    if total_vol < 1:
        return markets[0].yes_prob  # fallback: equal weight
    return sum(m.yes_prob * m.volume for m in markets) / total_vol


# ─── Specific probability getters ────────────────────────────────────
def get_recession_probability() -> Optional[float]:
    """US recession probability from prediction market consensus."""
    markets = search_markets("US recession 2025", limit=5)
    return _volume_weighted_prob(markets)


def get_fed_cut_probability() -> Optional[float]:
    """Probability the Fed cuts rates at the next/upcoming meeting."""
    markets = search_markets("Federal Reserve rate cut 2025", limit=5)
    return _volume_weighted_prob(markets)


def get_fed_hike_probability() -> Optional[float]:
    """Probability the Fed hikes rates."""
    markets = search_markets("Federal Reserve rate hike 2025", limit=3)
    return _volume_weighted_prob(markets)


def get_inflation_probability() -> Optional[float]:
    """Probability CPI remains above Fed target."""
    markets = search_markets("US inflation CPI 2025", limit=3)
    return _volume_weighted_prob(markets)


# ─── Aggregated macro risk ────────────────────────────────────────────
def get_macro_risk(use_cache: bool = True) -> MacroRiskReport:
    """
    Compute an aggregated macro risk score 0–100.

    Score components (weights sum to 1.0):
      Recession probability  × 0.45
      Fed hike probability   × 0.20
      1 – Fed cut prob       × 0.25  (no cut = tighter = bearish)
      Inflation probability  × 0.10

    Score interpretation:
      0–25   LOW      — full position sizing
      25–50  MODERATE — proceed with normal caution
      50–75  ELEVATED — reduce position size by 25–50%
      75+    HIGH     — block new longs
    """
    if not use_cache:
        _cache.clear()

    recession_p  = get_recession_probability()
    fed_cut_p    = get_fed_cut_probability()
    fed_hike_p   = get_fed_hike_probability()
    inflation_p  = get_inflation_probability()

    # Build score (all probabilities in 0–1 range → scale to 0–100)
    score = 0.0
    total_w = 0.0

    if recession_p is not None:
        score   += recession_p * 0.45 * 100
        total_w += 0.45
    if fed_hike_p is not None:
        score   += fed_hike_p * 0.20 * 100
        total_w += 0.20
    if fed_cut_p is not None:
        score   += (1.0 - fed_cut_p) * 0.25 * 100   # no cut = risk
        total_w += 0.25
    if inflation_p is not None:
        score   += inflation_p * 0.10 * 100
        total_w += 0.10

    # Normalize if some sources unavailable
    if total_w > 0 and total_w < 1.0:
        score = score / total_w
    elif total_w == 0:
        score = 30.0   # neutral default when API unavailable

    # Gather a sample of top markets for the report
    top = search_markets("recession OR Fed rate OR inflation", limit=5)

    return MacroRiskReport(
        score          = min(100.0, max(0.0, score)),
        recession_prob = recession_p,
        fed_cut_prob   = fed_cut_p,
        fed_hike_prob  = fed_hike_p,
        inflation_prob = inflation_p,
        top_markets    = top,
    )
