"""Statistics A, B and C of PREREGISTRATION.md on the downloaded sample, and the gate.

Every decision uses only what was known when a trade printed: its market, category, price,
size and the direction of the taker. Markets are selected, and assigned to a period, on
`latest_expiration_time`, fixed at listing. The outcome enters only as the settlement value of
the maker's position, and the settlement date only as a cluster label.

All per-print work happens in a DuckDB file on disk with a memory cap. Strings are replaced by
integer codes before any large aggregation, and taker orders are built with aggregations and
joins rather than window functions, so that the work spills to disk instead of failing when the
sample is larger than memory. pandas only sees one row per cell.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from .config import PREREG, prereg_sha256
from .ingest import hour_counts, hour_key, sampled_hours
from .stats import OUT_COLUMNS, SAMPLES, VARIANT_STAT, decide, finish

log = logging.getLogger(__name__)

HORIZON_EDGES = (0.0, 1.0, 6.0, 24.0, 168.0)
CELL_KEYS = ["stat", "sample", "category", "side", "bucket"]
STAT_LABEL = {0: "A", 1: "B", 2: "C"}
SIDE_LABEL = {0: "short_yes", 1: "long_yes"}
PERIOD_LABEL = {0: "exploration", 1: "confirmation", -1: "all"}
CLUSTER_DAYS = 100_000  # cluster code = category code x CLUSTER_DAYS + UTC day number


def _us(dt: datetime) -> int:
    return int(dt.timestamp()) * 1_000_000


def _bucket_sql(col: str) -> str:
    edges = PREREG.buckets
    parts = [f"WHEN {col} < {edges[i + 1]} THEN {i}" for i in range(len(edges) - 1)]
    return f"(CASE {' '.join(parts)} ELSE {len(edges) - 1} END)"


def _horizon_sql(col: str) -> str:
    e = HORIZON_EDGES
    parts = [f"WHEN {col} < {e[i + 1]} THEN {i}" for i in range(len(e) - 1)]
    return f"(CASE {' '.join(parts)} ELSE {len(e) - 1} END)"


def horizon_label(i: int) -> str:
    e = HORIZON_EDGES
    return f"{e[i]:g}-{e[i + 1]:g}h" if i + 1 < len(e) else f"{e[-1]:g}h+"


def connect(path: Path, memory_limit: str = "500MB") -> duckdb.DuckDBPyConnection:
    path.parent.mkdir(parents=True, exist_ok=True)
    for p in (path, path.with_suffix(path.suffix + ".wal")):
        p.unlink(missing_ok=True)
    tmp = path.parent / "duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute(f"SET memory_limit='{memory_limit}'")
    con.execute("SET threads=2")
    con.execute(f"SET temp_directory='{tmp}'")
    con.execute("SET preserve_insertion_order=false")
    con.execute("SET TimeZone='UTC'")
    return con


def build_tables(con: duckdb.DuckDBPyConnection, data_dir: Path, residue: int) -> dict:
    """Market codes (`mka`), price levels of taker orders (`lv`) and taker orders (`ord`)."""
    excluded = ", ".join(f"'{c}'" for c in PREREG.excluded_categories)
    finals = ", ".join(f"'{s}'" for s in PREREG.final_statuses)
    coef = PREREG.maker_fee_coef
    start, end = _us(PREREG.window_start), _us(PREREG.window_end)
    con.execute(
        f"CREATE OR REPLACE TABLE sr AS SELECT * FROM read_parquet('{data_dir}/series.parquet')"
    )
    # the latest record of each market: parts are numbered and a later part supersedes. The
    # latest part per ticker comes from a plain aggregation, then the record from a join, both
    # of which spill to disk; max_by would skip NULL fields and mix records of different parts
    rec = (
        "SELECT *, regexp_extract(filename, '(part-[0-9]+)[.]parquet$', 1) AS part "
        f"FROM read_parquet('{data_dir}/markets/*.parquet', filename = true)"
    )
    con.execute(
        f"CREATE OR REPLACE TABLE lp AS SELECT ticker, max(part) AS part FROM ({rec}) GROUP BY 1"
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE mk0 AS
        SELECT r.* EXCLUDE (filename) FROM ({rec}) r JOIN lp USING (ticker, part)
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE mka AS
        SELECT row_number() OVER (ORDER BY m.ticker) AS mid, m.ticker, m.part,
               dense_rank() OVER (ORDER BY m.event_ticker) AS eid,
               dense_rank() OVER (ORDER BY coalesce(s.category, '')) AS cid,
               coalesce(s.category, '') AS category, m.settlement_us,
               CASE WHEN m.result = 'yes' THEN 1.0 ELSE 0.0 END AS o,
               CASE WHEN s.fee_type = 'quadratic_with_maker_fees'
                    THEN {coef} * coalesce(s.fee_multiplier, 1.0) ELSE 0.0 END AS fee_rate,
               CAST(floor(m.settlement_us / 86400e6) AS BIGINT) AS sday,
               CASE WHEN m.latest_expiration_us < {_us(PREREG.split)} THEN 0 ELSE 1 END
                   AS period,
               m.settlement_us > m.latest_expiration_us + 86400e6 AS settled_late,
               CASE
                   WHEN s.series IS NULL THEN 'unknown_series'
                   WHEN s.category IN ({excluded}) THEN 'excluded_category'
                   WHEN m.mve THEN 'multivariate'
                   WHEN m.latest_expiration_us IS NULL
                        OR m.latest_expiration_us > {_us(PREREG.latest_expiration_cutoff)}
                        THEN 'late_expiration'
                   WHEN m.status NOT IN ({finals}) THEN 'not_final'
                   WHEN m.result NOT IN ('yes', 'no') THEN 'not_binary'
                   ELSE 'ok'
               END AS reason
        FROM mk0 m LEFT JOIN sr s ON s.series = m.series
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE rg AS
        SELECT a.mid, r.lo, r.hi, r.step
        FROM read_parquet('{data_dir}/ranges/*.parquet', filename = true) r
        JOIN mka a ON a.ticker = r.ticker
                  AND a.part = regexp_extract(r.filename, '(part-[0-9]+)[.]parquet$', 1)
        """
    )
    trades = f"{data_dir}/trades_r{residue}/*.parquet"
    con.execute(f"CREATE OR REPLACE VIEW tr AS SELECT * FROM read_parquet('{trades}')")
    reasons = con.execute(
        f"""
        SELECT CASE WHEN t.is_block THEN 'block'
                    WHEN t.created_us < {start} OR t.created_us >= {end} THEN 'outside_window'
                    WHEN t.yes_price <= 0 OR t.yes_price >= 1 OR t.count <= 0 THEN 'bad_trade'
                    WHEN a.mid IS NULL THEN 'no_market'
                    ELSE a.reason END AS reason,
               count(*) AS n
        FROM tr t LEFT JOIN mka a USING (ticker) GROUP BY 1
        """
    ).fetchall()
    counts = {f"trades_{k}": int(v) for k, v in reasons}
    counts["trades"] = sum(int(v) for _, v in reasons)
    con.execute(
        f"""
        CREATE OR REPLACE TABLE lv AS
        SELECT a.mid, t.created_us, t.taker_yes, t.yes_price AS p, sum(t.count) AS qty
        FROM tr t JOIN mka a USING (ticker)
        WHERE a.reason = 'ok' AND NOT t.is_block AND t.count > 0
          AND t.yes_price > 0 AND t.yes_price < 1
          AND t.created_us >= {start} AND t.created_us < {end}
        GROUP BY 1, 2, 3, 4
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE ord AS
        SELECT mid, created_us, taker_yes, count(*) AS nlv, sum(qty) AS oqty,
               CASE WHEN taker_yes THEN min(p) ELSE max(p) END AS best_p,
               CASE WHEN taker_yes THEN max(p) ELSE min(p) END AS last_p
        FROM lv GROUP BY 1, 2, 3
        """
    )

    def one(q: str) -> int:
        return int(con.execute(q).fetchone()[0])

    counts["levels"] = one("SELECT count(*) FROM lv")
    counts["orders"] = one("SELECT count(*) FROM ord")
    counts["events"] = one("SELECT count(DISTINCT eid) FROM mka WHERE mid IN (SELECT mid FROM lv)")
    counts["markets"] = one("SELECT count(DISTINCT mid) FROM lv")
    counts["markets_without_settlement_time"] = one(
        "SELECT count(*) FROM mka WHERE settlement_us IS NULL AND mid IN (SELECT mid FROM lv)"
    )
    counts["markets_settled_after_latest_expiration"] = one(
        "SELECT count(*) FROM mka WHERE settled_late AND mid IN (SELECT mid FROM lv)"
    )
    return counts


