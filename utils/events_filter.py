"""
Macro events filter — avoid trading around high-impact news events.
Sources:
  - ForexFactory JSON (free, no API key)
  - Hard-coded recurring schedule (FOMC, NFP, CPI)

Usage:
  gate = EventsFilter()
  if gate.is_safe_to_trade():
      execute_trade()
"""
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
import requests
from loguru import logger


# High-impact events that always move crypto significantly
RECURRING_EVENTS = [
    # Every first Friday: Non-Farm Payrolls (13:30 UTC)
    {"name": "NFP",    "day_of_month_range": (1, 7),  "weekday": 4, "hour": 13, "blackout_h": 4},
    # FOMC meetings: 8× per year — approx every 6 weeks Wed 18:00 UTC
    # (handled dynamically via ForexFactory)
    # US CPI: second or third Tuesday/Wednesday of month
    {"name": "US CPI", "day_of_month_range": (8, 15), "weekday": 2, "hour": 12, "blackout_h": 3},
]


class EventsFilter:
    def __init__(self, blackout_before_h: float = 1.0, blackout_after_h: float = 2.0):
        self.blackout_before = timedelta(hours=blackout_before_h)
        self.blackout_after  = timedelta(hours=blackout_after_h)
        self._cache: list[dict] = []
        self._cache_ts: float   = 0.0
        self._cache_ttl: float  = 3600.0   # refresh hourly

    # ------------------------------------------------------------------

    def is_safe_to_trade(self, now: Optional[datetime] = None) -> tuple[bool, str]:
        """
        Returns (True, "ok") if safe, or (False, reason) if near a high-impact event.
        """
        now = now or datetime.now(timezone.utc)

        # Check recurring hard-coded schedule
        for ev in RECURRING_EVENTS:
            ev_time = self._next_occurrence(ev, now)
            if ev_time is None:
                continue
            delta = ev_time - now
            if -self.blackout_after <= delta <= self.blackout_before:
                return False, f"Near {ev['name']} (event at {ev_time.strftime('%H:%M UTC')})"

        # Check ForexFactory feed
        events = self._fetch_forex_factory()
        for ev in events:
            ev_time = ev.get("datetime")
            if ev_time is None:
                continue
            delta = ev_time - now
            if -self.blackout_after <= delta <= self.blackout_before:
                return False, f"Near {ev.get('title', 'macro event')} ({ev_time.strftime('%H:%M UTC')})"

        return True, "ok"

    # ------------------------------------------------------------------

    def _next_occurrence(self, ev: dict, now: datetime) -> Optional[datetime]:
        """Check if today matches the recurring event pattern."""
        dom_lo, dom_hi = ev["day_of_month_range"]
        if not (dom_lo <= now.day <= dom_hi):
            return None
        if now.weekday() != ev["weekday"]:
            return None
        ev_time = now.replace(hour=ev["hour"], minute=30, second=0, microsecond=0)
        return ev_time

    def _fetch_forex_factory(self) -> list[dict]:
        """Fetch high-impact events from ForexFactory (cached 1h)."""
        if time.time() - self._cache_ts < self._cache_ttl:
            return self._cache

        try:
            resp = requests.get(
                "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
                timeout=5,
                headers={"User-Agent": "TradingBot/1.0"},
            )
            resp.raise_for_status()
            raw = resp.json()
            events = []
            for item in raw:
                if item.get("impact") != "High":
                    continue
                date_str = item.get("date", "") + " " + item.get("time", "00:00am")
                try:
                    dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %I:%M%p")
                    dt = dt.replace(tzinfo=timezone.utc)
                    events.append({"title": item.get("title", ""), "datetime": dt})
                except Exception:
                    pass
            self._cache    = events
            self._cache_ts = time.time()
            logger.debug(f"Loaded {len(events)} high-impact events from ForexFactory")
        except Exception as e:
            logger.debug(f"ForexFactory fetch failed (non-critical): {e}")

        return self._cache

    def upcoming_events(self, hours_ahead: int = 24) -> list[dict]:
        now    = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours_ahead)
        events = self._fetch_forex_factory()
        return [e for e in events if now <= e.get("datetime", now) <= cutoff]
