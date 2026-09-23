"""Forward accounting: settlement profit, the pre-registered limits and the report."""

import json

import numpy as np
import pandas as pd

from kmaker import report
from kmaker.paper import Fill, MarketInfo, open_db, write_fills
from kmaker.schema import parse_ranges

S = 1_000_000
Q = [{"variant": "PENNY", "category": "Mentions", "side": "short_yes", "bucket": 1}]


def fills_frame(rows):
    base = {
        "id": 0,
        "event": "E",
        "category": "Mentions",
        "variant": "PENNY",
        "side": "short_yes",
        "bucket": 1,
        "fee_rate": 0.0,
        "via": "tape",
        "improved": 1,
        "queue_ahead": 0.0,
        "settled_us": np.nan,
        "result": None,
    }
    out = []
    for i, r in enumerate(rows):
        out.append({**base, "id": i, **r})
    return report.with_pnl(pd.DataFrame(out))


def test_profit_signs_and_fees():
    f = fills_frame(
        [
            {"ts_us": 1, "ticker": "A", "price": 0.20, "qty": 10.0, "result": "no"},
            {"ts_us": 2, "ticker": "A", "price": 0.20, "qty": 10.0, "result": "yes"},
            {
                "ts_us": 3,
                "ticker": "A",
                "price": 0.40,
                "qty": 10.0,
                "result": "yes",
                "side": "long_yes",
                "fee_rate": 0.0175,
            },
            {"ts_us": 4, "ticker": "A", "price": 0.40, "qty": 10.0, "result": None},
        ]
    )
    assert np.allclose(f["pnl"].iloc[:3], [2.0, -8.0, 6.0 - 0.05])
    assert np.isnan(f["pnl"].iloc[3])
    assert np.allclose(f["risk_pc"], [0.8, 0.8, 0.4, 0.6])


def test_limits_per_market_event_and_total():
    rows = [
        {"ts_us": i, "ticker": "A", "price": 0.20, "qty": 40.0, "result": "no"} for i in range(4)
    ]
    sv = report.strategy_view(fills_frame(rows), Q)
    assert list(sv["qty"]) == [40.0, 40.0, 20.0]  # 100 contracts per market
    rows = [
        {"ts_us": i, "ticker": f"T{i}", "price": 0.50, "qty": 400.0, "result": "no"}
        for i in range(3)
    ]
    sv = report.strategy_view(fills_frame(rows), Q)
    # 100 per market, then 500 USD at risk per event: 50 + 50 + 50 USD at 0.5 each
    assert list(sv["qty"]) == [100.0, 100.0, 100.0]
    rows = [
        {"ts_us": i, "ticker": f"T{i}", "event": "E", "price": 0.01, "qty": 100.0, "result": "no"}
        for i in range(7)
    ]
    sv = report.strategy_view(fills_frame(rows), Q)
    assert np.isclose((sv["qty"] * sv["risk_pc"]).sum(), 500.0)


def test_risk_is_released_at_settlement():
    rows = (
        [
            {
                "ts_us": 1,
                "ticker": "A",
                "event": "E",
                "price": 0.01,
                "qty": 100.0,
                "result": "no",
                "settled_us": 8,
            },
        ]
        + [
            {
                "ts_us": 2 + i,
                "ticker": f"B{i}",
                "event": "E",
                "price": 0.01,
                "qty": 100.0,
                "result": "no",
            }
            for i in range(5)
        ]
        + [{"ts_us": 10, "ticker": "C", "event": "E", "price": 0.01, "qty": 100.0, "result": "no"}]
    )
    sv = report.strategy_view(fills_frame(rows), Q)
    # 99 USD per fill: A and B0..B3 use 495, B4 gets the last 5 USD, A settles at 8 and
    # frees 99 USD, so C at 10 fills in full
    assert np.isclose(sv[sv["ticker"] == "B4"]["qty"].iloc[0], 5.0 / 0.99)
    assert np.isclose(sv[sv["ticker"] == "C"]["qty"].iloc[0], 100.0)