def create_src(con: duckdb.DuckDBPyConnection) -> None:
    """Rows of statistics A (0), B (1) and C (2): integer keys, event, cluster, weight, value."""
    cap = PREREG.penny_fill_cap
    side = "CASE WHEN taker_yes THEN 0 ELSE 1 END"
    d = "CASE WHEN taker_yes THEN -1.0 ELSE 1.0 END"

    def cl(t: str) -> str:
        day = f"coalesce(a.sday, CAST(floor({t}.created_us / 86400e6) AS BIGINT))"
        return f"a.cid * {CLUSTER_DAYS} + {day}"

    con.execute(
        f"""
        CREATE OR REPLACE VIEW src AS
        WITH b0 AS (
            SELECT o.*, CASE WHEN o.taker_yes THEN o.best_p - 1e-9 ELSE o.best_p END AS probe
            FROM ord o
        ), b1 AS (
            SELECT b0.*, coalesce(r.step, 0.01) AS tick
            FROM b0 LEFT JOIN rg r ON r.mid = b0.mid AND b0.probe >= r.lo AND b0.probe < r.hi
        ), b2 AS (
            SELECT *, round(CASE WHEN taker_yes THEN best_p - tick ELSE best_p + tick END, 6)
                      AS a_price,
                   least(oqty, {cap}) AS q
            FROM b1
        )
        SELECT 0 AS stat, a.period, a.cid, {side} AS side, {_bucket_sql("l.p")} AS bucket,
               a.eid, {cl("l")} AS cl, l.qty AS w,
               {d} * (a.o - l.p) - a.fee_rate * l.p * (1 - l.p) AS v
        FROM lv l JOIN mka a USING (mid)
        UNION ALL
        SELECT 2, a.period, a.cid, {side}, {_bucket_sql("l.p")}, a.eid, {cl("l")}, l.qty,
               {d} * (a.o - l.p) - a.fee_rate * l.p * (1 - l.p)
        FROM lv l
        JOIN (SELECT mid, created_us, taker_yes, last_p FROM ord WHERE nlv > 1) o
          USING (mid, created_us, taker_yes)
        JOIN mka a USING (mid)
        WHERE l.p <> o.last_p
        UNION ALL
        SELECT 1, a.period, a.cid, {side}, {_bucket_sql("b.a_price")}, a.eid, {cl("b")}, b.q,
               {d} * (a.o - b.a_price)
               - ceil(round(a.fee_rate * b.q * b.a_price * (1 - b.a_price) * 100, 9)) / 100 / b.q
        FROM b2 b JOIN mka a USING (mid)
        WHERE b.a_price > 0 AND b.a_price < 1
        """
    )


