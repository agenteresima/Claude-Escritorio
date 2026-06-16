"""
AI Trading Advisor — conversational agent with tool calling.

Answers questions like:
  "¿Qué activos están listos para entrar ahora?"
  "¿BTC pasa todos los filtros para invertir?"
  "¿Cuál es el entorno macro actual?"
  "¿NVDA tiene señal de compra?"

Uses Claude (claude-sonnet-4-6) with tool use to fetch real-time data
from the bot's own analysis pipeline.
"""
from __future__ import annotations

import json
from typing import Any

import anthropic
from loguru import logger

from config import CONFIG
from utils.macro_filter import get_macro_gate
from utils.sentiment import get_current_fng, get_funding_rate
from utils.events_filter import EventsFilter
from utils.candle_patterns import add_candle_patterns
from utils.wsb_sentiment import get_ticker_signal, get_market_mood
from utils.polymarket import get_macro_risk


# ─── System prompt ────────────────────────────────────────────────────

_SYSTEM = """You are an expert trading advisor for a professional algorithmic trading bot.

You analyze trading opportunities using real-time data from multiple sources:
- Technical strategy signals (EMA, RSI, MACD, ATR)
- Polymarket prediction markets (recession, Fed rate probabilities)
- Reddit WallStreetBets sentiment (contrarian when overcrowded)
- Fear & Greed Index + funding rates
- Economic events blackout filter
- Candle pattern confirmation

RESPONSE GUIDELINES:
- Always respond in the same language as the user (Spanish if they write in Spanish)
- Be concise, direct, data-driven
- Use ✅ for pass, 🚫 for fail/block, ⚠️ for caution
- Give a clear final verdict: BUY / WAIT / AVOID
- Show position size factor when macro/WSB suggests reducing
- For multiple assets use a compact table format
- If macro risk is HIGH, always warn prominently

RISK RULES (non-negotiable):
- Never recommend entering when macro gate blocks longs (score ≥ 75)
- Max 2% portfolio risk per trade
- Always mention if size should be reduced due to macro/WSB conditions"""


# ─── Tool schemas ─────────────────────────────────────────────────────

