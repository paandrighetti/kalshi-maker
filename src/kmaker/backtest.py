"""Statistics A, B and C of PREREGISTRATION.md on the downloaded sample, and the gate.

Every decision uses only what was known when a trade printed: its market, category, price,
size and the direction of the taker. The outcome enters only as the settlement value of the
maker's position, and the settlement date only as a cluster label. All per-print work happens in
a DuckDB file on disk with a memory cap, so tens of millions of prints fit next to the other
services of a small server; pandas only sees one row per cell.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from .config import PREREG, prereg_sha256
from .ingest import load_markets, load_series, ranges_table
from .stats import OUT_COLUMNS, SAMPLES, VARIANT_STAT, decide, finish

log = logging.getLogger(__name__)

HORIZON_EDGES = (0.0, 1.0, 6.0, 24.0, 168.0)
ROLLUP = {"sample": "'all'", "category": "'ALL'", "bucket": "-1"}
CELL_KEYS = ["stat", "sample", "category", "side", "bucket"]


def _us(dt: datetime) -> int:
    return int(dt.timestamp()) * 1_000_000


def _bucket_sql(col: str) -> str:
    edges = PREREG.buckets
    parts = [f"WHEN {col} < {edges[i + 1]} THEN {i}" for i in range(len(edges) - 1)]
    return f"(CASE {' '.join(parts)} ELSE {len(edges) - 1} END)"


def _horizon_sql(col: str) -> str:
    e = HORIZON_EDGES
    parts = [f"WHEN {col} < {e[i + 1]} THEN '{e[i]:g}-{e[i + 1]:g}h'" for i in range(len(e) - 1)]
    return f"(CASE {' '.join(parts)} ELSE '{e[-1]:g}h+' END)"


def connect(path: Path, memory_limit: str = "400MB") -> duckdb.DuckDBPyConnection:
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
    return con


def build_tables(con: duckdb.DuckDBPyConnection, data_dir: Path, residue: int) -> dict:
    """`lvr`: one row per (taker order, price level) with everything the statistics need."""
    markets = load_markets(data_dir)
    con.register("sr_df", load_series(data_dir))
    con.register("mk_df", markets)
    con.register("rg_df", ranges_table(markets))
    con.execute("CREATE OR REPLACE TABLE sr AS SELECT * FROM sr_df")
    con.execute("CREATE OR REPLACE TABLE mk AS SELECT * FROM mk_df")
    con.execute("CREATE OR REPLACE TABLE rg AS SELECT * FROM rg_df")
    for name in ("sr_df", "mk_df", "rg_df"):
        con.unregister(name)
    glob = str(data_dir / f"trades_r{residue}" / "*.parquet")
    excluded = ", ".join(f"'{c}'" for c in PREREG.excluded_categories)
    coef = PREREG.maker_fee_coef
    con.execute(f"CREATE OR REPLACE VIEW tr AS SELECT * FROM read_parquet('{glob}')")

    def one(q: str) -> int:
        return con.execute(q).fetchone()[0]

    counts = {
        "trades": one("SELECT count(*) FROM tr"),
        "drop_no_market": one(
            "SELECT count(*) FROM tr LEFT JOIN mk USING (ticker) WHERE mk.ticker IS NULL"
        ),
        "drop_unknown_series": one(
            "SELECT count(*) FROM tr JOIN mk USING (ticker) "
            "LEFT JOIN sr ON sr.series = mk.series WHERE sr.series IS NULL"
        ),
        "drop_result": one(
            "SELECT count(*) FROM tr JOIN mk USING (ticker) WHERE mk.result NOT IN ('yes', 'no')"
        ),
        "drop_mve": one("SELECT count(*) FROM tr JOIN mk USING (ticker) WHERE mk.mve"),
        "drop_block": one("SELECT count(*) FROM tr WHERE is_block"),
    }
    con.execute(
        f"""
        CREATE OR REPLACE VIEW pr AS
        SELECT t.ticker, t.count AS qty, t.yes_price AS p, t.taker_yes, t.created_us,
               m.event_ticker AS event, s.category, m.settlement_us,
               s.category || '|' || strftime(
                   to_timestamp(coalesce(m.settlement_us, t.created_us) / 1e6), '%Y-%m-%d'
               ) AS cl,
               CASE WHEN m.result = 'yes' THEN 1.0 ELSE 0.0 END AS o,
               CASE WHEN t.taker_yes THEN -1.0 ELSE 1.0 END AS d,
               CASE WHEN s.fee_type LIKE 'quadratic_with%'
                    THEN {coef} * coalesce(s.fee_multiplier, 1.0) ELSE 0.0 END AS fee_rate,
               CASE WHEN t.created_us < {_us(PREREG.split)} THEN 'exploration'
                    ELSE 'confirmation' END AS sample
        FROM tr t
        JOIN mk m ON m.ticker = t.ticker
        JOIN sr s ON s.series = m.series
        WHERE m.result IN ('yes', 'no') AND NOT m.mve AND NOT t.is_block
          AND s.category NOT IN ({excluded})
          AND t.yes_price > 0 AND t.yes_price < 1 AND t.count > 0
          AND t.created_us >= {_us(PREREG.window_start)}
          AND t.created_us < {_us(PREREG.window_end)}
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE lvr AS
        WITH lv AS (
            SELECT ticker, created_us, taker_yes, p, sum(qty) AS qty, any_value(event) AS event,
                   any_value(category) AS category, any_value(cl) AS cl, any_value(o) AS o,
                   any_value(d) AS d, any_value(fee_rate) AS fee_rate,
                   any_value(sample) AS sample, any_value(settlement_us) AS settlement_us
            FROM pr GROUP BY ticker, created_us, taker_yes, p
        )
        SELECT lv.*,
               row_number() OVER w_ord AS lvl,
               count(*) OVER w_all AS nlv,
               sum(qty) OVER w_all AS order_qty
        FROM lv
        WINDOW w_all AS (PARTITION BY ticker, created_us, taker_yes),
               w_ord AS (PARTITION BY ticker, created_us, taker_yes
                         ORDER BY CASE WHEN taker_yes THEN p ELSE -p END)
        """
    )
    counts["prints_kept"] = one("SELECT count(*) FROM pr")
    counts["levels"] = one("SELECT count(*) FROM lvr")
    counts["orders"] = one("SELECT count(*) FROM lvr WHERE lvl = 1")
    counts["events"] = one("SELECT count(DISTINCT event) FROM lvr")
    counts["clusters"] = one("SELECT count(DISTINCT cl) FROM lvr")
    return counts


def create_src(con: duckdb.DuckDBPyConnection) -> None:
    """View of the rows of statistics A, B and C: keys, event, cluster, weight w, value v."""
    cap = PREREG.penny_fill_cap
    side = "CASE WHEN d < 0 THEN 'short_yes' ELSE 'long_yes' END"
    con.execute(
        f"""
        CREATE OR REPLACE VIEW src AS
        WITH b1 AS (
            SELECT l.*, CASE WHEN l.taker_yes THEN l.p - coalesce(r.step, 0.01)
                             ELSE l.p + coalesce(r.step, 0.01) END AS a,
                   least(l.order_qty, {cap}) AS q
            FROM lvr l LEFT JOIN rg r ON r.ticker = l.ticker AND l.p >= r.lo AND l.p < r.hi
            WHERE l.lvl = 1
        )
        SELECT 'A' AS stat, sample, category, {side} AS side, {_bucket_sql("p")} AS bucket,
               event, cl, qty AS w, d * (o - p) - fee_rate * p * (1 - p) AS v
        FROM lvr
        UNION ALL
        SELECT 'C', sample, category, {side}, {_bucket_sql("p")}, event, cl, qty,
               d * (o - p) - fee_rate * p * (1 - p)
        FROM lvr WHERE lvl < nlv
        UNION ALL
        SELECT 'B', sample, category, {side}, {_bucket_sql("a")}, event, cl, q,
               d * (o - a) - ceil(round(fee_rate * q * a * (1 - a) * 100, 9)) / 100 / q
        FROM b1 WHERE a > 0 AND a < 1
        """
    )


def cell_stats(
    con: duckdb.DuckDBPyConnection, src: str, fixed: list[str], cube: list[str]
) -> pd.DataFrame:
    """Per-cell clustered statistics, with every roll-up of the `cube` columns."""
    keys = fixed + cube
    cube_sql = f", CUBE({', '.join(cube)})" if cube else ""
    sel = ", ".join(fixed + [f"coalesce({c}, {ROLLUP[c]}) AS {c}" for c in cube])
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
    con.execute(
        f"""
        CREATE OR REPLACE TABLE ev AS
        SELECT {sel}, events FROM (
            SELECT {raw}, count(*) AS events
            FROM (SELECT DISTINCT {raw}, event FROM {src})
            GROUP BY {", ".join(fixed)}{cube_sql}
        )
        """
    )
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


def diagnostics(con: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    """Descriptive tables; none of them enters the decision."""
    out = {}
    out["volume"] = con.execute(
        """
        SELECT category, sample, count(DISTINCT event) AS events,
               count(DISTINCT ticker) AS markets, sum(qty) AS contracts,
               sum(CASE WHEN taker_yes THEN qty ELSE 0 END) / sum(qty) AS taker_yes_share
        FROM lvr GROUP BY ALL ORDER BY category, sample
        """
    ).df()
    out["calibration"] = con.execute(
        """
        SELECT coalesce(category, 'ALL') AS category, decile_lo, contracts, mean_price, yes_rate
        FROM (
            SELECT category, least(floor(p * 10), 9) / 10 AS decile_lo, sum(qty) AS contracts,
                   sum(qty * p) / sum(qty) AS mean_price, sum(qty * o) / sum(qty) AS yes_rate
            FROM lvr GROUP BY GROUPING SETS ((category, decile_lo), (decile_lo))
        ) ORDER BY 1, 2
        """
    ).df()
    side = "CASE WHEN d < 0 THEN 'short_yes' ELSE 'long_yes' END"
    hours = "(settlement_us - created_us) / 3.6e9"
    con.execute(
        f"""
        CREATE OR REPLACE VIEW src_h AS
        SELECT {_horizon_sql(hours)} AS horizon, {side} AS side, event, cl, qty AS w,
               d * (o - p) - fee_rate * p * (1 - p) AS v
        FROM lvr WHERE settlement_us IS NOT NULL
        """
    )
    out["horizon_expost"] = cell_stats(con, "src_h", ["horizon", "side"], [])
    return out


def run(data_dir: Path, reports_dir: Path, residue: int, write_gate: bool) -> dict:
    label = "primary" if residue == PREREG.primary_residue else f"r{residue}"
    out_dir = reports_dir / "backtest" / label
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / f"work_r{residue}.duckdb"
    con = connect(db_path)
    try:
        counts = build_tables(con, data_dir, residue)
        log.info("backtest %s: %s", label, counts)
        create_src(con)
        allc = cell_stats(con, "src", ["stat", "side"], ["sample", "category", "bucket"])
        diags = diagnostics(con)
    finally:
        con.close()
        for p in (db_path, db_path.with_suffix(db_path.suffix + ".wal")):
            p.unlink(missing_ok=True)
    cells = allc[allc["bucket"] >= 0][CELL_KEYS + OUT_COLUMNS]
    cells = cells.sort_values(["stat", "category", "side", "bucket", "sample"])
    overall = allc[allc["bucket"] < 0][CELL_KEYS + OUT_COLUMNS]
    cells.to_csv(out_dir / "cells.csv", index=False)
    overall.to_csv(out_dir / "overall.csv", index=False)
    for name, df in diags.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)

    # replication: statistic A over all categories and both sides, per sample
    a_all = overall[(overall["stat"] == "A") & (overall["category"] == "ALL")]
    replication = {}
    for sample, g in a_all.groupby("sample"):
        w = g["contracts"].sum()
        replication[sample] = {
            "mean_c": round(float((g["mean_c"] * g["contracts"]).sum() / w), 4),
            "t_by_side": {r["side"]: round(float(r["t"]), 2) for _, r in g.iterrows()},
        }
    summary = {
        "label": label,
        "residue": residue,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prereg_sha256": prereg_sha256(),
        "counts": {k: int(v) for k, v in counts.items()},
        "replication_A_pooled": replication,
        "replication_fails": bool(
            all(replication.get(s, {"mean_c": 0.0})["mean_c"] < 0 for s in SAMPLES)
        ),
    }
    if write_gate:
        qualifying, tested = decide(cells)
        summary["pairs_tested"] = tested
        summary["qualifying"] = qualifying
        gate = {
            "generated_at": summary["generated_at"],
            "prereg_sha256": summary["prereg_sha256"],
            "replication_fails": summary["replication_fails"],
            "pairs_tested": tested,
            "qualifying": qualifying,
        }
        (data_dir / "gate.json").write_text(json.dumps(gate, indent=2))
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
