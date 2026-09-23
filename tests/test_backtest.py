"""The backtest on synthetic tapes whose answer is known by construction."""

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from kmaker import backtest, ingest
from kmaker.config import PREREG
from kmaker.ingest import MARKET_SCHEMA, RANGE_SCHEMA, TRADE_SCHEMA, write_rows
from kmaker.schema import parse_ranges
from kmaker.stats import cluster_table

ONE_CENT = json.dumps([{"start": "0", "end": "1", "step": "0.01"}])
TAPERED = json.dumps(
    [
        {"start": "0", "end": "0.1", "step": "0.001"},
        {"start": "0.1", "end": "0.9", "step": "0.01"},
        {"start": "0.9", "end": "1", "step": "0.001"},
    ]
)
SERIES = [
    {
        "series": "KXM",
        "category": "Mentions",
        "fee_type": "quadratic",
        "fee_multiplier": 1.0,
        "title": "",
    },
    {
        "series": "KXW",
        "category": "Climate and Weather",
        "fee_type": "quadratic_with_maker_fees",
        "fee_multiplier": 1.0,
        "title": "",
    },
    {
        "series": "KXS",
        "category": "Sports",
        "fee_type": "quadratic",
        "fee_multiplier": 1.0,
        "title": "",
    },
]


def us(s: str) -> int:
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()) * 1_000_000


def market(ticker, event, series, result, settled="2026-01-06T00:00:00", **kw):
    m = {
        "ticker": ticker,
        "event_ticker": event,
        "series": series,
        "status": "finalized",
        "result": result,
        "close_us": None,
        "expected_expiration_us": None,
        "latest_expiration_us": us(settled),
        "settlement_us": us(settled),
        "mve": False,
        "price_ranges": ONE_CENT,
    }
    return {**m, **kw}


def write_dir(tmp_path, markets, trades, series=SERIES, all_hours=True):
    """A data directory as ingestion writes it; every sampled hour marked non-empty."""
    d = tmp_path / "data"
    d.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(series).to_parquet(d / "series.parquet", index=False)
    write_rows(markets, MARKET_SCHEMA, d / "markets" / "part-00000.parquet")
    ranges = []
    for m in markets:
        parsed = parse_ranges(m["price_ranges"])
        if parsed != ingest.DEFAULT_RANGES:
            ranges += [(m["ticker"], lo, hi, step) for lo, hi, step in parsed]
    write_rows(ranges, RANGE_SCHEMA, d / "ranges" / "part-00000.parquet")
    write_rows(trades, TRADE_SCHEMA, d / "trades_r0" / "2026-01-01T00.parquet")
    if all_hours:
        hours = ingest.sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, 0)
        (d / "hours_r0.json").write_text(json.dumps({ingest.hour_key(h): 1 for h in hours}))
    return d


def src_sums(con, keys):
    backtest.create_src(con)
    k = ", ".join(keys)
    df = con.execute(f"SELECT {k}, sum(w * v) AS s, sum(w) AS w FROM src GROUP BY {k}").df()
    return df.set_index(keys)


A, B, C = 0, 1, 2
SHORT, LONG = 0, 1


