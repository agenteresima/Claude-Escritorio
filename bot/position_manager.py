"""
Advanced position management:
  - Pyramid entries (scale in on confirmation)
  - Partial profit taking (close 50 % at TP1, let rest run to TP2)
  - Break-even stop (move SL to entry after +1R)
  - Time-based exit (close if trade stale > max_bars)
"""
import time
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger
from bot.notifier import notify_trade_open, notify_trade_close


@dataclass
class OpenPosition:
    symbol:       str
    direction:    str          # "long" | "short"
    entry_price:  float
    size:         float
    stop_loss:    float
    take_profit1: float        # 50 % closes here
    take_profit2: float        # remaining closes here
    entry_time:   float = field(default_factory=time.time)
    partial_taken: bool = False
    breakeven_set: bool = False
    bar_count:    int = 0

    @property
    def unrealised_pnl_pct(self) -> float:
        return 0.0  # filled by live trader with live price


class PositionManager:
    def __init__(self, max_bars: int = 96, dry_run: bool = True):
        self.positions: dict[str, OpenPosition] = {}
        self.max_bars  = max_bars      # ~4 days on 1h candles
        self.dry_run   = dry_run
        self.closed_trades: list[dict] = []

    def open_position(self, symbol: str, direction: str, entry: float,
                      size: float, stop: float, tp1: float, tp2: float):
        if symbol in self.positions:
            return
        self.positions[symbol] = OpenPosition(
            symbol=symbol, direction=direction, entry_price=entry,
            size=size, stop_loss=stop, take_profit1=tp1, take_profit2=tp2,
        )
        notify_trade_open(symbol, direction, entry, stop, tp2, size, self.dry_run)
        logger.info(f"Opened {direction} {symbol} @ {entry:.4f} | size={size:.4f}")

    def update(self, symbol: str, current_price: float) -> list[str]:
        """
        Check position management rules.
        Returns list of actions taken: 'partial_close', 'breakeven', 'full_close', 'time_exit'.
        """
        if symbol not in self.positions:
            return []

        pos     = self.positions[symbol]
        actions = []
        pos.bar_count += 1
        price   = current_price

        # -- Time-based exit --
        if pos.bar_count >= self.max_bars:
            self._close(symbol, price, "time_exit")
            return ["time_exit"]

        if pos.direction == "long":
            # -- Stop loss --
            if price <= pos.stop_loss:
                self._close(symbol, price, "stop_loss")
                return ["stop_loss"]

            # -- Break-even: move SL to entry after price hits +1R --
            one_r = pos.entry_price + (pos.take_profit1 - pos.entry_price) * 0.5
            if not pos.breakeven_set and price >= one_r:
                pos.stop_loss    = pos.entry_price * 1.001   # tiny buffer above entry
                pos.breakeven_set = True
                actions.append("breakeven")
                logger.info(f"{symbol} break-even stop set @ {pos.stop_loss:.4f}")

            # -- Partial take-profit 1 (50 % of size) --
            if not pos.partial_taken and price >= pos.take_profit1:
                partial_size      = pos.size * 0.50
                pos.size         -= partial_size
                pos.partial_taken = True
                pnl_pct           = (price - pos.entry_price) / pos.entry_price
                notify_trade_close(symbol, pos.entry_price, price,
                                   (price - pos.entry_price) * partial_size,
                                   pnl_pct, "partial_tp1")
                actions.append("partial_close")
                logger.info(f"{symbol} partial TP1 @ {price:.4f} | remaining size={pos.size:.4f}")

            # -- Full take-profit 2 --
            if pos.partial_taken and price >= pos.take_profit2:
                self._close(symbol, price, "take_profit2")
                return actions + ["full_close"]

        else:  # short
            if price >= pos.stop_loss:
                self._close(symbol, price, "stop_loss")
                return ["stop_loss"]

            one_r = pos.entry_price - (pos.entry_price - pos.take_profit1) * 0.5
            if not pos.breakeven_set and price <= one_r:
                pos.stop_loss     = pos.entry_price * 0.999
                pos.breakeven_set = True
                actions.append("breakeven")

            if not pos.partial_taken and price <= pos.take_profit1:
                partial_size      = pos.size * 0.50
                pos.size         -= partial_size
                pos.partial_taken = True
                actions.append("partial_close")

            if pos.partial_taken and price <= pos.take_profit2:
                self._close(symbol, price, "take_profit2")
                return actions + ["full_close"]

        return actions

    def _close(self, symbol: str, price: float, reason: str):
        pos = self.positions.pop(symbol, None)
        if pos is None:
            return
        if pos.direction == "long":
            pnl     = (price - pos.entry_price) * pos.size
            pnl_pct = (price - pos.entry_price) / pos.entry_price
        else:
            pnl     = (pos.entry_price - price) * pos.size
            pnl_pct = (pos.entry_price - price) / pos.entry_price

        notify_trade_close(symbol, pos.entry_price, price, pnl, pnl_pct, reason)
        self.closed_trades.append({
            "symbol": symbol, "entry": pos.entry_price, "exit": price,
            "pnl": pnl, "pnl_pct": pnl_pct, "reason": reason,
            "bars": pos.bar_count,
        })
        logger.info(f"Closed {symbol} @ {price:.4f} | pnl={pnl:+.2f} ({reason})")
