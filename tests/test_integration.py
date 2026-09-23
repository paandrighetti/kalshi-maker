"""End-to-end wiring against a fake Kalshi API: pipeline to report, and paper maker cycles."""

import json
import time
from datetime import datetime, timezone

import httpx
import numpy as np

from kmaker import backtest, ingest, report
from kmaker.client import Kalshi
from kmaker.config import PREREG, Settings
from kmaker.paper import PaperMaker


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class FakeAPI:
    """Serves /series, /historical/cutoff, trades and markets for a few sampled hours."""

    def __init__(self, hours):
        rng = np.random.default_rng(3)
        self.cutoff = int(datetime(2026, 7, 24, tzinfo=timezone.utc).timestamp())
        self.trades = {True: [], False: []}
        self.markets = {True: {}, False: {}}
        n = 0
        for h in hours:
            for e in range(4):
                ev = f"KXM-{h}-{e}"
                tk = f"{ev}-A"
                hist = h < self.cutoff
                self.markets[hist][tk] = {
                    "ticker": tk,
                    "event_ticker": ev,
                    "status": "finalized",
                    "result": "yes" if rng.random() < 0.1 else "no",
                    "close_time": iso(h + 7200),
                    "settlement_ts": iso(h + 7300),
                    "price_ranges": [{"start": "0", "end": "1", "step": "0.01"}],
                }
                for k in range(6):
                    n += 1
                    self.trades[hist].append(
                        {
                            "ticker": tk,
                            "trade_id": f"t{n}",
                            "count_fp": "3.00",
                            "yes_price_dollars": "0.2000",
                            "taker_outcome_side": "yes",
                            "created_time": iso(h + 60 * e + k),
                            "is_block_trade": False,
                        }
                    )
                n += 1
                self.trades[hist].append(
                    {  # a sports trade in the same hour
                        "ticker": f"KXS-{h}-{e}-A",
                        "trade_id": f"t{n}",
                        "count_fp": "9.00",
                        "yes_price_dollars": "0.5000",
                        "taker_outcome_side": "yes",
                        "created_time": iso(h + 30),
                        "is_block_trade": False,
                    }
                )

    def handler(self, req: httpx.Request) -> httpx.Response:
        path, q = req.url.path.removeprefix("/v2"), req.url.params
        if path == "/series":
            return httpx.Response(
                200,
                json={
                    "series": [
                        {
                            "ticker": "KXM",
                            "category": "Mentions",
                            "fee_type": "quadratic",
                            "fee_multiplier": 1,
                        },
                        {
                            "ticker": "KXS",
                            "category": "Sports",
                            "fee_type": "quadratic",
                            "fee_multiplier": 1,
                        },
                    ]
                },
            )
        if path == "/historical/cutoff":
            return httpx.Response(200, json={"trades_created_ts": iso(self.cutoff)})
        if path in ("/historical/trades", "/markets/trades"):
            hist = path.startswith("/historical")
            lo, hi = int(q["min_ts"]), int(q["max_ts"])
            rows = [
                t
                for t in self.trades[hist]
                if lo <= datetime.fromisoformat(t["created_time"]).timestamp() <= hi
            ]
            page = int(q.get("cursor") or 0)
            chunk = rows[page * 5 : page * 5 + 5]  # tiny pages to exercise pagination
            nxt = str(page + 1) if page * 5 + 5 < len(rows) else ""
            return httpx.Response(200, json={"trades": chunk, "cursor": nxt})
        if path in ("/historical/markets", "/markets"):
            hist = path.startswith("/historical")
            got = [
                self.markets[hist][t] for t in q["tickers"].split(",") if t in self.markets[hist]
            ]
            return httpx.Response(200, json={"markets": got, "cursor": ""})
        return httpx.Response(404)


