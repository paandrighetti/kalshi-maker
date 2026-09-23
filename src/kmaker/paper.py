"""Forward paper maker: virtual quotes on the live Kalshi book, filled from the public tape.

The simulator (`Simulator`) is pure: it takes books and taker orders with their timestamps and
returns fills, so it is tested without the network. `PaperMaker` does the input and output: it
polls Kalshi, feeds the simulator and appends fills to SQLite.

Each (variant, side) quote lives in its own counterfactual world: the PENNY and JOIN quotes of a
market never interact, and no virtual quote changes the real book. The fill rule, the queue model
and the latency are those of PREREGISTRATION.md, section "Forward test": a new quote and a cancel
both take effect one second after the book they were decided on.

Failure handling. Each stage of a cycle fails on its own: a failed market listing does not stop
trade polling or quoting. Trade ids are marked as seen only once a whole poll succeeded, and fills
are written as soon as they exist, so an API error never loses a fill. If the tape cannot be read
for two minutes, every quote is canceled, as a real maker's watchdog would do.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .client import Kalshi
from .config import PREREG, Settings
from .schema import (
    FINAL_STATUSES,
    bucket_of,
    closes_us,
    maker_fee_rate,
    normalize_market,
    normalize_trade,
    parse_ranges,
    series_of,
    tick_at,
    top_of_book,
    ts_us,
)

log = logging.getLogger(__name__)

EPS = 1e-9
INF = 2**62
TRADE_OVERLAP_S = 30
SCAN_BATCH = 200
LISTING_PAGES_PER_CYCLE = 5
TAPE_WATCHDOG_S = 120


@dataclass
class MarketInfo:
    ticker: str
    event: str
    category: str
    fee_rate: float
    ranges: list[tuple[float, float, float]]
    expiry_us: int
    volume_24h: float = 0.0
    two_sided: bool = False


@dataclass
class VOrder:
    oid: str
    ticker: str
    variant: str
    side: str  # short_yes: virtual YES ask; long_yes: virtual YES bid
    price: float
    remaining: float
    queue_ahead: float
    improved: bool
    live_us: int
    cancel_us: int = INF


@dataclass
class Fill:
    ts_us: int
    ticker: str
    variant: str
    side: str
    price: float
    qty: float
    via: str
    improved: bool
    queue_ahead: float
    oid: str
    taker_qty: float


@dataclass
class TakerOrder:
    ticker: str
    created_us: int
    taker_yes: bool
    levels: list[tuple[float, float]] = field(default_factory=list)  # (YES price, contracts)

    @property
    def qty(self) -> float:
        return sum(q for _, q in self.levels)


def group_taker_orders(rows: Iterable[tuple]) -> list[TakerOrder]:
    """Normalized trade rows to taker orders (same market, microsecond and taker side)."""
    orders: dict[tuple, TakerOrder] = {}
    for ticker, _tid, count, price, taker_yes, created_us, is_block in rows:
        if is_block:
            continue
        key = (ticker, created_us, taker_yes)
        o = orders.get(key)
        if o is None:
            o = orders[key] = TakerOrder(ticker, created_us, taker_yes)
        o.levels.append((price, count))
    return sorted(orders.values(), key=lambda o: o.created_us)


def target_quote(
    variant: str, side: str, book: tuple[float, float, float, float], ranges
) -> tuple[float, bool, float]:
    """(price, improved, queue ahead) of the quote a variant wants on one side of this book."""
    bid, bid_size, ask, ask_size = book
    if side == "short_yes":
        if variant == "PENNY":
            cand = round(ask - tick_at(ranges, ask - EPS), 6)
            if cand > bid + EPS:
                return cand, True, 0.0
        return ask, False, ask_size
    if variant == "PENNY":
        cand = round(bid + tick_at(ranges, bid), 6)
        if cand < ask - EPS:
            return cand, True, 0.0
    return bid, False, bid_size


class Simulator:
    """Virtual orders, their queue positions and their fills. No I/O."""

    def __init__(self, qualifying: list[dict], quote_size: float = PREREG.quote_size) -> None:
        self.quote_size = quote_size
        self.cells = {
            (q["variant"], q["category"], q["side"], int(q["bucket"])) for q in qualifying
        }
        self.variant_sides = sorted({(q["variant"], q["side"]) for q in qualifying})
        self.orders: dict[str, list[VOrder]] = {}
        self._seq = 0

    def eligible(self, variant: str, category: str, side: str, price: float) -> bool:
        b = bucket_of(price, PREREG.buckets)
        return (variant, category, side, b) in self.cells or (variant, "ALL", side, b) in self.cells

    def live_orders(self, ticker: str) -> list[VOrder]:
        """Orders not yet canceled; an order whose cancel is pending is no longer managed."""
        return [o for o in self.orders.get(ticker, []) if o.cancel_us == INF]

    def _fill(self, o: VOrder, reach: float, ts: int, via: str, taker_qty: float) -> Fill | None:
        qty = min(o.remaining, max(0.0, reach - o.queue_ahead))
        ahead = o.queue_ahead
        o.queue_ahead = max(0.0, o.queue_ahead - reach)
        if qty <= EPS:
            return None
        o.remaining -= qty
        if o.remaining <= EPS:
            o.cancel_us = min(o.cancel_us, ts)  # done; the next book posts a fresh quote
        return Fill(
            ts, o.ticker, o.variant, o.side, o.price, qty, via, o.improved, ahead, o.oid, taker_qty
        )

    def on_taker_order(self, t: TakerOrder) -> list[Fill]:
        side = "short_yes" if t.taker_yes else "long_yes"
        fills = []
        for o in self.orders.get(t.ticker, []):
            if o.side != side or o.remaining <= EPS:
                continue
            if not (o.live_us <= t.created_us < o.cancel_us):
                continue
            if side == "short_yes":
                reach = sum(q for p, q in t.levels if p >= o.price - EPS)
            else:
                reach = sum(q for p, q in t.levels if p <= o.price + EPS)
            if reach > EPS:
                f = self._fill(o, reach, t.created_us, "tape", t.qty)
                if f:
                    fills.append(f)
        return fills

    def on_book(
        self,
        info: MarketInfo,
        book: tuple[float, float, float, float] | None,
        now_us: int,
        live_delay_us: int,
    ) -> list[Fill]:
        """Crossing fills for stale quotes, then cancel and replace to the current targets."""
        fills = []
        if book is not None:
            bid, bid_size, ask, ask_size = book
            for o in self.live_orders(info.ticker):
                if now_us < o.live_us or o.remaining <= EPS:
                    continue
                if o.side == "short_yes" and bid >= o.price - EPS:
                    f = self._fill(o, bid_size, now_us, "cross", bid_size)
                elif o.side == "long_yes" and ask <= o.price + EPS:
                    f = self._fill(o, ask_size, now_us, "cross", ask_size)
                else:
                    f = None
                if f:
                    fills.append(f)
        orders = self.orders.setdefault(info.ticker, [])
        for variant, side in self.variant_sides:
            want = None
            if book is not None and now_us < info.expiry_us:
                price, improved, ahead = target_quote(variant, side, book, info.ranges)
                if self.eligible(variant, info.category, side, price):
                    want = (price, improved, ahead)
            keep = None
            for o in self.live_orders(info.ticker):
                if (o.variant, o.side) != (variant, side):
                    continue
                if want is not None and keep is None and abs(o.price - want[0]) < EPS:
                    keep = o
                else:
                    o.cancel_us = now_us + live_delay_us
            if want is not None and keep is None:
                self._seq += 1
                orders.append(
                    VOrder(
                        f"o{self._seq}",
                        info.ticker,
                        variant,
                        side,
                        want[0],
                        self.quote_size,
                        want[2],
                        want[1],
                        now_us + live_delay_us,
                    )
                )
        return fills

    def cancel_all(self, ticker: str, at_us: int) -> None:
        for o in self.live_orders(ticker):
            o.cancel_us = at_us

    def prune(self, before_us: int) -> None:
        """Forget orders canceled before `before_us`, once the tape up to then was processed."""
        for ticker in list(self.orders):
            kept = [o for o in self.orders[ticker] if o.cancel_us >= before_us]
            if kept:
                self.orders[ticker] = kept
            else:
                del self.orders[ticker]


# persistence ---------------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS fills (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts_us INTEGER, ticker TEXT, event TEXT, category TEXT,
    variant TEXT, side TEXT, price REAL, qty REAL, bucket INTEGER, via TEXT, improved INTEGER,
    queue_ahead REAL, fee_rate REAL, expiry_us INTEGER, oid TEXT, taker_qty REAL, run TEXT
);
CREATE TABLE IF NOT EXISTS settlements (
    ticker TEXT PRIMARY KEY, result TEXT, status TEXT, settled_us INTEGER, seen_us INTEGER
);
CREATE TABLE IF NOT EXISTS cycles (
    ts_us INTEGER, duration_s REAL, active INTEGER, candidates INTEGER, orders INTEGER,
    taker_orders INTEGER, fills INTEGER, requests INTEGER, trade_lag_s REAL, errors TEXT
);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
"""


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    return db


