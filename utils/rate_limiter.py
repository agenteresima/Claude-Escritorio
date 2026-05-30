"""
Token-bucket rate limiter for exchange API calls.
Prevents hitting exchange rate limits (→ IP bans).

Each exchange has different limits:
  Binance  : 1200 weight/min, 10 orders/sec
  Bybit    : 120 req/min per endpoint
  Kraken   : 15 req/min (rolling)

Usage:
    limiter = RateLimiter(calls_per_second=2.0)
    async with limiter:
        data = await exchange.fetch_ohlcv(...)
"""
import asyncio
import time
import threading
from loguru import logger


class RateLimiter:
    """Token bucket rate limiter — thread-safe and async-compatible."""

    def __init__(self, calls_per_second: float = 2.0, burst: int = 5):
        self.rate     = calls_per_second
        self.burst    = burst
        self._tokens  = float(burst)
        self._last_ts = time.monotonic()
        self._lock    = threading.Lock()
        self._alock   = None   # asyncio lock, created on demand

    def _refill(self):
        now    = time.monotonic()
        delta  = now - self._last_ts
        self._tokens = min(self.burst, self._tokens + delta * self.rate)
        self._last_ts = now

    # ── Sync context manager ─────────────────────────────────────────────────

    def __enter__(self):
        with self._lock:
            self._refill()
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.rate
                logger.debug(f"Rate limit: sleeping {wait:.2f}s")
                time.sleep(wait)
                self._refill()
            self._tokens -= 1.0
        return self

    def __exit__(self, *_):
        pass

    # ── Async context manager ────────────────────────────────────────────────

    async def __aenter__(self):
        if self._alock is None:
            self._alock = asyncio.Lock()
        async with self._alock:
            self._refill()
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.rate
                logger.debug(f"Rate limit: sleeping {wait:.2f}s")
                await asyncio.sleep(wait)
                self._refill()
            self._tokens -= 1.0
        return self

    async def __aexit__(self, *_):
        pass


class ExchangeRateLimiter:
    """
    Per-endpoint rate limiter for exchange APIs.
    """
    PRESETS = {
        "binance":  {"calls_per_second": 10.0, "burst": 20},
        "bybit":    {"calls_per_second":  2.0,  "burst": 10},
        "kraken":   {"calls_per_second":  0.25, "burst":  5},
        "coinbase": {"calls_per_second":  3.0,  "burst": 10},
        "default":  {"calls_per_second":  2.0,  "burst":  5},
    }

    def __init__(self, exchange_name: str = "binance"):
        preset = self.PRESETS.get(exchange_name.lower(), self.PRESETS["default"])
        self.general   = RateLimiter(**preset)
        self.order     = RateLimiter(calls_per_second=5.0, burst=10)    # stricter for orders
        self.market_data = RateLimiter(calls_per_second=20.0, burst=40) # loose for data


# Global limiters
_limiters: dict[str, ExchangeRateLimiter] = {}

def get_limiter(exchange: str = "binance") -> ExchangeRateLimiter:
    if exchange not in _limiters:
        _limiters[exchange] = ExchangeRateLimiter(exchange)
    return _limiters[exchange]
