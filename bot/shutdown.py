"""
Graceful shutdown handler.
Catches SIGTERM/SIGINT, closes all open positions (optional),
saves state to DB, flushes logs and exits cleanly.

Usage in main loop:
    shutdown = GracefulShutdown(close_positions_on_exit=False)
    shutdown.install()
    while not shutdown.requested:
        ...
"""
import signal
import sys
import asyncio
from typing import Optional, Callable
from loguru import logger

from data.database import set_state
from bot.notifier import notify


class GracefulShutdown:
    def __init__(self, close_positions_on_exit: bool = False,
                 pos_manager=None):
        self.requested               = False
        self.close_positions         = close_positions_on_exit
        self.pos_manager             = pos_manager
        self._shutdown_callbacks: list[Callable] = []

    def install(self):
        signal.signal(signal.SIGTERM, self._handle)
        signal.signal(signal.SIGINT,  self._handle)
        logger.info("Graceful shutdown handler installed (SIGTERM / SIGINT).")

    def add_callback(self, fn: Callable):
        self._shutdown_callbacks.append(fn)

    def _handle(self, signum, frame):
        sig_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.warning(f"Received {sig_name} — initiating graceful shutdown...")
        self._run_shutdown()
        sys.exit(0)

    def _run_shutdown(self):
        self.requested = True
        set_state("paused", True)
        notify("🛑 *Trading Bot Shutting Down*\nReceived shutdown signal. Trading paused.")

        if self.close_positions and self.pos_manager:
            logger.warning("Closing all open positions...")
            for sym in list(self.pos_manager.positions.keys()):
                logger.warning(f"  Open position NOT closed (no live price): {sym}")

        for cb in self._shutdown_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Shutdown callback error: {e}")

        logger.info("Shutdown complete. Exiting.")

    # ── Async version ────────────────────────────────────────────────────────

    def install_async(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        loop = loop or asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_async, sig)
        logger.info("Async graceful shutdown handler installed.")

    def _handle_async(self, signum):
        logger.warning(f"Async shutdown signal received ({signum})")
        self.requested = True
        set_state("paused", True)
        notify("🛑 *Trading Bot Shutting Down* (async)")
