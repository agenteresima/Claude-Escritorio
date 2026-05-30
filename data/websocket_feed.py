"""
Real-time WebSocket data feed via CCXT Pro (or fallback to ccxt REST polling).
Pushes candles into an asyncio queue consumed by the live trader.

Usage:
    feed = WebSocketFeed(["BTC/USDT", "ETH/USDT"], timeframe="1m")
    async for candle in feed.stream():
        process(candle)
"""
import asyncio
import time
from datetime import datetime, timezone
from typing import AsyncIterator
import pandas as pd
from loguru import logger


class Candle:
    __slots__ = ("symbol", "timestamp", "open", "high", "low", "close", "volume", "closed")

    def __init__(self, symbol: str, ohlcv: list, closed: bool = False):
        self.symbol    = symbol
        self.timestamp = datetime.fromtimestamp(ohlcv[0] / 1000, tz=timezone.utc)
        self.open      = ohlcv[1]
        self.high      = ohlcv[2]
        self.low       = ohlcv[3]
        self.close     = ohlcv[4]
        self.volume    = ohlcv[5]
        self.closed    = closed

    def to_series(self) -> dict:
        return {
            "open": self.open, "high": self.high,
            "low":  self.low,  "close": self.close, "volume": self.volume,
        }

    def __repr__(self):
        return (f"Candle({self.symbol} {self.timestamp} "
                f"O={self.open:.2f} H={self.high:.2f} L={self.low:.2f} C={self.close:.2f})")


class WebSocketFeed:
    """
    Streams OHLCV candles using ccxtpro if available,
    falls back to REST polling otherwise.
    """

    def __init__(self, symbols: list[str], timeframe: str = "1m",
                 exchange_name: str = "binance"):
        self.symbols       = symbols
        self.timeframe     = timeframe
        self.exchange_name = exchange_name
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._running      = False
        self._candle_buffers: dict[str, list] = {s: [] for s in symbols}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def stream(self) -> AsyncIterator[Candle]:
        """Async generator — yields closed candles in real time."""
        self._running = True
        producer = asyncio.create_task(self._produce())
        try:
            while self._running:
                candle = await asyncio.wait_for(self._queue.get(), timeout=60)
                yield candle
        finally:
            producer.cancel()
            self._running = False

    def stop(self):
        self._running = False

    # ------------------------------------------------------------------
    # Internal producers
    # ------------------------------------------------------------------

    async def _produce(self):
        try:
            import ccxtpro as ccxtpro_mod
            exchange = getattr(ccxtpro_mod, self.exchange_name)()
            logger.info(f"WebSocket feed (ccxtpro): {self.symbols}")
            await self._ws_loop(exchange)
        except (ImportError, ModuleNotFoundError):
            logger.info("ccxtpro not installed — using REST polling fallback (1 min latency)")
            await self._rest_poll_loop()

    async def _ws_loop(self, exchange):
        """ccxtpro watch_ohlcv loop."""
        tasks = [
            asyncio.create_task(self._watch_symbol(exchange, sym))
            for sym in self.symbols
        ]
        await asyncio.gather(*tasks)
        await exchange.close()

    async def _watch_symbol(self, exchange, symbol: str):
        prev_ts = None
        while self._running:
            try:
                ohlcvs = await exchange.watch_ohlcv(symbol, self.timeframe)
                for ohlcv in ohlcvs:
                    ts = ohlcv[0]
                    if ts != prev_ts and prev_ts is not None:
                        # Previous candle is now closed
                        candle = Candle(symbol, ohlcv, closed=True)
                        await self._queue.put(candle)
                        logger.debug(f"New closed candle: {candle}")
                    prev_ts = ts
            except Exception as e:
                logger.warning(f"WS error {symbol}: {e} — retrying in 5s")
                await asyncio.sleep(5)

    async def _rest_poll_loop(self):
        """Fallback: poll REST API every N seconds aligned to candle close."""
        import ccxt.async_support as ccxt_async

        exchange_cls = getattr(ccxt_async, self.exchange_name)
        exchange     = exchange_cls({"enableRateLimit": True})

        tf_seconds = {
            "1m": 60, "5m": 300, "15m": 900,
            "1h": 3600, "4h": 14400, "1d": 86400,
        }
        period = tf_seconds.get(self.timeframe, 60)

        prev_ts: dict[str, int] = {}

        try:
            while self._running:
                # Sleep until next candle close
                now    = int(time.time())
                sleep  = period - (now % period) + 2
                await asyncio.sleep(sleep)

                for symbol in self.symbols:
                    try:
                        ohlcvs = await exchange.fetch_ohlcv(symbol, self.timeframe, limit=2)
                        if len(ohlcvs) >= 2:
                            # Second-to-last is the just-closed candle
                            closed_ohlcv = ohlcvs[-2]
                            ts           = closed_ohlcv[0]
                            if prev_ts.get(symbol) != ts:
                                candle = Candle(symbol, closed_ohlcv, closed=True)
                                await self._queue.put(candle)
                                prev_ts[symbol] = ts
                                logger.debug(f"Polled candle: {candle}")
                    except Exception as e:
                        logger.warning(f"Poll error {symbol}: {e}")
        finally:
            await exchange.close()


# ------------------------------------------------------------------
# Candle buffer → DataFrame (used by strategy.run())
# ------------------------------------------------------------------

class CandleBuffer:
    """Rolling buffer of the last N candles per symbol as a DataFrame."""

    def __init__(self, maxlen: int = 500):
        self.maxlen  = maxlen
        self._data: dict[str, list[dict]] = {}

    def push(self, candle: Candle):
        sym = candle.symbol
        if sym not in self._data:
            self._data[sym] = []
        self._data[sym].append({
            "timestamp": candle.timestamp,
            **candle.to_series(),
        })
        if len(self._data[sym]) > self.maxlen:
            self._data[sym].pop(0)

    def to_df(self, symbol: str) -> pd.DataFrame:
        rows = self._data.get(symbol, [])
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows).set_index("timestamp")
        df.index = pd.to_datetime(df.index, utc=True)
        return df

    def to_dataframe(self) -> pd.DataFrame:
        """Return all buffered candles (all symbols) as a single DataFrame."""
        all_rows: list[dict] = []
        for rows in self._data.values():
            all_rows.extend(rows)
        if not all_rows:
            return pd.DataFrame()
        df = pd.DataFrame(all_rows).set_index("timestamp")
        df.index = pd.to_datetime(df.index, utc=True)
        return df.sort_index()

    def is_ready(self, symbol: str, min_bars: int = 200) -> bool:
        return len(self._data.get(symbol, [])) >= min_bars
