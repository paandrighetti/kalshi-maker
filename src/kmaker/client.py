"""Minimal client for Kalshi's public market data (no authentication).

Requests are paced at a fixed minimum interval. Kalshi's basic tier allows about 20 reads per
second per client; the default here is lower because other processes on the same host poll the
same API. 429, 5xx and transport errors are retried with exponential backoff; a transport error
also rotates to the next base URL, since Kalshi serves the same API under two hosts.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterator, Sequence
from typing import Any

import httpx

log = logging.getLogger(__name__)


class KalshiError(RuntimeError):
    pass


class Kalshi:
    def __init__(
        self,
        bases: Sequence[str],
        rate: float = 8.0,
        timeout: float = 30.0,
        max_tries: int = 8,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not bases:
            raise ValueError("at least one base URL is required")
        self._bases = [b.rstrip("/") for b in bases]
        self._min_interval = 1.0 / rate if rate > 0 else 0.0
        self._next = 0.0
        self._max_tries = max_tries
        self._sleep = sleep
        self._http = httpx.Client(
            timeout=timeout, transport=transport, headers={"Accept": "application/json"}
        )
        self.requests = 0

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Kalshi:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _pace(self) -> None:
        if not self._min_interval:
            return
        now = time.monotonic()
        if now < self._next:
            self._sleep(self._next - now)
            now = self._next
        self._next = now + self._min_interval

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        delay = 0.5
        last: Exception | None = None
        for _ in range(self._max_tries):
            self._pace()
            base = self._bases[0]
            try:
                r = self._http.get(base + path, params=params)
                self.requests += 1
            except httpx.TransportError as exc:
                last = exc
                self._bases.append(self._bases.pop(0))
                log.warning("transport error on %s%s: %s", base, path, exc)
            else:
                if r.status_code == 200:
                    return r.json()
                if r.status_code == 429 or r.status_code >= 500:
                    last = KalshiError(f"HTTP {r.status_code} on {path}")
                else:
                    raise KalshiError(f"HTTP {r.status_code} on {path}: {r.text[:300]}")
            self._sleep(delay)
            delay = min(delay * 2.0, 30.0)
        raise KalshiError(f"giving up on {path} after {self._max_tries} tries: {last}")

    def paginate(
        self, path: str, params: dict[str, Any] | None, key: str, max_pages: int | None = None
    ) -> Iterator[dict[str, Any]]:
        query = dict(params or {})
        pages = 0
        while True:
            data = self.get(path, query)
            yield from data.get(key) or []
            pages += 1
            cursor = data.get("cursor")
            if not cursor or (max_pages is not None and pages >= max_pages):
                return
            query["cursor"] = cursor

    def pages(
        self, path: str, params: dict[str, Any] | None, key: str
    ) -> Iterator[list[dict[str, Any]]]:
        """Like `paginate`, one list per page, so a caller can spread a listing over time."""
        query = dict(params or {})
        while True:
            data = self.get(path, query)
            yield data.get(key) or []
            cursor = data.get("cursor")
            if not cursor:
                return
            query["cursor"] = cursor

    # endpoints -----------------------------------------------------------------------------

    def cutoff(self) -> dict[str, Any]:
        return self.get("/historical/cutoff")

    def series(self) -> list[dict[str, Any]]:
        return list(self.paginate("/series", {}, "series"))

    def series_one(self, ticker: str) -> dict[str, Any] | None:
        try:
            return self.get(f"/series/{ticker}").get("series")
        except KalshiError:
            return None

    def trades(self, min_ts: int, max_ts: int, historical: bool) -> Iterator[dict[str, Any]]:
        path = "/historical/trades" if historical else "/markets/trades"
        return self.paginate(path, {"min_ts": min_ts, "max_ts": max_ts, "limit": 1000}, "trades")

    def recent_trades(self, min_ts: int) -> Iterator[dict[str, Any]]:
        return self.paginate("/markets/trades", {"min_ts": min_ts, "limit": 1000}, "trades")

    def markets_by_tickers(self, tickers: Sequence[str], historical: bool) -> list[dict[str, Any]]:
        if not tickers:
            return []
        path = "/historical/markets" if historical else "/markets"
        return list(self.paginate(path, {"tickers": ",".join(tickers), "limit": 1000}, "markets"))

    def open_market_pages(self) -> Iterator[list[dict[str, Any]]]:
        return self.pages(
            "/markets", {"status": "open", "mve_filter": "exclude", "limit": 1000}, "markets"
        )

    def updated_markets(self, min_updated_ts: int) -> Iterator[dict[str, Any]]:
        return self.paginate(
            "/markets",
            {"mve_filter": "exclude", "min_updated_ts": min_updated_ts, "limit": 1000},
            "markets",
        )