def test_cells_outside_the_gate_are_ignored():
    rows = [{"ts_us": 1, "ticker": "A", "price": 0.50, "qty": 10.0, "result": "no", "bucket": 2}]
    assert report.strategy_view(fills_frame(rows), Q).empty


def test_forward_report_end_to_end(tmp_path):
    d = tmp_path
    (d / "gate.json").write_text(json.dumps({"generated_at": "x", "qualifying": Q}))
    db = open_db(d / "paper.sqlite")
    infos = {
        f"T{i}": MarketInfo(f"T{i}", f"E{i}", "Mentions", 0.0, parse_ranges(None), 10**15)
        for i in range(40)
    }
    fills = [
        Fill(i * S, f"T{i}", "PENNY", "short_yes", 0.20, 10.0, "tape", True, 0.0, "o", 10.0)
        for i in range(40)
    ]
    write_fills(db, fills, infos, "run")
    db.executemany(
        "INSERT INTO settlements VALUES (?,?,?,?,?)",
        [(f"T{i}", "yes" if i % 10 == 0 else "no", "finalized", 10**9, 10**9) for i in range(40)],
    )
    db.execute("INSERT INTO cycles VALUES (1, 2.5, 10, 20, 30, 4, 1, 12, 0.8, '')")
    db.commit()
    text, digest = report.forward_report(d)
    # 36 fills keep 0.20, 4 lose 0.80 on 10 contracts: (72 - 32) / 400 = 10 cents per contract
    assert "10.000 cents per contract" in text
    assert "PENNY: 40 ev" in digest


def test_void_results_release_risk_and_carry_no_pnl():
    rows = [
        {
            "ts_us": 1,
            "ticker": "A",
            "event": "E",
            "price": 0.01,
            "qty": 100.0,
            "result": "void",
            "settled_us": 3,
        },
    ] + [
        {
            "ts_us": 2 + i,
            "ticker": f"B{i}",
            "event": "E",
            "price": 0.01,
            "qty": 100.0,
            "result": "no",
        }
        for i in range(5)
    ]
    f = fills_frame(rows)
    assert np.isnan(f.loc[f["ticker"] == "A", "pnl"]).all()
    assert bool(f.loc[f["ticker"] == "A", "closed"].iloc[0])
    sv = report.strategy_view(f, Q)
    # the void at 3 frees its 99 USD, so B0..B4 all fit under the 500 USD per event
    assert np.allclose(sv[sv["ticker"] != "A"]["qty"], 100.0)


def test_fee_is_recomputed_for_the_contracts_kept():
    rows = [
        {"ts_us": 0, "ticker": "A", "price": 0.5, "qty": 90.0, "result": "no", "fee_rate": 0.0175},
        {"ts_us": 1, "ticker": "A", "price": 0.5, "qty": 30.0, "result": "no", "fee_rate": 0.0175},
    ]
    sv = report.strategy_view(fills_frame(rows), Q)
    kept = sv.iloc[1]
    assert kept["qty"] == 10.0
    # 10 x 0.5 = 5.00 gross, fee ceil(0.0175 x 10 x 0.25 x 100) / 100 = 0.05
    assert np.isclose(kept["pnl"], 5.0 - 0.05)


def test_idle_reasons(tmp_path):
    for gate, expect in (
        (
            {
                "valid": False,
                "invalid_reasons": ["3.0% of sampled hours returned no trade"],
                "qualifying": [],
            },
            "validity checks",
        ),
        ({"valid": True, "replication_fails": True, "qualifying": Q}, "replication check"),
        ({"valid": True, "qualifying": []}, "no pre-registered pair qualified"),
        ({"valid": True, "qualifying": Q}, "has not started yet"),
    ):
        (tmp_path / "gate.json").write_text(json.dumps({"generated_at": "x", **gate}))
        text, digest = report.forward_report(tmp_path)
        assert expect in text and expect in digest, expect