_TOOLS: list[dict] = [
    {
        "name": "check_asset",
        "description": (
            "Run a complete entry-readiness check on a single asset. "
            "Fetches price data, runs the active strategy, checks the macro filter, "
            "WSB sentiment, events filter, and candle patterns. "
            "Use this to answer 'Does X pass the parameters to invest right now?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": (
                        "Asset symbol. "
                        "Crypto pair: 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'. "
                        "Stock: 'NVDA', 'TSLA', 'AAPL', 'SPY'."
                    ),
                },
                "strategy": {
                    "type": "string",
                    "description": "Strategy to evaluate with. Default: trend_ema",
                    "enum": ["trend_ema", "mean_reversion", "breakout", "hybrid_ml"],
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "scan_watchlist",
        "description": (
            "Scan multiple assets simultaneously and return which ones have buy signals "
            "and pass all entry filters. "
            "Use this to answer 'Which assets are ready to enter right now?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of symbols to scan (crypto pairs or stock tickers).",
                },
            },
            "required": ["symbols"],
        },
    },
    {
        "name": "get_macro_environment",
        "description": (
            "Get the current macro environment from Polymarket prediction markets. "
            "Returns recession probability, Fed rate decision odds, inflation outlook, "
            "and the aggregated macro risk score + WSB overall mood. "
            "Always call this first to understand the big picture."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_market_sentiment",
        "description": (
            "Get crypto market sentiment: Fear & Greed index (0=extreme fear, 100=extreme greed), "
            "BTC perpetual funding rate, and Reddit WSB market mood + top trending tickers."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ─── Tool implementations ─────────────────────────────────────────────

def _is_crypto(symbol: str) -> bool:
    return "/" in symbol


def _check_asset(symbol: str, strategy: str = "trend_ema") -> dict[str, Any]:
    """Full entry-readiness check — runs every filter in order."""
    result: dict[str, Any] = {
        "symbol":  symbol,
        "price":   None,
        "signal":  None,
        "verdict": "WAIT",
        "checks":  {},
        "reasons": [],
    }
    df = None

    # ── 1. Strategy signal ────────────────────────────────────────────
    try:
        from strategies import STRATEGIES
        from risk.manager import RiskManager
        from data.fetcher import fetch_ohlcv_ccxt, fetch_ohlcv_yfinance

        StratCls = STRATEGIES.get(strategy) or STRATEGIES["trend_ema"]
        strat    = StratCls(RiskManager(initial_capital=10_000))

        if _is_crypto(symbol):
            df = fetch_ohlcv_ccxt(symbol, "1h", limit=500, exchange_name=CONFIG.exchange.name)
        else:
            df = fetch_ohlcv_yfinance(symbol, "1d", start="2023-01-01")

        sig_df   = strat.run(df)
        last_row = sig_df.iloc[-1]
        signal   = int(last_row.get("signal", 0))
        price    = float(last_row["close"])

        result["price"]  = price
        result["signal"] = signal
        result["checks"]["strategy"] = {
            "pass":     signal == 1,
            "signal":   signal,
            "strategy": strategy,
            "price":    price,
        }
        if signal != 1:
            result["reasons"].append(
                f"Strategy {strategy}: no buy signal (signal={signal}, need 1)"
            )
    except Exception as e:
        result["checks"]["strategy"] = {"pass": False, "error": str(e)}
        result["reasons"].append(f"Strategy data unavailable: {e}")

    # ── 2. Economic events filter ─────────────────────────────────────
    try:
        safe, reason = EventsFilter().is_safe_to_trade()
        result["checks"]["events"] = {"pass": safe, "reason": reason or "ok"}
        if not safe:
            result["reasons"].append(f"Events blackout: {reason}")
    except Exception as e:
        result["checks"]["events"] = {"pass": True, "note": str(e)}

    # ── 3. Macro prediction filter ────────────────────────────────────
    ticker_base = symbol.split("/")[0]
    try:
        macro_gate = get_macro_gate(ticker=ticker_base)
        result["checks"]["macro"] = {
            "pass":         macro_gate.allow_long,
            "score":        round(macro_gate.macro_score, 1),
            "risk_label":   macro_gate.macro_report.risk_label() if macro_gate.macro_report else "N/A",
            "size_factor":  macro_gate.size_factor,
            "wsb_mood":     macro_gate.wsb_mood,
            "wsb_score":    macro_gate.wsb_score,
            "reason":       macro_gate.reason or "ok",
        }
        if macro_gate.macro_report:
            r = macro_gate.macro_report
            result["checks"]["macro"]["recession_prob"] = f"{(r.recession_prob or 0)*100:.1f}%"
            result["checks"]["macro"]["fed_hike_prob"]  = f"{(r.fed_hike_prob  or 0)*100:.1f}%"

        if not macro_gate.allow_long:
            result["reasons"].append(f"Macro BLOCKED (score {macro_gate.macro_score:.0f}/100): {macro_gate.reason}")
        elif macro_gate.size_factor < 1.0:
            result["reasons"].append(
                f"Macro caution: size → {macro_gate.size_factor:.0%} ({macro_gate.reason})"
            )
    except Exception as e:
        result["checks"]["macro"] = {"pass": True, "note": str(e)}

    # ── 4. Candle pattern confirmation ────────────────────────────────
    if df is not None:
        try:
            df_pat       = add_candle_patterns(df)
            candle_score = float(df_pat["candle_score"].iloc[-1])
            result["checks"]["candles"] = {
                "pass":  candle_score >= 0,
                "score": round(candle_score, 2),
            }
            if candle_score < 0:
                result["reasons"].append(f"Candle patterns bearish (score {candle_score:.1f})")
        except Exception:
            result["checks"]["candles"] = {"pass": True, "note": "unavailable"}

    # ── 5. WSB per-ticker overcrowding ────────────────────────────────
    try:
        wsb_sig = get_ticker_signal(ticker_base)
        result["checks"]["wsb_ticker"] = {
            "mentions":    wsb_sig.mentions,
            "signal":      wsb_sig.signal,
            "size_factor": wsb_sig.size_factor,
        }
        if wsb_sig.signal == "overcrowded":
            result["reasons"].append(
                f"WSB overcrowded: {ticker_base} has {wsb_sig.mentions} mentions → size ×50%"
            )
    except Exception:
        pass

    # ── Final verdict ─────────────────────────────────────────────────
    macro_pass    = result["checks"].get("macro",    {}).get("pass", True)
    strategy_pass = result["checks"].get("strategy", {}).get("pass", False)
    events_pass   = result["checks"].get("events",   {}).get("pass", True)
    candles_pass  = result["checks"].get("candles",  {}).get("pass", True)

    if not macro_pass:
        result["verdict"] = "AVOID"
    elif not events_pass:
        result["verdict"] = "WAIT"
    elif not strategy_pass:
        result["verdict"] = "WAIT"
    elif not candles_pass:
        result["verdict"] = "WAIT"
    else:
        result["verdict"] = "BUY"

    return result


def _scan_watchlist(symbols: list[str]) -> dict[str, Any]:
    """Scan a list of assets, return compact summary."""
    rows = []
    for sym in symbols:
        try:
            r = _check_asset(sym)
            rows.append({
                "symbol":        r["symbol"],
                "verdict":       r["verdict"],
                "price":         r["price"],
                "strategy_pass": r["checks"].get("strategy", {}).get("pass", False),
                "macro_pass":    r["checks"].get("macro",    {}).get("pass", True),
                "size_factor":   r["checks"].get("macro",    {}).get("size_factor", 1.0),
                "top_reason":    r["reasons"][0] if r["reasons"] else "all filters passed",
            })
        except Exception as e:
            rows.append({"symbol": sym, "verdict": "ERROR", "reason": str(e)})

    buy_count = sum(1 for r in rows if r.get("verdict") == "BUY")
    return {
        "scanned":      len(rows),
        "buy_signals":  buy_count,
        "assets":       rows,
        "summary":      f"{buy_count}/{len(rows)} assets have BUY signal",
    }


def _get_macro_environment() -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        report = get_macro_risk()
        gate   = get_macro_gate()
        out = {
            "macro_risk_score":  round(report.score, 1),
            "risk_label":        report.risk_label(),
            "allow_longs":       gate.allow_long,
            "size_factor":       f"{gate.size_factor:.0%}",
            "gate_reason":       gate.reason or "all clear",
            "polymarket": {
                "recession_prob": f"{(report.recession_prob or 0)*100:.1f}%",
                "fed_cut_prob":   f"{(report.fed_cut_prob   or 0)*100:.1f}%",
                "fed_hike_prob":  f"{(report.fed_hike_prob  or 0)*100:.1f}%",
                "inflation_prob": f"{(report.inflation_prob or 0)*100:.1f}%",
            },
            "wsb_market_mood": {
                "mood":  gate.wsb_mood,
                "score": gate.wsb_score,
            },
        }
        if report.top_markets:
            out["top_polymarket_markets"] = [
                {"question": m.question[:80], "yes_prob": f"{m.yes_prob*100:.1f}%"}
                for m in report.top_markets[:5]
            ]
    except Exception as e:
        out = {"error": str(e), "note": "Polymarket API may be temporarily unavailable"}
    return out


def _get_market_sentiment() -> dict[str, Any]:
    out: dict[str, Any] = {}

    try:
        fng = get_current_fng()
        if fng:
            v = fng["value"]
            out["fear_greed"] = {
                "value":          v,
                "classification": fng["classification"],
                "date":           str(fng["timestamp"].date()),
                "interpretation": (
                    "extreme greed — market may be overextended, caution on longs" if v >= 80 else
                    "greed"                if v >= 60 else
                    "neutral"              if v >= 40 else
                    "fear"                 if v >= 20 else
                    "extreme fear — potential capitulation zone"
                ),
            }
    except Exception as e:
        out["fear_greed"] = {"error": str(e)}

    try:
        fr = get_funding_rate("BTC/USDT:USDT", CONFIG.exchange.name)
        out["btc_funding_rate"] = {
            "rate":   fr,
            "signal": (
                "longs overleveraged — shorts may squeeze soon" if (fr or 0) > 0.0005 else
                "shorts overleveraged — longs may squeeze soon" if (fr or 0) < -0.0005 else
                "neutral"
            ) if fr is not None else "unavailable",
        }
    except Exception:
        out["btc_funding_rate"] = {"rate": None, "signal": "unavailable"}

    try:
        mood = get_market_mood()
        out["wsb_mood"] = {
            "mood":         mood.mood,
            "score":        mood.score,
            "top_tickers":  dict(list(mood.top_tickers.items())[:10]),
        }
    except Exception as e:
        out["wsb_mood"] = {"error": str(e)}

    return out


# ─── Tool dispatcher ──────────────────────────────────────────────────

def _dispatch(name: str, tool_input: dict) -> str:
    handlers = {
        "check_asset":           lambda: _check_asset(**tool_input),
        "scan_watchlist":        lambda: _scan_watchlist(**tool_input),
        "get_macro_environment": lambda: _get_macro_environment(),
        "get_market_sentiment":  lambda: _get_market_sentiment(),
    }
    fn = handlers.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = fn()
    return json.dumps(result, default=str, ensure_ascii=False, indent=2)


# ─── Main advisor loop ────────────────────────────────────────────────

def ask(
    question: str,
    history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    """
    Ask the trading advisor a question.

    Args:
        question: Natural language question (Spanish or English).
        history:  Conversation history for multi-turn sessions.

    Returns:
        (answer_text, updated_history)
    """
    client   = anthropic.Anthropic()
    messages = list(history or [])
    messages.append({"role": "user", "content": question})

    while True:
        response = client.messages.create(
            model      = "claude-sonnet-4-6",
            max_tokens = 2048,
            system     = _SYSTEM,
            tools      = _TOOLS,
            messages   = messages,
        )

        content = response.content

        if response.stop_reason == "end_turn":
            text = next((b.text for b in content if hasattr(b, "text")), "")
            messages.append({"role": "assistant", "content": content})
            return text, messages

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in content:
                if block.type == "tool_use":
                    logger.debug(f"[Advisor] → {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                    result_str = _dispatch(block.name, block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result_str,
                    })
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user",      "content": tool_results})
            continue

        break  # unexpected stop reason

    return "Sin respuesta.", messages
