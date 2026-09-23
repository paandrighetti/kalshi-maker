"""Normalization of Kalshi API objects into flat rows, shared by the backtest and the paper maker.

Kalshi moved to fixed-point string fields in 2026 (`count_fp`, `yes_price_dollars`) and to the
pair `taker_outcome_side` / `taker_book_side` for trade direction. `taker_outcome_side` is the
outcome whose exposure the taker gained: buying YES and selling NO both report `yes` (Kalshi API
documentation, "Order direction"). The older integer fields are read when the new ones are
absent.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .config import PREREG

TRADE_COLUMNS = ["ticker", "trade_id", "count", "yes_price", "taker_yes", "created_us", "is_block"]

MARKET_COLUMNS = [
    "ticker",
    "event_ticker",
    "series",
    "status",
    "result",
    "close_us",
    "expected_expiration_us",
    "latest_expiration_us",
    "settlement_us",
    "mve",
    "price_ranges",
]

FINAL_STATUSES = PREREG.final_statuses


def ts_us(value: str | None) -> int | None:
    """ISO 8601 timestamp to integer microseconds since the epoch, None when absent."""
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return int(dt.timestamp()) * 1_000_000 + dt.microsecond


def series_of(ticker: str) -> str:
    """Series ticker from a market or event ticker (Kalshi's `SERIES-EVENT-MARKET` convention)."""
    return ticker.split("-", 1)[0]


def _num(obj: dict[str, Any], new: str, old: str, scale: float) -> float | None:
    v = obj.get(new)
    if v not in (None, ""):
        return float(v)
    v = obj.get(old)
    if v not in (None, ""):
        return float(v) / scale
    return None


def normalize_trade(t: dict[str, Any]) -> tuple | None:
    side = t.get("taker_outcome_side") or t.get("taker_side")
    if side not in ("yes", "no"):
        return None
    price = _num(t, "yes_price_dollars", "yes_price", 100.0)
    count = _num(t, "count_fp", "count", 1.0)
    created = ts_us(t.get("created_time"))
    if price is None or count is None or created is None or not t.get("ticker"):
        return None
    return (
        t["ticker"],
        str(t.get("trade_id", "")),
        count,
        price,
        side == "yes",
        created,
        bool(t.get("is_block_trade", False)),
    )


def normalize_market(m: dict[str, Any]) -> dict[str, Any]:
    event = m.get("event_ticker") or ""
    series = series_of(event or m["ticker"])
    mve = bool(m.get("mve_collection_ticker")) or series.startswith("KXMVE")
    return {
        "ticker": m["ticker"],
        "event_ticker": event,
        "series": series,
        "status": m.get("status") or "",
        "result": (m.get("result") or "").lower(),
        "close_us": ts_us(m.get("close_time")),
        "expected_expiration_us": ts_us(m.get("expected_expiration_time")),
        "latest_expiration_us": ts_us(m.get("latest_expiration_time")),
        "settlement_us": ts_us(m.get("settlement_ts")),
        "mve": mve,
        "price_ranges": json.dumps(m.get("price_ranges") or []),
    }


def parse_ranges(price_ranges: str | list | None) -> list[tuple[float, float, float]]:
    """`price_ranges` as sorted (start, end, step) triples; the one-cent grid when absent."""
    raw = json.loads(price_ranges) if isinstance(price_ranges, str) else (price_ranges or [])
    out = []
    for r in raw:
        try:
            out.append((float(r["start"]), float(r["end"]), float(r["step"])))
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(out) or [(0.0, 1.0, 0.01)]


def tick_at(ranges: list[tuple[float, float, float]], price: float) -> float:
    """Step of the interval containing `price`; the last interval also holds its end point."""
    for start, end, step in ranges:
        if start <= price < end:
            return step
    return ranges[-1][2] if price >= ranges[-1][1] else ranges[0][2]


def top_of_book(m: dict[str, Any]) -> tuple[float, float, float, float] | None:
    """(best YES bid, its size, best YES ask, its size) from a market object; None if one-sided."""
    bid = _num(m, "yes_bid_dollars", "yes_bid", 100.0)
    ask = _num(m, "yes_ask_dollars", "yes_ask", 100.0)
    bid_size = _num(m, "yes_bid_size_fp", "yes_bid_size", 1.0) or 0.0
    ask_size = _num(m, "yes_ask_size_fp", "yes_ask_size", 1.0) or 0.0
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask >= 1 or bid_size <= 0 or ask_size <= 0 or bid >= ask:
        return None
    return bid, bid_size, ask, ask_size


def maker_fee(rate: float, qty: float, price: float) -> float:
    """Kalshi maker fee in dollars for one fill: rate x C x P x (1 - P), rounded up to the cent."""
    if rate <= 0 or qty <= 0:
        return 0.0
    raw = rate * qty * price * (1.0 - price)
    cents = -(-round(raw * 100.0, 9) // 1)  # ceiling, after removing float noise
    return cents / 100.0


def maker_fee_rate(fee_type: str | None, fee_multiplier: float | None, coef: float) -> float:
    """Maker fee coefficient. Only `quadratic_with_maker_fees` charges makers on single markets;
    the combo variant concerns multivariate markets, which are excluded (Amendment 2)."""
    if fee_type == "quadratic_with_maker_fees":
        return coef * (1.0 if fee_multiplier is None else float(fee_multiplier))
    return 0.0


def is_final(status: str | None, result: str | None) -> bool:
    return (status or "") in FINAL_STATUSES and (result or "").lower() in ("yes", "no", "scalar")


def closes_us(m: dict[str, Any]) -> int | None:
    """When trading on a market is expected to end: the earlier of close and expected expiration.

    Mention markets carry an expected expiration two weeks after the event they settle on, and
    some sports markets a close a week after the match, so neither field alone is the horizon.
    """
    times = [t for t in (ts_us(m.get("close_time")), ts_us(m.get("expected_expiration_time"))) if t]
    return min(times) if times else None


def bucket_of(price: float, edges: tuple[float, ...]) -> int:
    """Index of the price bucket; edges are lower bounds, the last bucket is closed at 1."""
    idx = 0
    for i, lo in enumerate(edges):
        if price >= lo:
            idx = i
    return idx


def bucket_label(idx: int, edges: tuple[float, ...]) -> str:
    lo = edges[idx]
    hi = edges[idx + 1] if idx + 1 < len(edges) else 1.0
    close = "]" if idx + 1 == len(edges) else ")"
    return f"[{lo:.2f}, {hi:.2f}{close}"
