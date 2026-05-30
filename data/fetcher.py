"""
Data fetcher — supports CCXT (crypto) and yfinance (stocks/forex).
Caches OHLCV locally as Parquet files to avoid repeated API calls.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import ccxt
import pandas as pd
import yfinance as yf
from loguru import logger

from config import CONFIG

MAX_RETRIES = 4
_BACKOFF_BASE = 2.0   # seconds; retry waits 2, 4, 8, 16 s


def _retry_sleep(attempt: int) -> None:
    wait = _BACKOFF_BASE ** attempt
    logger.debug(f"Retry {attempt} — waiting {wait:.0f}s")
    time.sleep(wait)


CACHE_DIR = CONFIG.data_dir / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(symbol: str, timeframe: str, source: str) -> Path:
    safe = symbol.replace("/", "_")
    return CACHE_DIR / f"{source}_{safe}_{timeframe}.parquet"


def fetch_ohlcv_ccxt(
    symbol: str,
    timeframe: str = "1h",
    start: str = "2020-01-01",
    end: Optional[str] = None,
    exchange_name: str = "binance",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch OHLCV from a CCXT exchange with local cache."""
    cache = _cache_path(symbol, timeframe, exchange_name)
    if use_cache and cache.exists():
        df = pd.read_parquet(cache)
        logger.info(f"Cache hit: {symbol} {timeframe} ({len(df)} candles)")
        return df

    exchange_cls = getattr(ccxt, exchange_name)
    exchange = exchange_cls({"enableRateLimit": True})

    since_ms = int(datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000)
    until_ms = int(datetime.strptime(end, "%Y-%m-%d").timestamp() * 1000) if end else None

    all_ohlcv: list = []
    while True:
        for attempt in range(MAX_RETRIES):
            try:
                batch = exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=1000)
                break
            except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                logger.warning(f"Network error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                _retry_sleep(attempt)
            except ccxt.RateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded, backing off: {e}")
                _retry_sleep(attempt + 1)
        else:
            break

        if not batch:
            break
        all_ohlcv.extend(batch)
        since_ms = batch[-1][0] + 1
        if until_ms and since_ms >= until_ms:
            break
        if len(batch) < 1000:
            break
        time.sleep(exchange.rateLimit / 1000)

    df = pd.DataFrame(all_ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df[~df.index.duplicated()].sort_index()

    if use_cache:
        df.to_parquet(cache)
    logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
    return df


def fetch_ohlcv_yfinance(
    ticker: str,
    interval: str = "1h",
    start: str = "2020-01-01",
    end: Optional[str] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch OHLCV from Yahoo Finance (stocks, ETFs, indices)."""
    cache = _cache_path(ticker, interval, "yfinance")
    if use_cache and cache.exists():
        df = pd.read_parquet(cache)
        logger.info(f"Cache hit: {ticker} {interval} ({len(df)} candles)")
        return df

    for attempt in range(MAX_RETRIES):
        try:
            df = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
            break
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            logger.warning(f"yfinance error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            _retry_sleep(attempt)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    df.index = pd.to_datetime(df.index, utc=True)
    rename_map = {c: "close" for c in df.columns if "adj" in c.lower() and "close" in c.lower()}
    if rename_map:
        df = df.rename(columns=rename_map)
    needed = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df = df[needed]
    df.dropna(inplace=True)

    if use_cache:
        df.to_parquet(cache)
    logger.info(f"Fetched {len(df)} rows for {ticker} {interval}")
    return df


def fetch_multiple_pairs(
    pairs: list[str],
    timeframe: str = "1h",
    start: str = "2020-01-01",
    source: str = "ccxt",
) -> dict[str, pd.DataFrame]:
    """Fetch multiple pairs in a batch."""
    result = {}
    for pair in pairs:
        try:
            if source == "ccxt":
                result[pair] = fetch_ohlcv_ccxt(pair, timeframe, start)
            else:
                result[pair] = fetch_ohlcv_yfinance(pair, timeframe, start)
        except Exception as e:
            logger.error(f"Failed to fetch {pair}: {e}")
    return result
