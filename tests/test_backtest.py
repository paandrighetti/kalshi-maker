"""The backtest on synthetic tapes whose answer is known by construction."""

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from kmaker import backtest
from kmaker.schema import MARKET_COLUMNS, TRADE_COLUMNS

ONE_CENT = json.dumps([{"start": "0", "end": "1", "step": "0.01"}])


def us(s: str) -> int:
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()) * 1_000_000


def write_dir(tmp_path, series, markets, trades):
    d = tmp_path / "data"
    (d / "markets").mkdir(parents=True)
    (d / "trades_r0").mkdir(parents=True)
    pd.DataFrame(series).to_parquet(d / "series.parquet", index=False)
    pd.DataFrame(markets, columns=MARKET_COLUMNS).to_parquet(
        d / "markets" / "part-00000.parquet", index=False
    )
    pd.DataFrame(trades, columns=TRADE_COLUMNS).to_parquet(
        d / "trades_r0" / "2026-01-01T00.parquet", index=False
    )
    return d


def src_sums(con, keys):
    backtest.create_src(con)
    k = ", ".join(keys)
    df = con.execute(f"SELECT {k}, sum(w * v) AS s, sum(w) AS w FROM src GROUP BY {k}").df()
    return df.set_index(keys)


def market(ticker, event, series, result, settled="2026-09-10T00:00:00"):
    return {
        "ticker": ticker,
        "event_ticker": event,
        "series": series,
        "status": "settled",
        "result": result,
        "close_us": None,
        "expected_expiration_us": None,
        "settlement_us": us(settled),
        "mve": False,
        "price_ranges": ONE_CENT,
    }


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


def test_hand_computed_statistics(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [
        # one taker order buying YES that sweeps two levels; market resolves NO
        ("KXM-E1-A", "t1", 4.0, 0.20, True, t0, False),
        ("KXM-E1-A", "t2", 6.0, 0.21, True, t0, False),
        # one taker order selling YES at a single level; market resolves NO
        ("KXM-E1-A", "t3", 3.0, 0.18, False, t0 + 5, False),
        # excluded: block trade, unsettled market, sports, outside the window
        ("KXM-E1-A", "t4", 50.0, 0.50, True, t0 + 9, True),
        ("KXM-E2-A", "t5", 50.0, 0.50, True, t0, False),
        ("KXS-E3-A", "t6", 50.0, 0.50, True, t0, False),
        ("KXM-E1-A", "t7", 50.0, 0.50, True, us("2026-09-10T00:00:00"), False),
    ]
    markets = [
        market("KXM-E1-A", "KXM-E1", "KXM", "no"),
        market("KXM-E2-A", "KXM-E2", "KXM", ""),
        market("KXS-E3-A", "KXS-E3", "KXS", "no"),
    ]
    d = write_dir(tmp_path, SERIES, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    counts = backtest.build_tables(con, d, 0)
    assert counts["trades"] == 7 and counts["prints_kept"] == 3
    assert counts["drop_block"] == 1 and counts["drop_result"] == 1
    rows = src_sums(con, ["stat", "side"])
    # A, short_yes: (4 x 0.20 + 6 x 0.21) / 10 = 0.206 per contract
    a = rows.loc[("A", "short_yes")]
    assert np.isclose(a["s"] / a["w"], 0.206) and a["w"] == 10
    # C keeps only the emptied level at 0.20
    c = rows.loc[("C", "short_yes")]
    assert np.isclose(c["s"] / c["w"], 0.20) and c["w"] == 4
    # B: q = min(10, 10) at 0.20 - 0.01 = 0.19, the maker keeps 0.19 when NO wins
    b = rows.loc[("B", "short_yes")]
    assert np.isclose(b["s"] / b["w"], 0.19) and b["w"] == 10
    # the seller of YES at 0.18: the maker bought YES; NO wins, A = -0.18, B at 0.19 = -0.19
    assert np.isclose(rows.loc[("A", "long_yes")]["s"] / 3, -0.18)
    assert np.isclose(rows.loc[("B", "long_yes")]["s"] / 3, -0.19)
    assert ("C", "long_yes") not in rows.index  # single-level order: its last level is unknown


def test_maker_fee_enters_b_rounded_per_fill(tmp_path):
    t0 = us("2026-01-05T12:00:00")
    trades = [("KXW-E1-A", "t1", 10.0, 0.50, True, t0, False)]
    markets = [market("KXW-E1-A", "KXW-E1", "KXW", "no")]
    d = write_dir(tmp_path, SERIES, markets, trades)
    con = backtest.connect(d / "work.duckdb")
    backtest.build_tables(con, d, 0)
    rows = src_sums(con, ["stat"])
    # A: 0.50 - 0.0175 x 0.25 = 0.495625 per contract, unrounded
    assert np.isclose(rows.loc["A", "s"] / rows.loc["A", "w"], 0.50 - 0.0175 * 0.25)
    # B: a = 0.49, fee = ceil(0.0175 x 10 x 0.49 x 0.51 x 100) / 100 = 0.05 for 10 contracts
    assert np.isclose(rows.loc["B", "s"] / rows.loc["B", "w"], 0.49 - 0.005)


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
    return write_dir(tmp_path, SERIES, markets, trades), tmp_path / "reports"


def test_gate_finds_the_planted_premium_only(planted):
    data_dir, reports_dir = planted
    summary = backtest.run(data_dir, reports_dir, 0, write_gate=True)
    gate = json.loads((data_dir / "gate.json").read_text())
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


def test_holdout_check_reads_pooled_sample(planted):
    data_dir, reports_dir = planted
    backtest.run(data_dir, reports_dir, 0, write_gate=True)
    # reuse the same files as a fake holdout: every qualifying pair must be confirmed
    (data_dir / "trades_r1").symlink_to(data_dir / "trades_r0")
    backtest.run(data_dir, reports_dir, 1, write_gate=False)
    gate = json.loads((data_dir / "gate.json").read_text())
    hc = backtest.holdout_check(reports_dir, gate, "r1")
    assert len(hc) == len(gate["qualifying"]) and not hc["contradicted"].any()


def test_sql_cells_match_the_pandas_reference(planted):
    """DuckDB roll-ups (samples, categories, buckets) against a direct pandas computation."""
    from kmaker.stats import cluster_table

    data_dir, _ = planted
    con = backtest.connect(data_dir / "work.duckdb")
    backtest.build_tables(con, data_dir, 0)
    backtest.create_src(con)
    sql = backtest.cell_stats(con, "src", ["stat", "side"], ["sample", "category", "bucket"])
    rows = con.execute("SELECT * FROM src").df().rename(columns={"cl": "cluster"})
    rows["s"], rows["n"] = rows["w"] * rows["v"], 1
    frames = []
    for s_all in (False, True):
        for c_all in (False, True):
            for b_all in (False, True):
                r = rows.copy()
                if s_all:
                    r["sample"] = "all"
                if c_all:
                    r["category"] = "ALL"
                if b_all:
                    r["bucket"] = -1
                frames.append(r)
    ref = cluster_table(
        pd.concat(frames, ignore_index=True), ["stat", "side", "sample", "category", "bucket"]
    )
    keys = ["stat", "side", "sample", "category", "bucket"]
    m = sql.merge(ref, on=keys, suffixes=("", "_ref"))
    assert len(m) == len(sql) == len(ref)
    for col in ("clusters", "events", "losing", "contracts", "rows", "mean_c", "se_c"):
        assert np.allclose(m[col], m[f"{col}_ref"], equal_nan=True), col
    assert np.allclose(m["t"], m["t_ref"], equal_nan=True)
