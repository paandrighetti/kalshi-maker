"""Reports generated from outputs only: the backtest verdict and the daily forward results.

No number in a report is typed by hand. The backtest report reads `reports/backtest/*/` and
`gate.json`; the forward report reads `paper.sqlite`. Both print the SHA-256 of
PREREGISTRATION.md so a reader can check which rules produced them.
"""

from __future__ import annotations

import heapq
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PREREG, prereg_sha256
from .schema import bucket_label, maker_fee
from .stats import cluster_table

SIDE_SIGN = {"short_yes": -1.0, "long_yes": 1.0}


def _fmt(x: float, nd: int = 2) -> str:
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def md_table(df: pd.DataFrame, floats: dict[str, int] | None = None) -> str:
    floats = floats or {}
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in floats:
                cells.append(_fmt(float(v), floats[c]))
            elif isinstance(v, float) and v.is_integer():
                cells.append(f"{int(v):,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# backtest --------------------------------------------------------------------------------------


def backtest_report(reports_dir: Path, data_dir: Path) -> str:
    base = reports_dir / "backtest" / "primary"
    summary = json.loads((base / "summary.json").read_text())
    gate_path = data_dir / "gate.json"
    gate = json.loads(gate_path.read_text()) if gate_path.exists() else None
    checks = summary.get("validity", {})
    edges = PREREG.buckets
    out = [
        "# Backtest: the retail-flow premium for a small Kalshi maker",
        "",
        f"Generated {summary.get('generated_at', 'n/a')} from `reports/backtest/primary/`. "
        f"Pre-registration SHA-256 `{summary.get('prereg_sha256', prereg_sha256())}`.",
        "",
        "## Verdict",
        "",
    ]
    if gate is None:
        out.append(
            "Pending: the data failed the pre-registered checks ("
            + "; ".join(checks.get("reasons", []))
            + "). The empty hours and the non-final markets are downloaded again every day, "
            "and the gate is written after at most 7 days (Amendment 3)."
        )
    elif not gate.get("valid", True):
        out.append(
            "No conclusion: the data failed the pre-registered validity checks ("
            + "; ".join(gate.get("invalid_reasons", []))
            + "). No pair was tested and the paper maker does not quote."
        )
    elif gate["qualifying"]:
        q = gate["qualifying"]
        out.append(
            f"{len(q)} of {gate['pairs_tested']} pre-registered (variant, cell) pairs qualify: "
            "positive with t >= 2 in both the exploration and the confirmation samples."
        )
        tbl = pd.DataFrame(q)
        tbl["bucket"] = tbl["bucket"].map(lambda b: bucket_label(int(b), edges))
        out += ["", md_table(tbl), ""]
    else:
        out.append(
            f"None of the {gate['pairs_tested']} pre-registered (variant, cell) pairs qualifies. "
            "A small maker has no demonstrated edge on Kalshi's non-sports markets in this sample, "
            "and the paper maker does not quote."
        )
    if "counts" not in summary:  # nothing was computed: no data yet
        return "\n".join(out) + "\n"
    cells = pd.read_csv(base / "cells.csv")
    overall = pd.read_csv(base / "overall.csv")
    volume = pd.read_csv(base / "volume.csv")
    rep = summary["replication_A_pooled"]
    out += [
        "",
        "## Replication of the published maker premium (statistic A, all categories pooled)",
        "",
        md_table(
            pd.DataFrame(
                [
                    {
                        "sample": k,
                        "mean, cents per contract": v["mean_c"],
                        "t, maker short YES": v["t_by_side"].get("short_yes", float("nan")),
                        "t, maker long YES": v["t_by_side"].get("long_yes", float("nan")),
                    }
                    for k, v in rep.items()
                ]
            ),
            {"mean, cents per contract": 3, "t, maker short YES": 2, "t, maker long YES": 2},
        ),
        "",
        "Replication check failed: the data handling must be audited before use."
        if summary["replication_fails"]
        else "The pooled maker premium does not contradict the literature on this sample.",
        "",
        "## Sample and validity checks",
        "",
        f"Sampled hours: {checks.get('hours', 'n/a')}; empty "
        f"{checks.get('empty_hour_share', float('nan')):.2%} (limit "
        f"{PREREG.max_empty_hour_share:.0%}); trades without a market record "
        f"{checks.get('unmatched_share', float('nan')):.2%} (limit "
        f"{PREREG.max_unmatched_share:.0%}); eligible trades in non-final markets "
        f"{checks.get('unsettled_share', float('nan')):.2%} (limit "
        f"{PREREG.max_unsettled_share:.0%}). Markets settled more than a day after their latest "
        f"expiration, which would reveal a moved field: "
        f"{summary['counts'].get('markets_settled_after_latest_expiration', 0)}.",
        "",
        md_table(pd.DataFrame(sorted(summary["counts"].items()), columns=["count", "value"])),
        "",
        md_table(volume, {"taker_yes_share": 3}),
        "",
        "## By category and side, all buckets (cents per contract)",
        "",
    ]
    ov = overall[overall["sample"].isin(["exploration", "confirmation"])].copy()
    ov = ov.pivot_table(
        index=["stat", "category", "side"], columns="sample", values=["mean_c", "t", "events"]
    )
    ov.columns = [f"{a}_{b}" for a, b in ov.columns]
    out += [md_table(ov.reset_index(), {c: 2 for c in ov.columns if not c.startswith("events")})]
    out += [
        "",
        "## Every cell (statistics B and C decide PENNY and JOIN)",
        "",
        "`rows` counts price levels of taker orders for A and C, and taker orders for B.",
        "",
    ]
    c = cells[cells["sample"].isin(["exploration", "confirmation"])].copy()
    c["bucket"] = c["bucket"].map(lambda b: bucket_label(int(b), edges))
    out += [md_table(c, {"mean_c": 3, "se_c": 3, "t": 2, "contracts": 0, "rows": 0})]
    hold = reports_dir / "backtest" / f"r{PREREG.holdout_residue}" / "cells.csv"
    if hold.exists() and gate and gate["qualifying"]:
        from .backtest import holdout_check

        hc = holdout_check(reports_dir, gate, f"r{PREREG.holdout_residue}")
        hc["bucket"] = hc["bucket"].map(lambda b: bucket_label(int(b), edges))
        out += [
            "",
            "## Holdout hours (reported, not used to decide)",
            "",
            md_table(hc, {"holdout_mean_c": 3, "holdout_t": 2}),
        ]
    return "\n".join(out) + "\n"


# forward ---------------------------------------------------------------------------------------


def load_forward(db_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict | None]:
    db = sqlite3.connect(db_path)
    fills = pd.read_sql_query("SELECT * FROM fills ORDER BY ts_us, id", db)
    cycles = pd.read_sql_query("SELECT * FROM cycles", db)
    settle = pd.read_sql_query("SELECT ticker, result, settled_us FROM settlements", db)
    meta = dict(db.execute("SELECT k, v FROM meta").fetchall())
    moved = db.execute("SELECT count(DISTINCT ticker) FROM field_changes").fetchone()[0]
    db.close()
    fills = fills.merge(settle, on="ticker", how="left")
    traded_gate = json.loads(meta["gate"]) if "gate" in meta else None
    if traded_gate is not None:
        traded_gate["_moved_latest_expiration"] = int(moved)
    return fills, cycles, traded_gate


def with_pnl(fills: pd.DataFrame) -> pd.DataFrame:
    """Settlement profit per fill. A final result other than yes or no (a void or a scalar
    settlement) ends the position without a binary payoff: it is closed and excluded from PnL."""
    f = fills.copy()
    closed = f["result"].notna() & (f["result"].astype(str) != "")
    settled = f["result"].isin(["yes", "no"])
    o = (f["result"] == "yes").astype(float)
    d = f["side"].map(SIDE_SIGN)
    fee = [maker_fee(r, q, p) for r, q, p in zip(f["fee_rate"], f["qty"], f["price"], strict=True)]
    f["pnl"] = np.where(settled, f["qty"] * (d * (o - f["price"])) - np.array(fee), np.nan)
    f["risk_pc"] = np.where(f["side"] == "long_yes", f["price"], 1.0 - f["price"])
    f["settled"] = settled
    f["closed"] = closed
    # clusters as in the backtest: category and UTC settlement date (trade date if unknown)
    when = pd.to_datetime(f["settled_us"].fillna(f["ts_us"]).astype("int64"), unit="us", utc=True)
    f["cluster"] = f["category"].astype(str) + "|" + when.dt.strftime("%Y-%m-%d")
    return f


def strategy_view(f: pd.DataFrame, qualifying: list[dict]) -> pd.DataFrame:
    """Fills kept under the pre-registered position limits, applied in time order per variant.

    Risk is released when a market closes (settled, void or scalar). A fill cut by a limit keeps
    its price, and its fee is recomputed for the contracts kept.
    """
    cells = {(q["variant"], q["category"], q["side"], int(q["bucket"])) for q in qualifying}
    keep_rows = []
    for variant, g in f.sort_values(["ts_us", "id"]).groupby("variant", sort=False):
        per_market: dict[str, float] = {}
        per_event: dict[str, float] = {}
        open_heap: list[tuple[float, float, str]] = []
        open_risk = 0.0
        for _, r in g.iterrows():
            b = int(r["bucket"])
            in_gate = (variant, r["category"], r["side"], b) in cells
            if not in_gate and (variant, "ALL", r["side"], b) not in cells:
                continue
            while open_heap and open_heap[0][0] <= r["ts_us"]:
                _end, risk, ev = heapq.heappop(open_heap)
                open_risk -= risk
                per_event[ev] = per_event.get(ev, 0.0) - risk
            room_m = PREREG.max_contracts_per_market - per_market.get(r["ticker"], 0.0)
            room_e = (PREREG.max_risk_per_event - per_event.get(r["event"], 0.0)) / r["risk_pc"]
            room_t = (PREREG.max_risk_total - open_risk) / r["risk_pc"]
            qty = max(0.0, min(r["qty"], room_m, room_e, room_t))
            if qty <= 1e-9:
                continue
            risk = qty * r["risk_pc"]
            per_market[r["ticker"]] = per_market.get(r["ticker"], 0.0) + qty
            per_event[r["event"]] = per_event.get(r["event"], 0.0) + risk
            open_risk += risk
            end = r["settled_us"] if r["closed"] and pd.notna(r["settled_us"]) else float("inf")
            heapq.heappush(open_heap, (end, risk, r["event"]))
            row = r.copy()
            row["qty"] = qty
            if r["settled"]:
                o = 1.0 if r["result"] == "yes" else 0.0
                gross = qty * SIDE_SIGN[r["side"]] * (o - r["price"])
                row["pnl"] = gross - maker_fee(r["fee_rate"], qty, r["price"])
            keep_rows.append(row)
    return pd.DataFrame(keep_rows)


STATUS_FILE = "forward_status.json"


def _finite(x: float) -> float | None:
    return float(x) if np.isfinite(x) else None


def _variant_stats(settled: pd.DataFrame) -> dict:
    if settled.empty:
        return {"events": 0, "losing": 0, "mean_c": None, "t": None}
    rows = settled.assign(s=settled["pnl"], w=settled["qty"], n=1, k=0)
    r = cluster_table(rows, ["k"]).iloc[0]
    return {
        "events": int(r["events"]),
        "losing": int(r["losing"]),
        "mean_c": _finite(r["mean_c"]),
        "t": _finite(r["t"]),
    }


def _status_text(rec: dict, st: dict, days: float) -> str:
    f = rec["final"]
    if f and f["status"] == "abandoned":
        return f"ABANDONED on {f['date']}: mean {_fmt(f['mean_c'])} c/ct on day {f['day']:.0f}"
    if f:
        word = "SUCCESS" if f["status"] == "success" else "INCONCLUSIVE"
        return (
            f"{word} at look {f['look']} on {f['date']}: {f['events']} events, "
            f"{f['losing']} losing clusters, t {_fmt(f['t'])} (threshold {PREREG.forward_look_t})"
        )
    head = f"running, day {days:.0f} of {PREREG.forward_final_day:.0f}"
    if rec["looks"]:
        lk = rec["looks"][0]
        return (
            f"{head}; look 1 on {lk['date']} not met (mean {_fmt(lk['mean_c'])} c/ct, "
            f"t {_fmt(lk['t'])}), final look on day {PREREG.forward_final_day:.0f}"
        )
    return (
        f"{head}; look 1 at {PREREG.success_min_events} events and "
        f"{PREREG.min_losing_clusters} losing clusters (now {st['events']} and {st['losing']})"
    )


def forward_status(
    settled: pd.DataFrame, first_fill_us: int, now_us: int, record: dict | None = None
) -> tuple[str, dict]:
    """Status of one variant under Amendment 4, and its record of looks and final status.

    Success is checked at two looks only: the first report where the minimums hold (200 settled
    events and 10 negative clusters) before day 60, and the first report on or after day 60.
    Each look needs a positive mean and t >= 2.28. A mean below zero in a report on or after
    day 30 abandons the variant. A final status is kept once reached: `record` is what
    `data/forward_status.json` holds for the variant, and a final one is returned unchanged.
    """
    rec = {"looks": list((record or {}).get("looks", [])), "final": (record or {}).get("final")}
    days = (now_us - first_fill_us) / 86_400e6
    if rec["final"]:
        return _status_text(rec, {}, days), rec
    st = _variant_stats(settled)
    minimums = (
        st["events"] >= PREREG.success_min_events and st["losing"] >= PREREG.min_losing_clusters
    )
    met = bool(
        minimums
        and st["mean_c"] is not None
        and st["mean_c"] > 0
        and st["t"] is not None
        and st["t"] >= PREREG.forward_look_t
    )
    date = datetime.fromtimestamp(now_us / 1e6, timezone.utc).strftime("%Y-%m-%d")
    entry = {"date": date, "day": round(days, 1), **st, "met": met}
    if days >= PREREG.forward_abandon_day and st["mean_c"] is not None and st["mean_c"] < 0:
        rec["final"] = {"status": "abandoned", **entry}
    elif days >= PREREG.forward_final_day:
        rec["looks"].append({"look": 2, **entry})
        rec["final"] = {"status": "success" if met else "inconclusive", "look": 2, **entry}
    elif minimums and not rec["looks"]:
        rec["looks"].append({"look": 1, **entry})
        if met:
            rec["final"] = {"status": "success", "look": 1, **entry}
    return _status_text(rec, st, days), rec


def _health(cycles: pd.DataFrame, traded_gate: dict | None) -> str:
    """Operating state for the digest: failed stages, last cycle, moved listing fields."""
    moved = (traded_gate or {}).get("_moved_latest_expiration", 0)
    if cycles.empty:
        return f"no cycle recorded yet; markets with a moved latest expiration: {moved}"
    now_us = datetime.now(timezone.utc).timestamp() * 1e6
    day = cycles[cycles["ts_us"] > now_us - 86_400e6]
    failed = int((day["errors"].fillna("") != "").sum())
    last_min = (now_us - cycles["ts_us"].max()) / 60e6
    return (
        f"last cycle {last_min:.0f} min ago; {failed} of {len(day)} cycles in 24 h with a failed "
        f"stage; markets with a moved latest expiration: {moved}"
    )


def _idle_reason(gate: dict) -> str | None:
    if not gate.get("valid", True):
        return "the data failed the validity checks (" + "; ".join(gate["invalid_reasons"]) + ")"
    if gate.get("replication_fails"):
        return "the replication check failed; the data handling must be audited"
    if not gate["qualifying"]:
        return "no pre-registered pair qualified"
    return None


def forward_report(data_dir: Path) -> tuple[str, str]:
    db_path = data_dir / "paper.sqlite"
    gate = json.loads((data_dir / "gate.json").read_text())
    now = datetime.now(timezone.utc)
    head = [
        "# Forward paper maker",
        "",
        f"Generated {now.isoformat(timespec='seconds')}. Pre-registration SHA-256 "
        f"`{prereg_sha256()}`; gate of {gate['generated_at']}, written under "
        f"`{gate.get('prereg_sha256', 'n/a')}`, with {len(gate['qualifying'])} qualifying pairs.",
        "",
    ]
    idle = _idle_reason(gate)
    if idle:
        text = "\n".join(head + [f"The paper maker does not quote: {idle}."]) + "\n"
        return text, f"kalshi-maker: idle, {idle}."
    if not db_path.exists():
        text = "\n".join(head + ["The paper maker has not started yet."]) + "\n"
        return text, "kalshi-maker: the paper maker has not started yet."
    fills, cycles, traded_gate = load_forward(db_path)
    health = _health(cycles, traded_gate)
    if traded_gate is not None and traded_gate.get("generated_at") != gate["generated_at"]:
        head += [
            "Warning: gate.json differs from the gate the paper maker trades; the report "
            "uses the traded one.",
            "",
        ]
        gate = traded_gate
    if fills.empty:
        text = "\n".join(head + ["No fill yet.", "", health]) + "\n"
        return text, "kalshi-maker: running, no fill yet.\n" + health
    f = with_pnl(fills)
    now_us = int(now.timestamp() * 1e6)
    out = list(head)
    digest = ["kalshi-maker forward", health]
    status_path = data_dir / STATUS_FILE
    records = json.loads(status_path.read_text()) if status_path.exists() else {}
    changed = False
    for variant in sorted(f["variant"].unique()):
        fv = f[f["variant"] == variant]
        sv = strategy_view(fv, gate["qualifying"])
        settled = sv[sv["settled"]] if not sv.empty else sv
        old = records.get(variant, {"looks": [], "final": None})
        status, rec = forward_status(settled, int(fv["ts_us"].min()), now_us, old)
        if rec != old:
            records[variant], changed = rec, True
        out += [f"## {variant}", "", f"Status: {status}.", ""]
        if rec["looks"]:
            looks = pd.DataFrame(rec["looks"]).astype({"mean_c": float, "t": float})
            out += [md_table(looks, {"mean_c": 3, "t": 2}), ""]
        if not settled.empty:
            rows = settled.assign(s=settled["pnl"], w=settled["qty"], n=1)
            by = cluster_table(rows.assign(k="all"), ["k"])
            cell = cluster_table(rows, ["category", "side", "bucket"])
            cell["bucket"] = cell["bucket"].map(lambda b: bucket_label(int(b), PREREG.buckets))
            pnl = float(settled["pnl"].sum())
            out += [
                f"Settled: {int(by['events'].iloc[0])} events in {int(by['clusters'].iloc[0])} "
                f"clusters ({int(by['losing'].iloc[0])} negative), "
                f"{by['contracts'].iloc[0]:.0f} contracts, "
                f"{_fmt(float(by['mean_c'].iloc[0]), 3)} cents per contract "
                f"(t = {_fmt(float(by['t'].iloc[0]))}), PnL {pnl:.2f} USD.",
                "",
                md_table(cell, {"mean_c": 3, "se_c": 3, "t": 2, "contracts": 0, "rows": 0}),
                "",
            ]
            digest.append(
                f"{variant}: {int(by['events'].iloc[0])} ev, "
                f"{_fmt(float(by['mean_c'].iloc[0]), 2)} c/ct, t {_fmt(float(by['t'].iloc[0]))}, "
                f"PnL {pnl:.2f} USD, {status}"
            )
        else:
            digest.append(f"{variant}: nothing settled yet; {status}")
        open_ = sv[~sv["closed"]] if not sv.empty else sv
        if not open_.empty:
            out += [
                f"Open: {len(open_)} fills, {float((open_['qty'] * open_['risk_pc']).sum()):.2f}"
                " USD at risk.",
                "",
            ]
        mech = fv.groupby(["via", "improved"]).agg(
            fills=("qty", "size"),
            contracts=("qty", "sum"),
            mean_queue_ahead=("queue_ahead", "mean"),
        )
        out += [
            "Fill mechanics (all fills, before limits):",
            "",
            md_table(mech.reset_index(), {"mean_queue_ahead": 1, "contracts": 0}),
            "",
        ]
    if not cycles.empty:
        d = cycles["duration_s"]
        errs = int((cycles["errors"].fillna("") != "").sum())
        out += [
            "## Cycles",
            "",
            f"{len(cycles)} cycles; duration median {d.median():.1f} s, 95th percentile "
            f"{d.quantile(0.95):.1f} s; median {cycles['active'].median():.0f} active markets, "
            f"{cycles['orders'].median():.0f} live quotes, {cycles['requests'].median():.0f} "
            f"requests per cycle; median age of the newest trade at poll "
            f"{cycles['trade_lag_s'].median():.1f} s; {errs} cycles with a failed stage.",
            "",
        ]
    if changed:  # a look or a final status is added once and never changed afterwards
        tmp = status_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(records, indent=2))
        tmp.replace(status_path)
    return "\n".join(out) + "\n", "\n".join(digest)