def test_pipeline_to_report(tmp_path):
    hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)
    # a few hours on each side of the split and of the historical cutoff
    pick = [h for h in hours if h < 1767225600][:3] + [h for h in hours if h > 1785000000][:3]
    api = FakeAPI(pick)
    data_dir, reports_dir = tmp_path / "data", tmp_path / "reports"
    c = Kalshi(
        ["https://k.test/v2"],
        rate=0,
        transport=httpx.MockTransport(api.handler),
        sleep=lambda s: None,
    )
    ingest.ingest_series(c, data_dir)
    import kmaker.ingest as ing

    orig = ing.sampled_hours
    ing.sampled_hours = lambda *a: pick
    try:
        paths = ingest.ingest_trades(c, data_dir, 0)
    finally:
        ing.sampled_hours = orig
    markets = ingest.ingest_markets(c, data_dir, paths)
    assert len(paths) == 6 and len(markets) == 24
    assert set(markets["result"]) <= {"yes", "no"}
    summary = backtest.run(data_dir, reports_dir, 0, write_gate=True)
    assert summary["counts"]["trades"] == 144  # sports trades never written
    assert summary["counts"]["prints_kept"] == 144
    text = report.backtest_report(reports_dir, data_dir)
    assert "Pre-registration SHA-256" in text and "## Verdict" in text
    # resumable: a second run downloads nothing new
    before = c.requests
    ing.sampled_hours = lambda *a: pick
    try:
        ingest.ingest_trades(c, data_dir, 0)
    finally:
        ing.sampled_hours = orig
    ingest.ingest_markets(c, data_dir, paths)
    assert c.requests - before == 1  # only the cutoff lookup


class FakeLive:
    """Duck-typed client for the paper maker: one Mentions market and a scripted tape."""

    def __init__(self):
        self.requests = 0
        self.now = time.time()
        self.book = {
            "yes_bid_dollars": "0.1500",
            "yes_bid_size_fp": "20.00",
            "yes_ask_dollars": "0.2000",
            "yes_ask_size_fp": "30.00",
        }
        self.tape = []
        self.result = ""

    def _market(self, ticker="KXM-E1-A"):
        return {
            "ticker": ticker,
            "event_ticker": "KXM-E1",
            "status": "active",
            "expected_expiration_time": iso(self.now + 3600),
            "close_time": iso(self.now + 7200),
            "volume_24h_fp": "500.00",
            "result": self.result,
            "settlement_ts": iso(self.now),
            "price_ranges": [{"start": "0", "end": "1", "step": "0.01"}],
            **self.book,
        }

    def open_markets(self):
        self.requests += 1
        yield self._market()
        yield {**self._market("KXS-E9-A"), "event_ticker": "KXS-E9"}  # sports, filtered

    def updated_markets(self, min_updated_ts):
        self.requests += 1
        return iter([])

    def markets_by_tickers(self, tickers, historical):
        self.requests += 1
        return [self._market(t) for t in tickers if t == "KXM-E1-A"]

    def recent_trades(self, min_ts):
        self.requests += 1
        out, self.tape = self.tape, []
        return iter(out)


def test_paper_maker_cycles(tmp_path, monkeypatch):
    gate = {
        "generated_at": "x",
        "qualifying": [
            {"variant": "PENNY", "category": "Mentions", "side": "short_yes", "bucket": 1},
            {"variant": "JOIN", "category": "Mentions", "side": "short_yes", "bucket": 1},
        ],
    }
    (tmp_path / "gate.json").write_text(json.dumps(gate))
    monkeypatch.setenv("KM_DATA_DIR", str(tmp_path))
    fake = FakeLive()
    series = {"KXM": ("Mentions", "quadratic", 1.0), "KXS": ("Sports", "quadratic", 1.0)}
    pm = PaperMaker(Settings(), fake, gate, series)
    pm.cycle()  # discovers the market and posts PENNY at 0.19 and JOIN at 0.20 behind 30
    assert pm.active == ["KXM-E1-A"]
    quotes = sorted((o.variant, o.price, o.queue_ahead) for o in pm.sim.live_orders("KXM-E1-A"))
    assert quotes == [("JOIN", 0.20, 30.0), ("PENNY", 0.19, 0.0)]
    time.sleep(1.1)  # let the quotes go live
    fake.tape = [
        {
            "ticker": "KXM-E1-A",
            "trade_id": "x1",
            "count_fp": "40.00",
            "yes_price_dollars": "0.2000",
            "taker_outcome_side": "yes",
            "created_time": iso(time.time()),
            "is_block_trade": False,
        }
    ]
    pm.cycle()
    fills = pm.db.execute("SELECT variant, price, qty FROM fills ORDER BY variant").fetchall()
    assert fills == [("JOIN", 0.2, 10.0), ("PENNY", 0.19, 10.0)]
    # settlement: the market resolves NO and the report counts both fills
    fake.result, fake.now = "no", time.time() - 7200
    pm.last_settle = 0
    pm.check_settlements()
    text, digest = report.forward_report(tmp_path)
    assert "PENNY" in digest and "JOIN" in digest
    assert "19.000 cents per contract" in text and "20.000 cents per contract" in text