def cell_stats(
    con: duckdb.DuckDBPyConnection, src: str, fixed: list[str], cube: list[str]
) -> pd.DataFrame:
    """Per-cell clustered statistics, with every roll-up of the integer `cube` columns as -1."""
    keys = fixed + cube
    cube_sql = f", CUBE({', '.join(cube)})" if cube else ""
    sel = ", ".join(fixed + [f"coalesce({c}, -1) AS {c}" for c in cube])
    raw = ", ".join(keys)
    con.execute(
        f"""
        CREATE OR REPLACE TABLE g AS
        SELECT {sel}, cl, s, w, n FROM (
            SELECT {raw}, cl, sum(w * v) AS s, sum(w) AS w, count(*) AS n
            FROM {src} GROUP BY {", ".join(fixed + ["cl"])}{cube_sql}
        )
        """
    )
    # distinct events per cell, one roll-up at a time: two plain aggregations, which DuckDB
    # spills to disk, where count(DISTINCT) under CUBE ran out of memory on large samples
    con.execute(f"CREATE OR REPLACE TABLE evd AS SELECT DISTINCT {raw}, eid FROM {src}")
    parts = []
    for mask in range(2 ** len(cube)):
        cols = fixed + [c if mask >> i & 1 == 0 else f"-1 AS {c}" for i, c in enumerate(cube)]
        parts.append(
            f"SELECT {raw}, count(*) AS events FROM "
            f"(SELECT DISTINCT {', '.join(cols)}, eid FROM evd) GROUP BY {raw}"
        )
    con.execute(f"CREATE OR REPLACE TABLE ev AS {' UNION ALL '.join(parts)}")
    tk = ", ".join("t." + c for c in keys)
    on = " AND ".join(f"g.{c} = t.{c}" for c in keys)
    df = con.execute(
        f"""
        WITH t AS (
            SELECT {raw}, sum(s) / sum(w) AS m, sum(w) AS contracts, sum(n) AS rows,
                   count(*) AS clusters
            FROM g GROUP BY {raw}
        ), r AS (
            SELECT {tk}, any_value(t.m) AS m, any_value(t.contracts) AS contracts,
                   any_value(t.rows) AS rows, any_value(t.clusters) AS clusters,
                   sum((g.s - t.m * g.w) * (g.s - t.m * g.w)) AS e2,
                   sum(CASE WHEN g.s < 0 THEN 1 ELSE 0 END) AS losing
            FROM g JOIN t ON {on}
            GROUP BY {tk}
        )
        SELECT r.*, ev.events FROM r JOIN ev USING ({raw})
        """
    ).df()
    return finish(df)[keys + OUT_COLUMNS]


