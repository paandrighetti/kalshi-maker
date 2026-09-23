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
    cells = pd.read_csv(base / "cells.csv")
    overall = pd.read_csv(base / "overall.csv")
    volume = pd.read_csv(base / "volume.csv")
    gate = json.loads((data_dir / "gate.json").read_text())
    edges = PREREG.buckets
    out = [
        "# Backtest: the retail-flow premium for a small Kalshi maker",
        "",
        f"Generated {summary['generated_at']} from `reports/backtest/primary/`. "
        f"Pre-registration SHA-256 `{summary['prereg_sha256']}`.",
        "",
        "## Verdict",
        "",
    ]
    q = gate["qualifying"]
    if q:
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
        "## Sample",
        "",
        md_table(pd.DataFrame([summary["counts"]])),
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
    out += ["", "## Every cell (statistics B and C decide PENNY and JOIN)", ""]
    c = cells[cells["sample"].isin(["exploration", "confirmation"])].copy()
    c["bucket"] = c["bucket"].map(lambda b: bucket_label(int(b), edges))
    out += [md_table(c, {"mean_c": 3, "se_c": 3, "t": 2, "contracts": 0, "rows": 0})]
    hold = reports_dir / "backtest" / f"r{PREREG.holdout_residue}" / "cells.csv"
    if hold.exists() and q:
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


def load_forward(db_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    db = sqlite3.connect(db_path)
    fills = pd.read_sql_query("SELECT * FROM fills ORDER BY ts_us, id", db)
    cycles = pd.read_sql_query("SELECT * FROM cycles", db)
    settle = pd.read_sql_query("SELECT * FROM settlements", db)
    db.close()
    fills = fills.merge(settle[["ticker", "result", "settled_us"]], on="ticker", how="left")
    return fills, cycles


def with_pnl(fills: pd.DataFrame) -> pd.DataFrame:
    f = fills.copy()
    settled = f["result"].isin(["yes", "no"])
    o = (f["result"] == "yes").astype(float)
    d = f["side"].map(SIDE_SIGN)
    fee = [maker_fee(r, q, p) for r, q, p in zip(f["fee_rate"], f["qty"], f["price"], strict=True)]
    f["pnl"] = np.where(settled, f["qty"] * (d * (o - f["price"])) - np.array(fee), np.nan)
    f["risk_pc"] = np.where(f["side"] == "long_yes", f["price"], 1.0 - f["price"])
    f["settled"] = settled
    # clusters as in the backtest: category and UTC settlement date (trade date if unknown)
    when = pd.to_datetime(f["settled_us"].fillna(f["ts_us"]).astype("int64"), unit="us", utc=True)
    f["cluster"] = f["category"].astype(str) + "|" + when.dt.strftime("%Y-%m-%d")
    return f


def strategy_view(f: pd.DataFrame, qualifying: list[dict]) -> pd.DataFrame:
    """Fills kept under the pre-registered position limits, applied in time order per variant."""
    cells = {(q["variant"], q["category"], q["side"], int(q["bucket"])) for q in qualifying}
    keep_rows = []
    for variant, g in f.sort_values(["ts_us", "id"]).groupby("variant", sort=False):
        per_market: dict[str, float] = {}
        per_event: dict[str, float] = {}
        open_heap: list[tuple[float, float, str]] = []
        open_risk = 0.0
        for _, r in g.iterrows():
            b = int(r["bucket"])
            if (variant, r["category"], r["side"], b) not in cells and (
                variant,
                "ALL",
                r["side"],
                b,
            ) not in cells:
                continue
            while open_heap and open_heap[0][0] <= r["ts_us"]:
                end, risk, ev = heapq.heappop(open_heap)
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
            end = r["settled_us"] if pd.notna(r["settled_us"]) else float("inf")
            heapq.heappush(open_heap, (end, risk, r["event"]))
            row = r.copy()
            scale = qty / r["qty"]
            row["qty"] = qty
            row["pnl"] = r["pnl"] * scale if pd.notna(r["pnl"]) else np.nan
            keep_rows.append(row)
    return pd.DataFrame(keep_rows)


def forward_status(settled: pd.DataFrame, first_fill_us: int, now_us: int) -> str:
    if settled.empty:
        return "running, nothing settled"
    rows = settled.assign(s=settled["pnl"], w=settled["qty"], n=1, k=0)
    t = cluster_table(rows, ["k"]).iloc[0]
    days = (now_us - first_fill_us) / 86_400e6
    if (
        t["events"] >= PREREG.success_min_events
        and t["losing"] >= PREREG.min_losing_clusters
        and t["mean_c"] > 0
        and t["t"] >= PREREG.min_t
    ):
        return "success criterion met"
    if days >= 30 and t["mean_c"] < 0:
        return "abandon criterion met"
    return "running"


def forward_report(data_dir: Path) -> tuple[str, str]:
    db_path = data_dir / "paper.sqlite"
    gate = json.loads((data_dir / "gate.json").read_text())
    now = datetime.now(timezone.utc)
    head = [
        "# Forward paper maker",
        "",
        f"Generated {now.isoformat(timespec='seconds')}. Pre-registration SHA-256 "
        f"`{prereg_sha256()}`; gate of {gate['generated_at']} with "
        f"{len(gate['qualifying'])} qualifying pairs.",
        "",
    ]
    if not db_path.exists() or not gate["qualifying"]:
        text = "\n".join(head + ["No qualifying pair, nothing is quoted."]) + "\n"
        return text, "kalshi-maker: no qualifying pair, the paper maker is idle."
    fills, cycles = load_forward(db_path)
    if fills.empty:
        text = "\n".join(head + ["No fill yet."]) + "\n"
        return text, "kalshi-maker: running, no fill yet."
    f = with_pnl(fills)
    now_us = int(now.timestamp() * 1e6)
    out = list(head)
    digest = ["kalshi-maker forward"]
    for variant in sorted(f["variant"].unique()):
        sv = strategy_view(f[f["variant"] == variant], gate["qualifying"])
        settled = sv[sv["settled"]] if not sv.empty else sv
        status = forward_status(settled, int(f["ts_us"].min()), now_us)
        out += [f"## {variant}", "", f"Status: {status}.", ""]
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
            digest.append(f"{variant}: nothing settled yet")
        open_ = sv[~sv["settled"]] if not sv.empty else sv
        if not open_.empty:
            out += [
                f"Open: {len(open_)} fills, {float((open_['qty'] * open_['risk_pc']).sum()):.2f}"
                " USD at risk.",
                "",
            ]
        mech = (
            f[f["variant"] == variant]
            .groupby(["via", "improved"])
            .agg(
                fills=("qty", "size"),
                contracts=("qty", "sum"),
                mean_queue_ahead=("queue_ahead", "mean"),
            )
        )
        out += [
            "Fill mechanics (all fills, before limits):",
            "",
            md_table(mech.reset_index(), {"mean_queue_ahead": 1, "contracts": 0}),
            "",
        ]
    if not cycles.empty:
        d = cycles["duration_s"]
        out += [
            "## Cycles",
            "",
            f"{len(cycles)} cycles; duration median {d.median():.1f} s, 95th percentile "
            f"{d.quantile(0.95):.1f} s; median {cycles['active'].median():.0f} active markets, "
            f"{cycles['orders'].median():.0f} live quotes, {cycles['requests'].median():.0f} "
            "requests per cycle.",
            "",
        ]
    return "\n".join(out) + "\n", "\n".join(digest)