def test_hand_computed_statistics(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [
        # one taker order buying YES that sweeps two levels; market resolves NO
        ("KXM-E1-A", "t1", 4.0, 0.20, True, t0, False),
        ("KXM-E1-A", "t2", 6.0, 0.21, True, t0, False),
        # one taker order selling YES at a single level; market resolves NO
        ("KXM-E1-A", "t3", 3.0, 0.18, False, t0 + 5, False),
        # excluded: block trade, non-final market, sports, outside the window, late expiration
        ("KXM-E1-A", "t4", 50.0, 0.50, True, t0 + 9, True),
        ("KXM-E2-A", "t5", 50.0, 0.50, True, t0, False),
        ("KXS-E3-A", "t6", 50.0, 0.50, True, t0, False),
        ("KXM-E1-A", "t7", 50.0, 0.50, True, us("2026-09-10T00:00:00"), False),
        ("KXM-E4-A", "t8", 50.0, 0.50, True, t0, False),
        ("KXM-E9-A", "t9", 50.0, 0.50, True, t0, False),  # no market record
    ]
    markets = [
        market("KXM-E1-A", "KXM-E1", "KXM", "no"),
        market("KXM-E2-A", "KXM-E2", "KXM", "yes", status="determined"),
        market("KXS-E3-A", "KXS-E3", "KXS", "no"),
        market("KXM-E4-A", "KXM-E4", "KXM", "yes", latest_expiration_us=us("2026-12-31T00:00:00")),
    ]
    d = write_dir(tmp_path, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    counts = backtest.build_tables(con, d, 0)
    assert counts["trades"] == 9 and counts["trades_ok"] == 3
    assert counts["trades_block"] == 1 and counts["trades_not_final"] == 1
    assert counts["trades_excluded_category"] == 1 and counts["trades_outside_window"] == 1
    assert counts["trades_late_expiration"] == 1 and counts["trades_no_market"] == 1
    rows = src_sums(con, ["stat", "side"])
    # A, maker short YES: (4 x 0.20 + 6 x 0.21) / 10 = 0.206 per contract
    a = rows.loc[(A, SHORT)]
    assert np.isclose(a["s"] / a["w"], 0.206) and a["w"] == 10
    # C keeps only the emptied level at 0.20
    c = rows.loc[(C, SHORT)]
    assert np.isclose(c["s"] / c["w"], 0.20) and c["w"] == 4
    # B: q = min(10, 10) at 0.20 - 0.01 = 0.19, the maker keeps 0.19 when NO wins
    b = rows.loc[(B, SHORT)]
    assert np.isclose(b["s"] / b["w"], 0.19) and b["w"] == 10
    # the seller of YES at 0.18: the maker bought YES; NO wins, A = -0.18, B at 0.19 = -0.19
    assert np.isclose(rows.loc[(A, LONG)]["s"] / 3, -0.18)
    assert np.isclose(rows.loc[(B, LONG)]["s"] / 3, -0.19)
    assert (C, LONG) not in rows.index  # single-level order: its last level is unknown


def test_maker_fee_only_on_maker_fee_series_and_rounded_in_b(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [("KXW-E1-A", "t1", 10.0, 0.50, True, t0, False)]
    d = write_dir(tmp_path, [market("KXW-E1-A", "KXW-E1", "KXW", "no")], trades)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    rows = src_sums(con, ["stat"])
    # A: 0.50 - 0.0175 x 0.25 = 0.495625 per contract, unrounded
    assert np.isclose(rows.loc[A, "s"] / rows.loc[A, "w"], 0.50 - 0.0175 * 0.25)
    # B: a = 0.49, fee = ceil(0.0175 x 10 x 0.49 x 0.51 x 100) / 100 = 0.05 for 10 contracts
    assert np.isclose(rows.loc[B, "s"] / rows.loc[B, "w"], 0.49 - 0.005)


def test_combo_maker_fee_type_does_not_charge(tmp_path):
    series = [dict(SERIES[1], fee_type="quadratic_with_combo_maker_fees")]
    trades = [("KXW-E1-A", "t1", 10.0, 0.50, True, us("2026-01-05T12:00:00"), False)]
    d = write_dir(tmp_path, [market("KXW-E1-A", "KXW-E1", "KXW", "no")], trades, series)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    rows = src_sums(con, ["stat"])
    assert np.isclose(rows.loc[A, "s"] / rows.loc[A, "w"], 0.50)


def test_tapered_grid_ticks_and_float_buckets(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [
        ("KXM-E1-A", "t1", 1.0, 0.90, True, t0, False),  # ask 0.90 -> penny 0.89, bucket 3
        ("KXM-E1-A", "t2", 1.0, 0.10, True, t0 + 1, False),  # ask 0.10 -> 0.099, bucket 0
        ("KXM-E2-A", "t3", 1.0, 0.09, False, t0 + 2, False),  # bid 0.09 -> 0.10, bucket 1
    ]
    markets = [
        market("KXM-E1-A", "KXM-E1", "KXM", "no", price_ranges=TAPERED),
        market("KXM-E2-A", "KXM-E2", "KXM", "no"),
    ]
    d = write_dir(tmp_path, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    backtest.create_src(con)
    got = con.execute(
        "SELECT side, bucket, round(v, 6) AS v FROM src WHERE stat = 1 ORDER BY v"
    ).fetchall()
    # short YES at 0.099 and 0.89 keep the price when NO wins; long YES at 0.10 loses it
    assert got == [(LONG, 1, -0.1), (SHORT, 0, 0.099), (SHORT, 3, 0.89)]


def test_periods_follow_settlement_date(tmp_path):
    trades = [
        ("KXM-E1-A", "t1", 1.0, 0.30, True, us("2026-04-20T00:00:00"), False),
        ("KXM-E1-A", "t2", 1.0, 0.30, True, us("2026-05-03T00:00:00"), False),
    ]
    markets = [market("KXM-E1-A", "KXM-E1", "KXM", "no", settled="2026-05-04T00:00:00")]
    d = write_dir(tmp_path, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    backtest.create_src(con)
    assert con.execute("SELECT DISTINCT period FROM src").fetchall() == [(1,)]


def test_events_are_distinct_in_rollups(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [  # one event, three buckets
        ("KXM-E1-A", "t1", 1.0, 0.05, True, t0, False),
        ("KXM-E1-A", "t2", 1.0, 0.50, True, t0 + 1, False),
        ("KXM-E1-B", "t3", 1.0, 0.95, True, t0 + 2, False),
    ]
    markets = [
        market("KXM-E1-A", "KXM-E1", "KXM", "no"),
        market("KXM-E1-B", "KXM-E1", "KXM", "no"),
    ]
    d = write_dir(tmp_path, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    backtest.create_src(con)
    cells = backtest.cell_stats(con, "src", ["stat", "side"], ["period", "cid", "bucket"])
    top = cells[
        (cells["stat"] == A)
        & (cells["period"] == -1)
        & (cells["cid"] == -1)
        & (cells["bucket"] == -1)
    ]
    assert top["events"].tolist() == [1]


@pytest.fixture
def planted(tmp_path):
    """Mentions: takers buy YES at 0.20 on events that resolve YES 10 % of the time.

    Weather: prices equal the true probability. Sports: a huge premium that must be excluded.
    Two events per series and day for 120 days in each period, settled the day they trade.
    """
    rng = np.random.default_rng(7)
    trades, markets, n = [], [], 0
    for first_day in ("2025-12-05", "2026-05-05"):
        base = us(f"{first_day}T00:00:00")
        for series, p_true, price_yes, price_no in (
            ("KXM", 0.10, 0.20, 0.18),
            ("KXW", 0.19, 0.19, 0.19),
            ("KXS", 0.01, 0.50, 0.49),
        ):
            for day in range(120):
                day_us = base + day * 86_400 * 1_000_000
                settled = datetime.fromtimestamp(day_us / 1e6 + 20 * 3600, timezone.utc)
                for e in range(2):
                    ev = f"{series}-{first_day}-{day}-{e}"
                    tk = f"{ev}-A"
                    res = "yes" if rng.random() < p_true else "no"
                    markets.append(
                        market(tk, ev, series, res, settled.strftime("%Y-%m-%dT%H:%M:%S"))
                    )
                    for k in range(15):
                        n += 1
                        ts = day_us + (e * 1000 + k) * 1_000_000
                        if rng.random() < 0.7:
                            trades.append((tk, f"t{n}", 5.0, price_yes, True, ts, False))
                            if rng.random() < 0.3:
                                n += 1
                                trades.append((tk, f"t{n}", 5.0, price_yes + 0.01, True, ts, False))
                        else:
                            trades.append((tk, f"t{n}", 5.0, price_no, False, ts, False))
    return write_dir(tmp_path, markets, trades), tmp_path / "reports"


def test_gate_finds_the_planted_premium_only(planted):
    data_dir, reports_dir = planted
    summary = backtest.run(data_dir, reports_dir, 0, write_gate=True)
    gate = json.loads((data_dir / "gate.json").read_text())
    assert gate["valid"], gate["invalid_reasons"]
    got = {(q["variant"], q["category"], q["side"], q["bucket"]) for q in gate["qualifying"]}
    assert ("PENNY", "Mentions", "short_yes", 1) in got
    assert ("JOIN", "Mentions", "short_yes", 1) in got
    assert not any(c == "Climate and Weather" for _, c, _, _ in got)
    assert not any(c == "Sports" for _, c, _, _ in got)
    assert not any(s == "long_yes" for _, _, s, _ in got)
    assert summary["pairs_tested"] == gate["pairs_tested"] > 0
    assert gate["prereg_sha256"] != "missing"
    cells = pd.read_csv(reports_dir / "backtest" / "primary" / "cells.csv")
    assert "Sports" not in set(cells["category"])
    assert set(cells["sample"]) == {"exploration", "confirmation", "all"}


def test_gate_is_written_once(planted):
    data_dir, reports_dir = planted
    backtest.run(data_dir, reports_dir, 0, write_gate=True)
    first = (data_dir / "gate.json").read_text()
    backtest.run(data_dir, reports_dir, 0, write_gate=True)
    assert (data_dir / "gate.json").read_text() == first


def test_empty_hours_invalidate_the_gate(planted):
    data_dir, reports_dir = planted
    counts = json.loads((data_dir / "hours_r0.json").read_text())
    for k in list(counts)[: len(counts) // 10]:  # 10 % of hours empty
        counts[k] = 0
    (data_dir / "hours_r0.json").write_text(json.dumps(counts))
    backtest.run(data_dir, reports_dir, 0, write_gate=True)
    gate = json.loads((data_dir / "gate.json").read_text())
    assert not gate["valid"] and gate["qualifying"] == [] and gate["pairs_tested"] == 0
    assert any("returned no trade" in r for r in gate["invalid_reasons"])


def test_a_missing_period_invalidates_the_gate(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [("KXM-E1-A", f"t{i}", 1.0, 0.30, True, t0 + i, False) for i in range(5)]
    d = write_dir(tmp_path, [market("KXM-E1-A", "KXM-E1", "KXM", "no")], trades)
    backtest.run(d, tmp_path / "reports", 0, write_gate=True)
    gate = json.loads((d / "gate.json").read_text())
    assert not gate["valid"] and any("periods" in r for r in gate["invalid_reasons"])


def test_holdout_check_reads_pooled_sample(planted):
    data_dir, reports_dir = planted
    backtest.run(data_dir, reports_dir, 0, write_gate=True)
    # reuse the same files as a fake holdout: every qualifying pair must be confirmed
    (data_dir / "trades_r1").symlink_to(data_dir / "trades_r0")
    (data_dir / "hours_r1.json").write_text((data_dir / "hours_r0.json").read_text())
    backtest.run(data_dir, reports_dir, 1, write_gate=False)
    gate = json.loads((data_dir / "gate.json").read_text())
    hc = backtest.holdout_check(reports_dir, gate, "r1")
    assert len(hc) == len(gate["qualifying"]) and not hc["contradicted"].any()


def test_sql_cells_match_the_pandas_reference(planted):
    """DuckDB roll-ups (periods, categories, buckets) against a direct pandas computation."""
    data_dir, _ = planted
    con = backtest.connect(data_dir / "work.duckdb")
    backtest.build_tables(con, data_dir, 0)
    backtest.create_src(con)
    keys = ["stat", "side", "period", "cid", "bucket"]
    sql = backtest.cell_stats(con, "src", ["stat", "side"], ["period", "cid", "bucket"])
    rows = con.execute("SELECT * FROM src").df().rename(columns={"cl": "cluster", "eid": "event"})
    rows["s"], rows["n"] = rows["w"] * rows["v"], 1
    frames = []
    for p_all in (False, True):
        for c_all in (False, True):
            for b_all in (False, True):
                r = rows.copy()
                if p_all:
                    r["period"] = -1
                if c_all:
                    r["cid"] = -1
                if b_all:
                    r["bucket"] = -1
                frames.append(r)
    ref = cluster_table(pd.concat(frames, ignore_index=True), keys)
    m = sql.merge(ref, on=keys, suffixes=("", "_ref"))
    assert len(m) == len(sql) == len(ref)
    for col in ("clusters", "events", "losing", "contracts", "rows", "mean_c", "se_c"):
        assert np.allclose(m[col], m[f"{col}_ref"], equal_nan=True), col
    assert np.allclose(m["t"], m["t_ref"], equal_nan=True)
