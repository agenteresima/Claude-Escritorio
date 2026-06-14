"""
Macro prediction market filter.

Aggregates signals from:
  1. Polymarket  — recession / Fed / inflation probabilities
  2. Reddit WSB  — retail sentiment and ticker overcrowding

Produces a MacroGate that the live trader checks before placing orders.

Gate logic:
  Macro risk score >= 75  →  block new longs entirely
  Macro risk score >= 50  →  reduce position size to 50%
  WSB euphoria >= 70      →  reduce position size to 75% (contrarian)
  WSB ticker overcrowded  →  reduce position size to 50% for that ticker
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

from .polymarket import get_macro_risk, MacroRiskReport
from .wsb_sentiment import get_market_mood, get_ticker_signal, WSBMood, WSBTickerSignal

# ─── Thresholds ──────────────────────────────────────────────────────
MACRO_BLOCK_SCORE    = 75   # block new longs
MACRO_CAUTION_SCORE  = 50   # reduce to 50% size
WSB_EUPHORIA_CAUTION = 70   # WSB score → contrarian caution (75% size)

_CACHE_TTL = 3600.0  # 1 hour

# ─── Gate result ─────────────────────────────────────────────────────
@dataclass
class MacroGate:
    allow_long:   bool  = True
    allow_short:  bool  = True   # reserved for future use
    size_factor:  float = 1.0    # multiply position size by this
    macro_score:  float = 0.0
    wsb_score:    int   = 50
    wsb_mood:     str   = "neutral"
    ticker_signal: Optional[WSBTickerSignal] = None
    macro_report:  Optional[MacroRiskReport] = None
    reasons:      list[str] = field(default_factory=list)

    @property
    def reason(self) -> str:
        return " | ".join(self.reasons) if self.reasons else "ok"

    def summary(self) -> str:
        lines = [
            "╔══ Macro Prediction Filter ══════════════════════════════╗",
            f"║  Polymarket macro risk : {self.macro_score:5.1f}/100"
            f" [{self.macro_report.risk_label() if self.macro_report else 'N/A':8}]",
        ]
        if self.macro_report:
            r = self.macro_report
            lines += [
                f"║    Recession prob      : {(r.recession_prob or 0)*100:5.1f}%",
                f"║    Fed hike prob       : {(r.fed_hike_prob  or 0)*100:5.1f}%",
                f"║    Fed cut prob        : {(r.fed_cut_prob   or 0)*100:5.1f}%",
                f"║    Inflation prob      : {(r.inflation_prob or 0)*100:5.1f}%",
            ]
        lines += [
            f"║  WSB mood              : {self.wsb_mood:10} ({self.wsb_score:3}/100)",
            f"║  Allow long            : {'✅ YES' if self.allow_long else '🚫 NO '}",
            f"║  Position size factor  : {self.size_factor*100:.0f}%",
            f"║  Reason                : {self.reason}",
            "╚═════════════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# ─── Cache ────────────────────────────────────────────────────────────
_cached_gate: Optional[MacroGate] = None
_cached_at:   float = 0.0


def get_macro_gate(ticker: str | None = None, force_refresh: bool = False) -> MacroGate:
    """
    Compute (or return cached) macro gate for the current market environment.

    Args:
        ticker:        Optional ticker to check for WSB overcrowding.
        force_refresh: If True, bypasses cache and re-fetches all sources.

    Returns:
        MacroGate with allow_long, size_factor, and detailed reasons.
    """
    global _cached_gate, _cached_at

    # Use cache when available and ticker check not needed
    if not force_refresh and _cached_gate and not ticker:
        if time.time() - _cached_at < _CACHE_TTL:
            return _cached_gate

    gate    = MacroGate()
    reasons: list[str] = []

    # ── 1. Polymarket macro risk ──────────────────────────────────────
    try:
        report = get_macro_risk()
        gate.macro_score  = report.score
        gate.macro_report = report

        if report.score >= MACRO_BLOCK_SCORE:
            gate.allow_long  = False
            gate.size_factor = 0.0
            reasons.append(
                f"Polymarket macro risk {report.score:.0f}/100 ≥ {MACRO_BLOCK_SCORE} "
                f"(recession {(report.recession_prob or 0)*100:.0f}%)"
            )
        elif report.score >= MACRO_CAUTION_SCORE:
            gate.size_factor = min(gate.size_factor, 0.50)
            reasons.append(
                f"Polymarket macro risk {report.score:.0f}/100 → 50% size "
                f"(recession {(report.recession_prob or 0)*100:.0f}%, "
                f"hike {(report.fed_hike_prob or 0)*100:.0f}%)"
            )
    except Exception as e:
        logger.warning(f"Polymarket gate error: {e}")

    # ── 2. Reddit WSB mood ────────────────────────────────────────────
    try:
        mood = get_market_mood()
        gate.wsb_score = mood.score
        gate.wsb_mood  = mood.mood

        if mood.score >= WSB_EUPHORIA_CAUTION:
            gate.size_factor = min(gate.size_factor, 0.75)
            reasons.append(f"WSB euphoria {mood.score}/100 → contrarian caution (75% size)")
        elif mood.mood == "fearful":
            # Extreme fear on WSB sometimes signals capitulation (contrarian bullish)
            reasons.append(f"WSB fearful ({mood.score}/100) — potential capitulation zone")
    except Exception as e:
        logger.warning(f"WSB mood gate error: {e}")

    # ── 3. Per-ticker WSB overcrowding ────────────────────────────────
    if ticker:
        try:
            sig = get_ticker_signal(ticker)
            gate.ticker_signal = sig
            if sig.signal == "overcrowded":
                gate.size_factor = min(gate.size_factor, 0.50)
                reasons.append(
                    f"{ticker} WSB overcrowded ({sig.mentions} mentions in hot) → 50% size"
                )
            elif sig.signal == "momentum":
                reasons.append(f"{ticker} trending on WSB ({sig.mentions} mentions) ✓")
        except Exception as e:
            logger.warning(f"WSB ticker gate error [{ticker}]: {e}")

    gate.reasons = reasons

    # Cache result (only when no per-ticker check to keep it generic)
    if not ticker:
        _cached_gate = gate
        _cached_at   = time.time()

    return gate


def clear_cache() -> None:
    global _cached_gate, _cached_at
    _cached_gate = None
    _cached_at   = 0.0
