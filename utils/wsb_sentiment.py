"""
Reddit WallStreetBets sentiment scraper.

Uses Reddit's public JSON API (no API key required) to:
  1. Count ticker mentions in hot posts → momentum / overcrowding signal
  2. Detect bullish/bearish keywords → market mood score

Contrarian interpretation (standard WSB behaviour):
  - Very high mentions (>20 in top-100 hot posts) → overcrowded → caution
  - Medium mentions (5–20)                         → genuine momentum
  - Low / zero mentions                            → neutral
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from collections import Counter
from typing import Optional

import requests
from loguru import logger

# ─── Config ──────────────────────────────────────────────────────────
_WSB_HOT    = "https://www.reddit.com/r/wallstreetbets/hot.json"
_WSB_NEW    = "https://www.reddit.com/r/wallstreetbets/new.json"
_HEADERS    = {"User-Agent": "ProfessionalTradingBot/2.0 (educational use)"}
_TTL        = 900   # 15 min cache

_TICKER_RE  = re.compile(r'\b([A-Z]{1,5})\b')

# Tokens that look like tickers but are not
_EXCLUDE: set[str] = {
    "I", "A", "U", "DD", "OG", "IV", "ATH", "EV", "AI", "IPO",
    "WSB", "SEC", "FED", "IRS", "GDP", "CPI", "CEO", "CFO", "ETF",
    "THE", "AND", "OR", "FOR", "IN", "ON", "AT", "TO", "OF", "IF",
    "IS", "IT", "MY", "WE", "DO", "NO", "UP", "GO", "AM", "PM",
    "YOLO", "FOMO", "HODL", "TLDR", "IMO", "LMAO", "LOL", "OMG",
    "US", "UK", "EU", "UN", "IMF", "NYSE", "NASDAQ", "OTC",
}

_BULLISH_WORDS = {
    "bull", "calls", "call", "moon", "mooning", "buy", "buying",
    "long", "green", "pump", "pumping", "rocket", "squeeze", "squeeze",
    "yolo", "tendies", "gains", "print", "printing", "run",
}
_BEARISH_WORDS = {
    "bear", "puts", "put", "crash", "crashing", "short", "shorting",
    "red", "dump", "dumping", "sell", "selling", "rekt", "rug",
    "collapse", "bankrupt", "bankruptcy", "margin call",
}

# ─── Cache ───────────────────────────────────────────────────────────
_cache: dict[str, dict] = {}


# ─── Data models ─────────────────────────────────────────────────────
@dataclass
class WSBTickerSignal:
    ticker:       str
    mentions:     int
    signal:       str   # "neutral" | "momentum" | "overcrowded"
    bias:         str   # "neutral" | "positive" | "contrarian_caution"
    size_factor:  float # 1.0 = full, 0.5 = reduced (overcrowded)
    source:       str = "reddit_wsb"


@dataclass
class WSBMood:
    mood:        str    # "fearful" | "bearish" | "neutral" | "bullish" | "euphoric"
    score:       int    # 0–100 (bull ratio × 100)
    bull_count:  int
    bear_count:  int
    top_tickers: dict[str, int]  # {ticker: mention_count}
    source:      str = "reddit_wsb"

    def risk_label(self) -> str:
        if self.score >= 70: return "euphoric"
        if self.score >= 55: return "bullish"
        if self.score >= 45: return "neutral"
        if self.score >= 30: return "bearish"
        return "fearful"


# ─── HTTP helper ─────────────────────────────────────────────────────
def _fetch_posts(url: str, limit: int = 100) -> Optional[list[dict]]:
    key = url
    if key in _cache and time.time() - _cache[key]["ts"] < _TTL:
        return _cache[key]["data"]
    try:
        r = requests.get(url, params={"limit": limit}, headers=_HEADERS, timeout=10)
        r.raise_for_status()
        posts = r.json()["data"]["children"]
        _cache[key] = {"data": posts, "ts": time.time()}
        return posts
    except requests.Timeout:
        logger.warning("Reddit WSB API timeout")
        return None
    except Exception as e:
        logger.warning(f"Reddit WSB fetch error: {e}")
        return None


# ─── Ticker mention counter ───────────────────────────────────────────
def get_ticker_mentions(
    tickers: list[str] | None = None,
    limit: int = 100,
) -> dict[str, int]:
    """
    Returns a dict of {TICKER: mention_count} from the WSB hot feed.
    If `tickers` is given, only those tickers are counted.
    Otherwise returns the top 30 most-mentioned tickers.
    """
    posts = _fetch_posts(_WSB_HOT, limit=limit)
    if not posts:
        return {}

    counts: Counter = Counter()
    for post in posts:
        d    = post["data"]
        text = f"{d.get('title', '')} {d.get('selftext', '')}"
        for t in _TICKER_RE.findall(text):
            if t not in _EXCLUDE and len(t) >= 2:
                counts[t] += 1

    if tickers:
        return {t.upper(): counts.get(t.upper(), 0) for t in tickers}
    return dict(counts.most_common(30))


# ─── Per-ticker signal ────────────────────────────────────────────────
def get_ticker_signal(ticker: str) -> WSBTickerSignal:
    """Compute momentum/contrarian signal for a single ticker."""
    mentions = get_ticker_mentions()
    count    = mentions.get(ticker.upper(), 0)

    if count > 20:
        signal      = "overcrowded"
        bias        = "contrarian_caution"
        size_factor = 0.5
    elif count > 5:
        signal      = "momentum"
        bias        = "positive"
        size_factor = 1.0
    else:
        signal      = "neutral"
        bias        = "neutral"
        size_factor = 1.0

    return WSBTickerSignal(
        ticker      = ticker.upper(),
        mentions    = count,
        signal      = signal,
        bias        = bias,
        size_factor = size_factor,
    )


# ─── Overall market mood ─────────────────────────────────────────────
def get_market_mood(limit: int = 100) -> WSBMood:
    """
    Aggregate WSB bullish/bearish keyword count → mood score.
    Also returns top tickers being discussed.
    """
    posts = _fetch_posts(_WSB_HOT, limit=limit)
    if not posts:
        return WSBMood(mood="unknown", score=50, bull_count=0, bear_count=0, top_tickers={})

    bull_count = bear_count = 0
    for post in posts:
        d    = post["data"]
        text = (d.get("title", "") + " " + d.get("selftext", "")).lower()
        bull_count += sum(text.count(w) for w in _BULLISH_WORDS)
        bear_count += sum(text.count(w) for w in _BEARISH_WORDS)

    total = bull_count + bear_count or 1
    score = int(bull_count / total * 100)

    if score >= 70:  mood = "euphoric"
    elif score >= 55: mood = "bullish"
    elif score >= 45: mood = "neutral"
    elif score >= 30: mood = "bearish"
    else:             mood = "fearful"

    top_tickers = get_ticker_mentions()

    return WSBMood(
        mood        = mood,
        score       = score,
        bull_count  = bull_count,
        bear_count  = bear_count,
        top_tickers = top_tickers,
    )


# ─── Batch signal for S&P 500 universe ───────────────────────────────
def get_universe_signals(tickers: list[str]) -> dict[str, WSBTickerSignal]:
    """Get WSB signals for an entire list of tickers in one API call."""
    mentions = get_ticker_mentions(tickers=tickers)
    return {t: WSBTickerSignal(
        ticker      = t,
        mentions    = mentions.get(t, 0),
        signal      = "overcrowded" if mentions.get(t, 0) > 20 else
                      "momentum"    if mentions.get(t, 0) > 5 else "neutral",
        bias        = "contrarian_caution" if mentions.get(t, 0) > 20 else
                      "positive"           if mentions.get(t, 0) > 5 else "neutral",
        size_factor = 0.5 if mentions.get(t, 0) > 20 else 1.0,
    ) for t in tickers}
