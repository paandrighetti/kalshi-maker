"""HTTP client behavior and the ingestion of sampled hours, without the network."""

from collections import Counter
from datetime import datetime, timezone

import httpx
import pandas as pd
import pytest

from kmaker import ingest
from kmaker.client import Kalshi, KalshiError
from kmaker.config import PREREG


def client_for(handler, bases=("https://a.test/v2",)):
    return Kalshi(bases, rate=0, transport=httpx.MockTransport(handler), sleep=lambda s: None)


def test_pagination_follows_cursor():
    def handler(req):
        cur = req.url.params.get("cursor")
        page = {None: (["t1", "t2"], "c1"), "c1": (["t3"], "")}[cur]
        return httpx.Response(200, json={"trades": [{"id": x} for x in page[0]], "cursor": page[1]})

    with client_for(handler) as c:
        assert [t["id"] for t in c.trades(0, 10, historical=False)] == ["t1", "t2", "t3"]


def test_retries_429_then_succeeds_and_raises_on_404():
    calls = Counter()

    def handler(req):
        calls[req.url.path] += 1
        if req.url.path.endswith("/historical/cutoff"):
            return (
                httpx.Response(429)
                if calls[req.url.path] < 3
                else httpx.Response(200, json={"trades_created_ts": "2026-07-24T00:00:00Z"})
            )
        return httpx.Response(404, text="nope")

    with client_for(handler) as c:
        assert c.cutoff()["trades_created_ts"].startswith("2026-07-24")
        with pytest.raises(KalshiError):
            c.get("/missing")
    assert calls["/v2/historical/cutoff"] == 3


def test_transport_error_rotates_base():
    seen = []

    def handler(req):
        seen.append(req.url.host)
        if req.url.host == "a.test":
            raise httpx.ConnectError("down", request=req)
        return httpx.Response(200, json={"series": [{"ticker": "S"}]})

    with client_for(handler, bases=("https://a.test/v2", "https://b.test/v2")) as c:
        assert c.series() == [{"ticker": "S"}]
    assert seen == ["a.test", "b.test"]


def test_sampled_hours_are_deterministic_and_partition_time():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 11, tzinfo=timezone.utc)
    sets = [set(ingest.sampled_hours(start, end, 12, r)) for r in range(12)]
    assert sum(len(s) for s in sets) == 240
    assert set().union(*sets) == {int(start.timestamp()) + 3600 * i for i in range(240)}
    assert ingest.sampled_hours(start, end, 12, 0) == ingest.sampled_hours(start, end, 12, 0)
    assert 5 <= len(sets[0]) <= 40


def _trade(ticker, tid, created, side="yes"):
    return {
        "ticker": ticker,
        "trade_id": tid,
        "count_fp": "1.00",
        "yes_price_dollars": "0.30",
        "taker_outcome_side": side,
        "created_time": created,
        "is_block_trade": False,
    }


class FakeClient:
    def __init__(self, historical, live):
        self.data = {True: historical, False: live}
        self.calls = []
        self.requests = 0

    def trades(self, min_ts, max_ts, historical):
        self.calls.append((min_ts, max_ts, historical))
        return iter(self.data[historical])


def test_every_hour_reads_live_then_historical_and_filters():
    h = int(datetime(2026, 7, 24, 0, tzinfo=timezone.utc).timestamp()) - 1800
    hist = [
        _trade("KXM-1-A", "a", "2026-07-23T23:30:00.000001Z"),
        _trade("KXM-1-A", "b", "2026-07-23T23:29:59.999999Z"),  # before the hour
        _trade("KXS-1-A", "c", "2026-07-23T23:45:00Z"),  # sports series, dropped
        _trade("KXM-1-A", "d", "2026-07-24T00:10:00Z"),  # moved to historical meanwhile
    ]
    live = [
        _trade("KXM-1-A", "d", "2026-07-24T00:10:00Z"),
        _trade("KXM-1-A", "d", "2026-07-24T00:10:00Z"),  # duplicate id
        _trade("KXM-1-A", "e", "2026-07-24T00:30:00Z"),  # end of the hour, excluded
    ]
    fc = FakeClient(hist, live)
    rows = ingest.trades_for_hour(fc, h, {"KXS"})
    assert sorted(r[1] for r in rows) == ["a", "d"]
    assert fc.calls == [(h - 1, h + 3601, False), (h - 1, h + 3601, True)]


