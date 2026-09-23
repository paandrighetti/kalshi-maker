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


def test_hour_straddling_the_cutoff_reads_both_tiers_and_filters():
    h = int(datetime(2026, 7, 24, 0, tzinfo=timezone.utc).timestamp()) - 1800
    cutoff = h + 1800
    hist = [
        _trade("KXM-1-A", "a", "2026-07-23T23:30:00.000001Z"),
        _trade("KXM-1-A", "b", "2026-07-23T23:29:59.999999Z"),  # before the hour
        _trade("KXS-1-A", "c", "2026-07-23T23:45:00Z"),  # sports series, dropped
    ]
    live = [
        _trade("KXM-1-A", "d", "2026-07-24T00:10:00Z"),
        _trade("KXM-1-A", "d", "2026-07-24T00:10:00Z"),  # duplicate id
        _trade("KXM-1-A", "e", "2026-07-24T00:30:00Z"),  # end of the hour, excluded
    ]
    fc = FakeClient(hist, live)
    df = ingest.trades_for_hour(fc, h, cutoff, {"KXS"})
    assert sorted(df["trade_id"]) == ["a", "d"]
    assert [c[2] for c in fc.calls] == [True, False]
    assert fc.calls[0][:2] == (h - 1, h + 3601)


def test_ingest_trades_is_resumable(tmp_path, monkeypatch):
    d = tmp_path / "data"
    d.mkdir()
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
    hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)[:3]
    monkeypatch.setattr(ingest, "sampled_hours", lambda *a: hours)

    class C:
        requests = 0

        def cutoff(self):
            return {"trades_created_ts": "2026-07-24T00:00:00Z"}

        def trades(self, min_ts, max_ts, historical):
            self.n = getattr(self, "n", 0) + 1
            return iter([])

    c = C()
    ingest.ingest_trades(c, d, 0)
    assert c.n == 3
    ingest.ingest_trades(c, d, 0)
    assert c.n == 3  # nothing downloaded twice
