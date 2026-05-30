"""
Order book analysis — detects institutional order flow imbalances.
Used as a real-time entry confirmation filter.

Key signals:
  - Bid/Ask imbalance (>70% bids = buying pressure)
  - Large wall detection (order > 5× average size)
  - Spread as % of price (liquidity indicator)
  - Depth ratio: sum of top-N bids vs asks

Professional application: only enter longs when OB is bid-heavy.
Avoid entries when a large ask wall sits directly above price.
"""
import asyncio
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class OrderBookSnapshot:
    symbol:         str
    bids:           list[list[float]]   # [[price, size], ...]
    asks:           list[list[float]]
    bid_ask_spread: float
    spread_pct:     float
    bid_depth:      float               # total bid volume (top N)
    ask_depth:      float
    imbalance:      float               # (bid_depth - ask_depth) / (bid_depth + ask_depth)
    best_bid:       float
    best_ask:       float
    mid_price:      float
    large_bid_wall: Optional[float]     # price of significant bid wall, if any
    large_ask_wall: Optional[float]

    @property
    def is_bid_heavy(self) -> bool:
        return self.imbalance > 0.20   # > 60% bids

    @property
    def is_ask_heavy(self) -> bool:
        return self.imbalance < -0.20

    @property
    def is_liquid(self) -> bool:
        return self.spread_pct < 0.001   # spread < 0.1%

    @property
    def has_resistance_wall(self) -> bool:
        return self.large_ask_wall is not None

    @property
    def has_support_wall(self) -> bool:
        return self.large_bid_wall is not None


async def fetch_orderbook(
    symbol: str,
    exchange_name: str = "binance",
    depth: int = 20,
) -> Optional[OrderBookSnapshot]:
    """Async fetch of order book snapshot via CCXT."""
    try:
        import ccxt.async_support as ccxt_async
        exchange = getattr(ccxt_async, exchange_name)({"enableRateLimit": True})
        try:
            ob = await exchange.fetch_order_book(symbol, limit=depth)
        finally:
            await exchange.close()

        bids = ob["bids"][:depth]
        asks = ob["asks"][:depth]

        if not bids or not asks:
            return None

        best_bid = bids[0][0]
        best_ask = asks[0][0]
        spread   = best_ask - best_bid
        mid      = (best_bid + best_ask) / 2

        bid_depth = sum(b[1] * b[0] for b in bids)   # in quote currency
        ask_depth = sum(a[1] * a[0] for a in asks)
        total     = bid_depth + ask_depth + 1e-9
        imbalance = (bid_depth - ask_depth) / total

        # Detect walls: orders > 5× median order size
        bid_sizes = [b[1] for b in bids]
        ask_sizes = [a[1] for a in asks]
        med_bid   = sorted(bid_sizes)[len(bid_sizes)//2] if bid_sizes else 1
        med_ask   = sorted(ask_sizes)[len(ask_sizes)//2] if ask_sizes else 1

        large_bid_wall = next((b[0] for b in bids if b[1] > med_bid * 5), None)
        large_ask_wall = next((a[0] for a in asks if a[1] > med_ask * 5), None)

        return OrderBookSnapshot(
            symbol         = symbol,
            bids           = bids,
            asks           = asks,
            bid_ask_spread = spread,
            spread_pct     = spread / mid,
            bid_depth      = bid_depth,
            ask_depth      = ask_depth,
            imbalance      = imbalance,
            best_bid       = best_bid,
            best_ask       = best_ask,
            mid_price      = mid,
            large_bid_wall = large_bid_wall,
            large_ask_wall = large_ask_wall,
        )
    except Exception as e:
        logger.debug(f"Order book fetch failed for {symbol}: {e}")
        return None


def orderbook_filter(ob: Optional[OrderBookSnapshot],
                     direction: str = "long") -> tuple[bool, str]:
    """
    Gate: should we enter based on order book conditions?
    Returns (allow: bool, reason: str)
    """
    if ob is None:
        return True, "no_data"   # don't block if OB unavailable

    if not ob.is_liquid:
        return False, f"Illiquid market (spread {ob.spread_pct*100:.3f}%)"

    if direction == "long":
        if ob.is_ask_heavy:
            return False, f"Ask-heavy OB (imbalance={ob.imbalance:.2f})"
        if ob.has_resistance_wall:
            return False, f"Large ask wall at {ob.large_ask_wall:.4f}"
        if ob.is_bid_heavy:
            return True, f"Bid-heavy OB (imbalance={ob.imbalance:.2f}) — confirmed"
    else:
        if ob.is_bid_heavy:
            return False, f"Bid-heavy OB (imbalance={ob.imbalance:.2f})"
        if ob.has_support_wall:
            return False, f"Large bid wall at {ob.large_bid_wall:.4f}"

    return True, "ok"
