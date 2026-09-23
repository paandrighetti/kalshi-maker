"""End-to-end wiring against a fake Kalshi API: pipeline to report, and paper maker cycles."""

import json
import time
from datetime import datetime, timezone

import httpx
import numpy as np
import pytest

from kmaker import backtest, cli, ingest, report
from kmaker.client import Kalshi
from kmaker.config import PREREG, Settings
from kmaker.paper import PaperMaker


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class FakeAPI:
    """Serves /series, trades (live and historical tiers) and markets for a few hours."""

    def __init__(self, hours):
        rng = np.random.default_rng(3)
        self.cutoff = int(datetime(2026, 7, 24, tzinfo=timezone.utc).timestamp())
        self.trades = {True: [], False: []}
        self.markets = {True: {}, False: {}}
        self.requests = 0
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
                    "latest_expiration_time": iso(h + 86400),
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
        self.requests += 1
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


@pytest.fixture
def pipeline_env(tmp_path, monkeypatch):
    hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)
    # a few hours on each side of the split and of the historical cutoff
    pick = [h for h in hours if h < 1767225600][:3] + [h for h in hours if h > 1785000000][:3]
    monkeypatch.setattr(ingest, "sampled_hours", lambda *a: pick)
    monkeypatch.setattr(backtest, "sampled_hours", lambda *a: pick)
    api = FakeAPI(pick)
    monkeypatch.setenv("KM_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("KM_REPORTS_DIR", str(tmp_path / "reports"))

    def fake_client(s, rate=None):
        return Kalshi(
            ["https://k.test/v2"],
            rate=0,
            transport=httpx.MockTransport(api.handler),
            sleep=lambda s: None,
        )

    monkeypatch.setattr(cli, "_client", fake_client)
    return api, tmp_path / "data", tmp_path / "reports"


def test_pipeline_to_report_then_a_restart_changes_nothing(pipeline_env):
    api, data_dir, reports_dir = pipeline_env
    cli.cmd_pipeline(Settings(), holdout=False)
    summary = json.loads((reports_dir / "backtest" / "primary" / "summary.json").read_text())
    assert summary["counts"]["trades"] == 144  # sports trades never written
    assert summary["counts"]["trades_ok"] == 144
    # the markets settle within hours, so the only period with data is the one of each hour:
    # both periods are present because the picked hours straddle the split
    assert summary["validity"]["periods"] == ["confirmation", "exploration"]
    gate = (data_dir / "gate.json").read_text()
    text = (reports_dir / "BACKTEST.md").read_text()
    assert "Pre-registration SHA-256" in text and "## Verdict" in text
    before = api.requests
    cli.cmd_pipeline(Settings(), holdout=False)
    assert api.requests == before  # the primary sample is decided once, nothing is fetched
    assert (data_dir / "gate.json").read_text() == gate


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
        self.result, self.status = "", "active"
        self.fail_trades = False

    def _market(self, ticker="KXM-E1-A"):
        return {
            "ticker": ticker,
            "event_ticker": "KXM-E1",
            "status": self.status,
            "close_time": iso(self.now + 3600),
            "expected_expiration_time": iso(self.now + 20 * 86400),  # like mentions
            "volume_24h_fp": "500.00",
            "result": self.result,
            "settlement_ts": iso(self.now),
            "price_ranges": [{"start": "0", "end": "1", "step": "0.01"}],
            **self.book,
        }

    def open_market_pages(self):
        self.requests += 1
        yield [self._market(), {**self._market("KXS-E9-A"), "event_ticker": "KXS-E9"}]

    def updated_markets(self, min_updated_ts):
        self.requests += 1
        return iter([])

    def markets_by_tickers(self, tickers, historical):
        self.requests += 1
        return [self._market(t) for t in tickers if t == "KXM-E1-A"]

    def recent_trade_pages(self, min_ts):
        self.requests += 1
        if self.fail_trades:

            def broken():
                yield self.tape[:1]
                raise RuntimeError("page 2 failed")

            return broken()
        out, self.tape = self.tape, []
        return iter([out])


def _trade(tid, price, qty):
    return {
        "ticker": "KXM-E1-A",
        "trade_id": tid,
        "count_fp": f"{qty:.2f}",
        "yes_price_dollars": f"{price:.4f}",
        "taker_outcome_side": "yes",
        "created_time": iso(time.time()),
        "is_block_trade": False,
    }


def test_paper_maker_cycles(tmp_path, monkeypatch):
    gate = {
        "generated_at": "x",
        "valid": True,
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
    pm.cycle()  # the listing completes, the market is quoted: PENNY 0.19, JOIN 0.20 behind 30
    assert pm.active == ["KXM-E1-A"]
    quotes = sorted((o.variant, o.price, o.queue_ahead) for o in pm.sim.live_orders("KXM-E1-A"))
    assert quotes == [("JOIN", 0.20, 30.0), ("PENNY", 0.19, 0.0)]
    time.sleep(1.1)  # let the quotes go live

    # a poll that fails on its second page keeps what the first page applied, and the retry
    # reads the same window again without applying the trade twice
    fake.tape = [_trade("x1", 0.20, 40.0)]
    fake.fail_trades = True
    last_poll = pm.last_trade_poll
    pm.cycle()
    assert pm.last_trade_poll == last_poll  # the window did not move
    assert "trades" in pm.db.execute("SELECT errors FROM cycles ORDER BY ts_us DESC").fetchone()[0]
    fake.fail_trades = False
    pm.cycle()
    fills = pm.db.execute("SELECT variant, price, qty FROM fills ORDER BY variant").fetchall()
    assert fills == [("JOIN", 0.2, 10.0), ("PENNY", 0.19, 10.0)]

    # settlement waits for a final status
    fake.result, fake.status = "no", "determined"
    pm.check_settlements()
    assert pm.db.execute("SELECT count(*) FROM settlements").fetchone()[0] == 0
    fake.status = "finalized"
    pm.check_settlements()
    text, digest = report.forward_report(tmp_path)
    assert "PENNY" in digest and "JOIN" in digest
    assert "19.000 cents per contract" in text and "20.000 cents per contract" in text


def test_tape_watchdog_pulls_quotes(tmp_path, monkeypatch):
    gate = {
        "generated_at": "x",
        "valid": True,
        "qualifying": [
            {"variant": "PENNY", "category": "Mentions", "side": "short_yes", "bucket": 1}
        ],
    }
    monkeypatch.setenv("KM_DATA_DIR", str(tmp_path))
    fake = FakeLive()
    pm = PaperMaker(Settings(), fake, gate, {"KXM": ("Mentions", "quadratic", 1.0)})
    pm.cycle()
    assert pm.sim.live_orders("KXM-E1-A")
    fake.fail_trades, fake.tape = True, [_trade("y1", 0.30, 1.0)]
    pm.last_tape_ok -= 1000  # blind for longer than the watchdog allows
    pm.cycle()
    assert pm.sim.live_orders("KXM-E1-A") == []


def test_a_quote_replaced_during_an_outage_still_fills_from_the_backlog(tmp_path, monkeypatch):
    gate = {
        "generated_at": "x",
        "valid": True,
        "qualifying": [
            {"variant": "PENNY", "category": "Mentions", "side": "short_yes", "bucket": 1}
        ],
    }
    monkeypatch.setenv("KM_DATA_DIR", str(tmp_path))
    fake = FakeLive()
    pm = PaperMaker(Settings(), fake, gate, {"KXM": ("Mentions", "quadratic", 1.0)})
    pm.cycle()  # PENNY ask at 0.19
    time.sleep(1.1)
    hit = _trade("z1", 0.19, 5.0)  # a taker lifts our ask while the tape cannot be read
    fake.fail_trades, fake.tape = True, []
    fake.book = {**fake.book, "yes_ask_dollars": "0.2500"}  # the ask moves: requote at 0.24
    pm.cycle()
    (old,) = [o for o in pm.sim.orders["KXM-E1-A"] if o.price == 0.19]
    assert old.cancel_us != 2**62
    for _ in range(3):  # a long outage: many cycles, pruning must keep the canceled quote
        pm.last_tape_ok = time.time()  # keep the watchdog out of this test
        pm.cycle()
    assert any(o.price == 0.19 for o in pm.sim.orders["KXM-E1-A"])
    fake.fail_trades, fake.tape = False, [hit]
    pm.cycle()
    got = pm.db.execute("SELECT price, qty FROM fills").fetchall()
    assert got == [(0.19, 5.0)]


def test_failed_checks_are_retried_until_the_markets_are_final(pipeline_env, monkeypatch):
    api, data_dir, reports_dir = pipeline_env
    for m in api.markets[True].values():  # every market not yet final at the first download
        m["status"] = "determined"
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(seconds)
        for m in api.markets[True].values():
            m["status"] = "finalized"

    monkeypatch.setattr(cli.time, "sleep", fake_sleep)
    cli.cmd_pipeline(Settings(), holdout=False, retry_wait_s=86400)
    gate = json.loads((data_dir / "gate.json").read_text())
    assert sleeps == [86400] and gate["valid"]
    assert "Pending" not in (reports_dir / "BACKTEST.md").read_text()


def test_an_invalid_gate_is_written_only_after_six_days(pipeline_env, monkeypatch):
    api, data_dir, reports_dir = pipeline_env
    for m in api.markets[True].values():
        m["status"] = "determined"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "first_decision_attempt.txt").write_text(f"{time.time() - 7 * 86400:.0f}")
    cli.cmd_pipeline(Settings(), holdout=False)
    gate = json.loads((data_dir / "gate.json").read_text())
    assert not gate["valid"] and "non-final" in gate["invalid_reasons"][0]
    text, digest = report.forward_report(data_dir)
    assert "validity checks" in digest


def test_retry_gives_up_on_client_errors_and_retries_transient_ones():
    from kmaker.client import KalshiClientError, KalshiError

    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise KalshiError("HTTP 503")
        return "ok"

    assert cli._retry(flaky, wait_s=0) == "ok" and len(calls) == 3

    def wrong():
        raise KalshiClientError("HTTP 400")

    with pytest.raises(KalshiClientError):
        cli._retry(wrong, wait_s=0)


def test_no_data_writes_an_invalid_gate_only_on_the_final_attempt(tmp_path):
    d, r = tmp_path / "data", tmp_path / "reports"
    d.mkdir()
    s = backtest.run(d, r, 0, write_gate=True, final_attempt=False)
    assert not s["validity"]["valid"] and not (d / "gate.json").exists()
    s = backtest.run(d, r, 0, write_gate=True, final_attempt=True)
    gate = json.loads((d / "gate.json").read_text())
    assert not gate["valid"] and gate["invalid_reasons"] == ["no market record was downloaded"]