def _series_file(d):
    pd.DataFrame(
        [
            {
                "series": "KXM",
                "category": "Mentions",
                "fee_type": "quadratic",
                "fee_multiplier": 1.0,
                "title": "",
            }
        ]
    ).to_parquet(d / "series.parquet")


class HourClient:
    """One trade per hour from the live tier, none from the historical one."""

    requests = 0

    def __init__(self, empty=()):
        self.n = 0
        self.empty = set(empty)

    def trades(self, min_ts, max_ts, historical):
        self.n += 1
        h = min_ts + 1
        if historical or h in self.empty:
            return iter([])
        ts = datetime.fromtimestamp(h + 5, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return iter([_trade("KXM-1-A", f"id{h}", ts)])


def test_ingest_trades_is_resumable(tmp_path, monkeypatch):
    d = tmp_path / "data"
    d.mkdir()
    _series_file(d)
    hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)[:3]
    monkeypatch.setattr(ingest, "sampled_hours", lambda *a: hours)
    c = HourClient()
    paths = ingest.ingest_trades(c, d, 0)
    assert c.n == 6 and all(p.exists() for p in paths)
    assert ingest.hour_counts(d, 0) == {ingest.hour_key(h): 1 for h in hours}
    ingest.ingest_trades(c, d, 0)
    assert c.n == 6  # nothing downloaded twice


def test_empty_hours_are_fetched_once_more_and_keep_their_schema(tmp_path, monkeypatch):
    import duckdb

    d = tmp_path / "data"
    d.mkdir()
    _series_file(d)
    hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)[:3]
    monkeypatch.setattr(ingest, "sampled_hours", lambda *a: hours)
    c = HourClient(empty={hours[0]})
    ingest.ingest_trades(c, d, 0)
    assert c.n == 8  # 3 hours x 2 tiers, then the empty hour once more
    assert ingest.hour_counts(d, 0)[ingest.hour_key(hours[0])] == 0
    # an empty file first in the glob must not break the schema of the others
    got = duckdb.sql(
        f"SELECT count(*), any_value(ticker) FROM read_parquet('{d}/trades_r0/*.parquet')"
    ).fetchone()
    assert got == (2, "KXM-1-A")


def _market_part(d, part, records):
    rows = [
        {
            **{c: None for c in ingest.MARKET_SCHEMA.names},
            "ticker": t,
            "status": status,
            "result": result,
        }
        for t, status, result in records
    ]
    ingest.write_rows(rows, ingest.MARKET_SCHEMA, d / "markets" / f"part-{part:05d}.parquet")


def test_markets_to_fetch_follow_the_latest_part(tmp_path):
    # A final; B final in the later part; C final first, then re-fetched and not final; D new
    _market_part(
        tmp_path, 0, [("A", "finalized", "yes"), ("B", "active", ""), ("C", "settled", "no")]
    )
    _market_part(tmp_path, 1, [("B", "finalized", "no"), ("C", "determined", "no")])
    trades = []
    for i, t in enumerate(["A", "B", "C", "D", "D"]):
        path = tmp_path / "trades_r0" / f"h{i}.parquet"
        ingest.write_rows([(t, f"id{i}", 1.0, 0.5, True, 0, False)], ingest.TRADE_SCHEMA, path)
        trades.append(path)
    n_wanted, n_final, todo = ingest._todo_tickers(
        tmp_path, trades + [tmp_path / "missing.parquet"]
    )
    assert (n_wanted, n_final) == (4, 2)
    assert pd.read_parquet(todo)["ticker"].tolist() == ["C", "D"]
