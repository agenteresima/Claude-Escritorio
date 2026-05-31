import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf
from loguru import logger

from config import CONFIG

SP500_TICKERS: list[str] = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "UNH", "XOM", "PG", "MA", "HD", "LLY", "CVX",
    "MRK", "ABBV", "KO", "PEP", "AVGO", "COST", "TMO", "WMT", "ABT",
    "MCD", "ACN", "BAC", "CSCO", "DHR", "NEE", "DIS", "BMY", "INTC",
    "CRM", "VZ", "CMCSA", "ADBE", "NFLX", "WFC", "T", "AMD", "QCOM",
    "AMGN", "LIN", "PM", "RTX", "GE",
]

SECTOR_MAP: dict[str, str] = {
    "AAPL":  "Technology",
    "MSFT":  "Technology",
    "NVDA":  "Technology",
    "AMZN":  "Consumer Discretionary",
    "GOOGL": "Communication Services",
    "META":  "Communication Services",
    "TSLA":  "Consumer Discretionary",
    "BRK-B": "Financials",
    "JPM":   "Financials",
    "JNJ":   "Healthcare",
    "V":     "Financials",
    "UNH":   "Healthcare",
    "XOM":   "Energy",
    "PG":    "Consumer Staples",
    "MA":    "Financials",
    "HD":    "Consumer Discretionary",
    "LLY":   "Healthcare",
    "CVX":   "Energy",
    "MRK":   "Healthcare",
    "ABBV":  "Healthcare",
    "KO":    "Consumer Staples",
    "PEP":   "Consumer Staples",
    "AVGO":  "Technology",
    "COST":  "Consumer Staples",
    "TMO":   "Healthcare",
    "WMT":   "Consumer Staples",
    "ABT":   "Healthcare",
    "MCD":   "Consumer Discretionary",
    "ACN":   "Technology",
    "BAC":   "Financials",
    "CSCO":  "Technology",
    "DHR":   "Healthcare",
    "NEE":   "Utilities",
    "DIS":   "Communication Services",
    "BMY":   "Healthcare",
    "INTC":  "Technology",
    "CRM":   "Technology",
    "VZ":    "Communication Services",
    "CMCSA": "Communication Services",
    "ADBE":  "Technology",
    "NFLX":  "Communication Services",
    "WFC":   "Financials",
    "T":     "Communication Services",
    "AMD":   "Technology",
    "QCOM":  "Technology",
    "AMGN":  "Healthcare",
    "LIN":   "Materials",
    "PM":    "Consumer Staples",
    "RTX":   "Industrials",
    "GE":    "Industrials",
}

_DEFAULT_CACHE_DIR = CONFIG.data_dir / "cache" / "sp500"
_CACHE_MAX_AGE_S = 86_400  # 24 hours


def _is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    return age < _CACHE_MAX_AGE_S


def _normalise_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    needed = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df = df[needed].copy()
    df.dropna(how="all", inplace=True)
    return df


def download_universe(
    tickers: list[str] | None = None,
    start: str = "2015-01-01",
    end: str = "2024-12-31",
    cache_dir: Path | str | None = None,
) -> dict[str, pd.DataFrame]:
    tickers = tickers or SP500_TICKERS
    cache_root = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    cache_root.mkdir(parents=True, exist_ok=True)

    universe: dict[str, pd.DataFrame] = {}
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        safe = ticker.replace("-", "_")
        cache_path = cache_root / f"{safe}_{start}_{end}.parquet"

        if _is_fresh(cache_path):
            try:
                df = pd.read_parquet(cache_path)
                logger.debug(f"[{i}/{total}] Cache hit: {ticker} ({len(df)} rows)")
                universe[ticker] = df
                continue
            except Exception as e:
                logger.warning(f"Cache read failed for {ticker}: {e} — re-downloading")

        try:
            raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            df = _normalise_df(raw)
            if df.empty:
                logger.warning(f"[{i}/{total}] {ticker}: empty data returned — skipping")
                continue
            df.to_parquet(cache_path)
            universe[ticker] = df
            logger.info(f"[{i}/{total}] Downloaded {ticker}: {len(df)} rows")
        except Exception as e:
            logger.warning(f"[{i}/{total}] Failed to download {ticker}: {e} — skipping")

        time.sleep(0.1)

    logger.info(f"Universe ready: {len(universe)}/{total} tickers loaded")
    return universe


def get_spy_benchmark(start: str = "2015-01-01", end: str = "2024-12-31") -> pd.Series:
    try:
        raw = yf.download("SPY", start=start, end=end, progress=False, auto_adjust=True)
        df = _normalise_df(raw)
        if "close" not in df.columns or df.empty:
            logger.error("SPY download returned no close prices")
            return pd.Series(dtype=float)
        series = df["close"].dropna()
        series.name = "SPY"
        logger.info(f"SPY benchmark loaded: {len(series)} days")
        return series
    except Exception as e:
        logger.error(f"Failed to download SPY benchmark: {e}")
        return pd.Series(dtype=float)


def compute_returns_matrix(universe: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not universe:
        return pd.DataFrame()

    close_dict: dict[str, pd.Series] = {}
    for ticker, df in universe.items():
        if df.empty or "close" not in df.columns:
            continue
        close_dict[ticker] = df["close"].dropna()

    if not close_dict:
        return pd.DataFrame()

    prices = pd.DataFrame(close_dict)
    returns = prices.pct_change().dropna(how="all")
    return returns