def write_fills(
    db: sqlite3.Connection, fills: list[Fill], infos: dict[str, MarketInfo], run: str
) -> None:
    if not fills:
        return
    rows = []
    for f in fills:
        i = infos[f.ticker]
        rows.append(
            (
                f.ts_us,
                f.ticker,
                i.event,
                i.category,
                f.variant,
                f.side,
                f.price,
                f.qty,
                bucket_of(f.price, PREREG.buckets),
                f.via,
                int(f.improved),
                f.queue_ahead,
                i.fee_rate,
                i.expiry_us,
                f.oid,
                f.taker_qty,
                run,
            )
        )
    db.executemany(
        "INSERT INTO fills (ts_us, ticker, event, category, variant, side, price, qty, bucket,"
        " via, improved, queue_ahead, fee_rate, expiry_us, oid, taker_qty, run)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    db.commit()


# the loop -------------------------------------------------------------------------------------


class PaperMaker:
    def __init__(self, settings: Settings, client: Kalshi, gate: dict, series: dict) -> None:
        self.s = settings
        self.client = client
        self.gate = gate
        self.series = series  # series ticker -> (category, fee_type, fee_multiplier)
        self.sim = Simulator(gate.get("qualifying", []))
        self.categories = {q["category"] for q in gate.get("qualifying", [])}
        self.db = open_db(settings.data_dir / "paper.sqlite")
        self.run_id = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        self.delay_us = int(PREREG.live_delay_s * 1e6)
        self.candidates: dict[str, MarketInfo] = {}
        self.known: dict[str, MarketInfo] = {}  # every market ever quoted, for fill metadata
        self.active: list[str] = []
        self.scan_order: list[str] = []
        self.scan_pos = 0
        self.listing: Iterator[list[dict]] | None = None
        self.listing_fresh: dict[str, MarketInfo] = {}
        self.seen_ids: deque[str] = deque(maxlen=300_000)
        self.seen_set: set[str] = set()
        self.last_trade_poll = time.time() - TRADE_OVERLAP_S
        self.last_tape_ok = time.time()
        self.last_full = 0.0
        self.last_incremental = 0.0
        self.last_settle = 0.0
        self.trade_lag_s = float("nan")

    # universe ---------------------------------------------------------------------------

    def _info(self, m: dict, now_us: int) -> MarketInfo | None:
        nm = normalize_market(m)
        if nm["mve"] or m.get("status") not in ("active", "open"):
            return None
        meta = self.series.get(series_of(nm["event_ticker"] or nm["ticker"]))
        if meta is None:
            return None
        category, fee_type, fee_mult = meta
        if category in PREREG.excluded_categories:
            return None
        if "ALL" not in self.categories and category not in self.categories:
            return None
        expiry = closes_us(m)
        horizon_us = PREREG.max_days_to_expiry * 86_400 * 1_000_000
        if expiry is None or expiry <= now_us or expiry - now_us > horizon_us:
            return None
        return MarketInfo(
            nm["ticker"],
            nm["event_ticker"],
            category,
            maker_fee_rate(fee_type, fee_mult, PREREG.maker_fee_coef),
            parse_ranges(nm["price_ranges"]),
            expiry,
            float(m.get("volume_24h_fp") or 0.0),
            top_of_book(m) is not None,
        )

    def listing_step(self) -> None:
        """Advance the full listing of open markets by a few pages; swap it in when complete.

        The full listing takes over a hundred pages. Spreading it over cycles keeps quotes and
        trade polling on schedule while it runs.
        """
        now = time.time()
        if self.listing is None:
            if self.last_full and now - self.last_full < 6 * 3600:
                return
            self.listing = self.client.open_market_pages()
            self.listing_fresh = {}
        now_us = int(now * 1e6)
        for _ in range(LISTING_PAGES_PER_CYCLE):
            try:
                page = next(self.listing, None)
            except Exception:
                # a broken listing restarts from scratch; a partial one is never swapped in
                self.listing, self.listing_fresh = None, {}
                raise
            if page is None:
                fresh = self.listing_fresh
                if self.last_full:  # keep what incremental updates found in the meantime
                    fresh = {**self.candidates, **fresh}
                self.candidates = {k: v for k, v in fresh.items() if v.expiry_us > now_us}
                self.scan_order = sorted(self.candidates)
                self.listing, self.last_full, self.last_incremental = None, now, now
                return
            for m in page:
                info = self._info(m, now_us)
                if info:
                    self.listing_fresh[info.ticker] = info

    def incremental_step(self) -> None:
        now = time.time()
        if not self.last_full or now - self.last_incremental < 300:
            return
        now_us = int(now * 1e6)
        for m in self.client.updated_markets(int(self.last_incremental) - 60):
            info = self._info(m, now_us)
            if info:
                self.candidates[info.ticker] = info
            else:
                self.candidates.pop(m.get("ticker", ""), None)
        self.candidates = {k: v for k, v in self.candidates.items() if v.expiry_us > now_us}
        self.scan_order = sorted(self.candidates)
        self.scan_pos = self.scan_pos % max(1, len(self.scan_order))
        self.last_incremental = now

    def scan_step(self) -> None:
        """Refresh the book summary of the next slice of candidates (round robin)."""
        if not self.scan_order:
            return
        batch = self.scan_order[self.scan_pos : self.scan_pos + SCAN_BATCH]
        nxt = self.scan_pos + SCAN_BATCH
        self.scan_pos = 0 if nxt >= len(self.scan_order) else nxt
        for i in range(0, len(batch), 50):
            for m in self.client.markets_by_tickers(batch[i : i + 50], historical=False):
                info = self.candidates.get(m.get("ticker", ""))
                if info is not None:
                    info.volume_24h = float(m.get("volume_24h_fp") or 0.0)
                    info.two_sided = top_of_book(m) is not None

    def choose_active(self, now_us: int) -> None:
        ranked = sorted(
            (i for i in self.candidates.values() if i.two_sided and i.volume_24h > 0),
            key=lambda i: (-i.volume_24h, i.ticker),
        )[: self.s.max_markets]
        keep = {i.ticker for i in ranked}
        for t in self.active:
            if t not in keep:
                self.sim.cancel_all(t, now_us + self.delay_us)
        self.active = sorted(keep)

    # cycle ------------------------------------------------------------------------------

    def poll_trades(self) -> list[TakerOrder]:
        """New taker orders on quoted markets. Nothing is marked seen unless the poll succeeds."""
        started = time.time()
        page_rows = list(self.client.recent_trades(int(self.last_trade_poll) - TRADE_OVERLAP_S))
        rows, newest = [], 0
        for t in page_rows:
            tid = str(t.get("trade_id", ""))
            if tid in self.seen_set:
                continue
            if len(self.seen_ids) == self.seen_ids.maxlen:
                self.seen_set.discard(self.seen_ids[0])
            self.seen_ids.append(tid)
            self.seen_set.add(tid)
            row = normalize_trade(t)
            if row is None:
                continue
            newest = max(newest, row[5])
            if row[0] in self.sim.orders:
                rows.append(row)
        if newest:
            self.trade_lag_s = started - newest / 1e6
        self.last_trade_poll = started
        self.last_tape_ok = time.time()
        return group_taker_orders(rows)

    def refresh_books(self) -> list[Fill]:
        fills = []
        for i in range(0, len(self.active), 50):
            batch = self.active[i : i + 50]
            try:
                got = {
                    m["ticker"]: m for m in self.client.markets_by_tickers(batch, historical=False)
                }
            except Exception:
                log.exception("book refresh failed; quotes of this batch are pulled")
                cancel_at = int(time.time() * 1e6) + self.delay_us
                for t in batch:
                    self.sim.cancel_all(t, cancel_at)
                continue
            recv_us = int(time.time() * 1e6)
            for t in batch:
                info, m = self.candidates.get(t), got.get(t)
                if info is None or m is None or m.get("status") not in ("active", "open"):
                    self.sim.cancel_all(t, recv_us + self.delay_us)
                    continue
                book = top_of_book(m)
                info.two_sided = book is not None
                info.volume_24h = float(m.get("volume_24h_fp") or info.volume_24h)
                self.known[t] = info
                fills += self.sim.on_book(info, book, recv_us, self.delay_us)
        return fills

    def check_settlements(self) -> None:
        """Record results of markets with fills once final; many close before expected."""
        now_us = int(time.time() * 1e6)
        pending = [
            r[0]
            for r in self.db.execute(
                "SELECT DISTINCT f.ticker FROM fills f LEFT JOIN settlements s USING (ticker)"
                " WHERE s.ticker IS NULL"
            )
        ]
        for i in range(0, len(pending), 50):
            batch = pending[i : i + 50]
            got = {m["ticker"]: m for m in self.client.markets_by_tickers(batch, historical=False)}
            missing = [t for t in batch if t not in got]
            if missing:
                hist = self.client.markets_by_tickers(missing, historical=True)
                got.update({m["ticker"]: m for m in hist})
            rows = [
                (
                    t,
                    (m.get("result") or "").lower(),
                    m.get("status"),
                    ts_us(m.get("settlement_ts")),
                    now_us,
                )
                for t, m in got.items()
                if m.get("status") in FINAL_STATUSES and m.get("result")
            ]
            self.db.executemany("INSERT OR REPLACE INTO settlements VALUES (?,?,?,?,?)", rows)
            self.db.commit()
        self.last_settle = time.time()

    def _stage(self, name: str, errors: list[str], fn, *args):
        try:
            return fn(*args)
        except Exception as exc:  # one failing stage must not stop the others
            log.exception("%s failed", name)
            errors.append(f"{name}: {type(exc).__name__}")
            return None

    def cycle(self) -> None:
        t0 = time.time()
        req0 = self.client.requests
        errors: list[str] = []
        self._stage("listing", errors, self.listing_step)
        self._stage("incremental", errors, self.incremental_step)
        self._stage("scan", errors, self.scan_step)
        self.choose_active(int(time.time() * 1e6))
        n_fills = 0
        taker_orders = self._stage("trades", errors, self.poll_trades) or []
        tape_fills = [f for t in taker_orders for f in self.sim.on_taker_order(t)]
        write_fills(self.db, tape_fills, self.known, self.run_id)
        n_fills += len(tape_fills)
        if time.time() - self.last_tape_ok > TAPE_WATCHDOG_S:
            # blind for too long: pull every quote and post nothing until the tape is back
            cancel_at = int(time.time() * 1e6) + self.delay_us
            for t in list(self.sim.orders):
                self.sim.cancel_all(t, cancel_at)
        else:
            book_fills = self._stage("books", errors, self.refresh_books) or []
            write_fills(self.db, book_fills, self.known, self.run_id)
            n_fills += len(book_fills)
        self.sim.prune(int((time.time() - 3 * max(self.s.cycle_s, TRADE_OVERLAP_S)) * 1e6))
        if time.time() - self.last_settle > 600:
            self._stage("settlements", errors, self.check_settlements)
        n_orders = sum(len(self.sim.live_orders(t)) for t in self.sim.orders)
        self.db.execute(
            "INSERT INTO cycles VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                int(t0 * 1e6),
                time.time() - t0,
                len(self.active),
                len(self.candidates),
                n_orders,
                len(taker_orders),
                n_fills,
                self.client.requests - req0,
                self.trade_lag_s,
                ";".join(errors),
            ),
        )
        self.db.commit()

    def run_forever(self) -> None:
        self.db.execute("INSERT OR REPLACE INTO meta VALUES ('gate', ?)", (json.dumps(self.gate),))
        self.db.commit()
        while True:
            t0 = time.time()
            try:
                self.cycle()
            except Exception:  # the loop itself must survive anything a cycle raises
                log.exception("cycle failed")
            time.sleep(max(0.0, self.s.cycle_s - (time.time() - t0)))