def _labels(con: duckdb.DuckDBPyConnection) -> dict[int, str]:
    rows = con.execute("SELECT DISTINCT cid, category FROM mka").fetchall()
    return {int(c): name for c, name in rows} | {-1: "ALL"}


def diagnostics(con: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    """Descriptive tables; none of them enters the decision."""
    out = {}
    out["volume"] = con.execute(
        """
        SELECT a.category, CASE WHEN a.period = 0 THEN 'exploration' ELSE 'confirmation' END
                   AS sample,
               count(DISTINCT a.eid) AS events, count(DISTINCT a.mid) AS markets,
               sum(l.qty) AS contracts,
               sum(CASE WHEN l.taker_yes THEN l.qty ELSE 0 END) / sum(l.qty) AS taker_yes_share
        FROM lv l JOIN mka a USING (mid) GROUP BY 1, 2 ORDER BY 1, 2
        """
    ).df()
    out["calibration"] = con.execute(
        """
        SELECT coalesce(category, 'ALL') AS category, decile_lo, contracts, mean_price, yes_rate
        FROM (
            SELECT a.category, least(floor(l.p * 10), 9) / 10 AS decile_lo,
                   sum(l.qty) AS contracts, sum(l.qty * l.p) / sum(l.qty) AS mean_price,
                   sum(l.qty * a.o) / sum(l.qty) AS yes_rate
            FROM lv l JOIN mka a USING (mid)
            GROUP BY GROUPING SETS ((a.category, decile_lo), (decile_lo))
        ) ORDER BY 1, 2
        """
    ).df()
    hours = "(a.settlement_us - l.created_us) / 3.6e9"
    con.execute(
        f"""
        CREATE OR REPLACE VIEW src_h AS
        SELECT {_horizon_sql(hours)} AS horizon, CASE WHEN l.taker_yes THEN 0 ELSE 1 END AS side,
               a.eid, a.cid * {CLUSTER_DAYS}
                   + coalesce(a.sday, CAST(floor(l.created_us / 86400e6) AS BIGINT)) AS cl,
               l.qty AS w,
               CASE WHEN l.taker_yes THEN -1.0 ELSE 1.0 END * (a.o - l.p)
               - a.fee_rate * l.p * (1 - l.p) AS v
        FROM lv l JOIN mka a USING (mid) WHERE a.settlement_us IS NOT NULL
        """
    )
    h = cell_stats(con, "src_h", ["horizon", "side"], [])
    h["horizon"] = h["horizon"].map(horizon_label)
    h["side"] = h["side"].map(SIDE_LABEL)
    out["horizon_expost"] = h
    return out


def validity(data_dir: Path, residue: int, counts: dict, cells: pd.DataFrame) -> dict:
    """Data checks of Amendment 2; a failed check means no gate and no conclusion."""
    hours = sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, residue)
    got = hour_counts(data_dir, residue)
    empty = sum(1 for h in hours if got.get(hour_key(h), 0) == 0)
    in_window = (
        counts["trades"] - counts.get("trades_block", 0) - counts.get("trades_outside_window", 0)
    )
    eligible = sum(counts.get(f"trades_{k}", 0) for k in ("ok", "not_final", "not_binary"))
    a = cells[(cells["stat"] == "A") & (cells["category"] == "ALL")]
    periods = sorted(set(a.loc[a["contracts"] > 0, "sample"]) & set(SAMPLES))
    v = {
        "hours": len(hours),
        "empty_hour_share": empty / len(hours) if hours else 1.0,
        "unmatched_share": counts.get("trades_no_market", 0) / in_window if in_window else 1.0,
        "unsettled_share": counts.get("trades_not_final", 0) / eligible if eligible else 1.0,
        "periods": periods,
    }
    reasons = []
    if v["empty_hour_share"] > PREREG.max_empty_hour_share:
        reasons.append(f"{v['empty_hour_share']:.1%} of sampled hours returned no trade")
    if v["unmatched_share"] > PREREG.max_unmatched_share:
        reasons.append(f"{v['unmatched_share']:.1%} of trades have no market record")
    if v["unsettled_share"] > PREREG.max_unsettled_share:
        reasons.append(f"{v['unsettled_share']:.1%} of eligible trades are in non-final markets")
    if len(periods) < 2:
        reasons.append(f"periods with data: {periods}")
    v["valid"] = not reasons
    v["reasons"] = reasons
    return v


def needed_gb(data_dir: Path, residue: int) -> float:
    """Scratch disk for DuckDB with a 500 MB memory cap: 3.7 GB measured at 36M trades, so
    about 100 bytes per trade; the estimate takes 130 plus a fixed gigabyte."""
    n = sum(hour_counts(data_dir, residue).values())
    return 1.0 + 1.3e-7 * n


def _no_data(data_dir: Path, residue: int) -> str | None:
    if not list((data_dir / "markets").glob("part-*.parquet")):
        return "no market record was downloaded"
    if not list((data_dir / f"trades_r{residue}").glob("*.parquet")):
        return "no trade file was downloaded"
    return None


def _write_gate(path: Path, gate: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(gate, indent=2))
    tmp.replace(path)


def run(
    data_dir: Path,
    reports_dir: Path,
    residue: int,
    write_gate: bool,
    final_attempt: bool = True,
) -> dict:
    """Statistics, checks and, for the primary sample, the gate.

    With failed checks, the gate is written (as invalid) only on the final attempt; before
    that the caller downloads again and retries (Amendment 3).
    """
    label = "primary" if residue == PREREG.primary_residue else f"r{residue}"
    out_dir = reports_dir / "backtest" / label
    out_dir.mkdir(parents=True, exist_ok=True)
    gate_path = data_dir / "gate.json"
    missing = _no_data(data_dir, residue)
    if missing:
        checks = {"valid": False, "reasons": [missing]}
        summary = {"label": label, "residue": residue, "validity": checks, "gate_written": False}
        if write_gate and final_attempt and not gate_path.exists():
            _write_gate(
                gate_path,
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "prereg_sha256": prereg_sha256(),
                    "valid": False,
                    "invalid_reasons": [missing],
                    "replication_fails": False,
                    "pairs_tested": 0,
                    "qualifying": [],
                },
            )
            summary["gate_written"] = True
        (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        return summary
    free, need = shutil.disk_usage(data_dir).free / 1e9, needed_gb(data_dir, residue)
    if free < need:
        raise RuntimeError(f"{free:.1f} GB free on {data_dir}, the backtest needs {need:.1f}")
    db_path = data_dir / f"work_r{residue}.duckdb"
    con = connect(db_path)
    try:
        counts = build_tables(con, data_dir, residue)
        log.info("backtest %s: %s", label, counts)
        create_src(con)
        allc = cell_stats(con, "src", ["stat", "side"], ["period", "cid", "bucket"])
        names = _labels(con)
        diags = diagnostics(con)
    finally:
        con.close()
        for p in (db_path, db_path.with_suffix(db_path.suffix + ".wal")):
            p.unlink(missing_ok=True)
    allc = allc.rename(columns={"period": "sample", "cid": "category"})
    allc["stat"] = allc["stat"].map(STAT_LABEL)
    allc["side"] = allc["side"].map(SIDE_LABEL)
    allc["sample"] = allc["sample"].map(PERIOD_LABEL)
    allc["category"] = allc["category"].map(names)
    cells = allc[allc["bucket"] >= 0][CELL_KEYS + OUT_COLUMNS]
    cells = cells.sort_values(["stat", "category", "side", "bucket", "sample"])
    overall = allc[allc["bucket"] < 0][CELL_KEYS + OUT_COLUMNS]
    cells.to_csv(out_dir / "cells.csv", index=False)
    overall.to_csv(out_dir / "overall.csv", index=False)
    for name, df in diags.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)

    # replication: statistic A over all categories and both sides, per period
    a_all = overall[(overall["stat"] == "A") & (overall["category"] == "ALL")]
    replication = {}
    for sample, g in a_all.groupby("sample"):
        w = g["contracts"].sum()
        replication[sample] = {
            "mean_c": round(float((g["mean_c"] * g["contracts"]).sum() / w), 4),
            "t_by_side": {r["side"]: round(float(r["t"]), 2) for _, r in g.iterrows()},
        }
    checks = validity(data_dir, residue, counts, cells)
    summary = {
        "label": label,
        "residue": residue,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prereg_sha256": prereg_sha256(),
        "counts": counts,
        "validity": checks,
        "replication_A_pooled": replication,
        "replication_fails": bool(
            checks["valid"] and all(replication[s]["mean_c"] < 0 for s in SAMPLES)
        ),
    }
    summary["gate_written"] = False
    if write_gate and gate_path.exists():
        log.warning("gate.json exists and is never overwritten; primary statistics only reported")
    elif write_gate and not checks["valid"] and not final_attempt:
        log.warning("validity checks failed, gate deferred: %s", checks["reasons"])
    elif write_gate:
        qualifying, tested = decide(cells) if checks["valid"] else ([], 0)
        summary["pairs_tested"] = tested
        summary["qualifying"] = qualifying
        gate = {
            "generated_at": summary["generated_at"],
            "prereg_sha256": summary["prereg_sha256"],
            "valid": checks["valid"],
            "invalid_reasons": checks["reasons"],
            "replication_fails": summary["replication_fails"],
            "pairs_tested": tested,
            "qualifying": qualifying,
        }
        _write_gate(gate_path, gate)
        summary["gate_written"] = True
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def holdout_check(reports_dir: Path, gate: dict, holdout_label: str) -> pd.DataFrame:
    """Holdout mean and t of each qualifying pair (both periods pooled); it changes no decision."""
    cells = pd.read_csv(reports_dir / "backtest" / holdout_label / "cells.csv")
    cells = cells[cells["sample"] == "all"]
    rows = []
    for q in gate.get("qualifying", []):
        sel = cells[
            (cells["stat"] == VARIANT_STAT[q["variant"]])
            & (cells["category"] == q["category"])
            & (cells["side"] == q["side"])
            & (cells["bucket"] == q["bucket"])
        ]
        r = sel.iloc[0] if len(sel) else None
        rows.append(
            {
                **q,
                "holdout_events": int(r["events"]) if r is not None else 0,
                "holdout_mean_c": float(r["mean_c"]) if r is not None else float("nan"),
                "holdout_t": float(r["t"]) if r is not None else float("nan"),
                "contradicted": bool(r is not None and r["mean_c"] < 0),
            }
        )
    return pd.DataFrame(rows)
