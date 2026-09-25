"""Download the pre-registered sample: series, the trades of the sampled hours, their markets.

Everything is resumable. Each sampled hour is one parquet file written atomically with a fixed
schema, so an interrupted run restarts at the first missing hour, and an hour that came back
empty is fetched once more before the run ends. Markets are fetched only for tickers not yet
stored with a final status. Sports series are dropped when trades are written, which keeps the
files small (sports is most of Kalshi's volume and is excluded by the pre-registration).

Kalshi serves trades older than a moving cutoff only from `/historical/trades` and newer ones
only from `/markets/trades`. Every hour is read from both, live first: a trade that moves to the
historical tier between the two reads is then still seen once, and duplicates are removed by id.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .client import Kalshi
from .config import PREREG
from .schema import (
    FINAL_STATUSES,
    MARKET_COLUMNS,
    normalize_market,
    normalize_trade,
    parse_ranges,
    series_of,
)

log = logging.getLogger(__name__)

MARKET_BATCH = 50
MARKET_PART_ROWS = 20_000

TRADE_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("trade_id", pa.string()),
        ("count", pa.float64()),
        ("yes_price", pa.float64()),
        ("taker_yes", pa.bool_()),
        ("created_us", pa.int64()),
        ("is_block", pa.bool_()),
    ]
)
MARKET_SCHEMA = pa.schema(
    [
        ("ticker", pa.string()),
        ("event_ticker", pa.string()),
        ("series", pa.string()),
        ("status", pa.string()),
        ("result", pa.string()),
        ("close_us", pa.int64()),
        ("expected_expiration_us", pa.int64()),
        ("latest_expiration_us", pa.int64()),
        ("settlement_us", pa.int64()),
        ("mve", pa.bool_()),
        ("price_ranges", pa.string()),
    ]
)
RANGE_SCHEMA = pa.schema(
    [("ticker", pa.string()), ("lo", pa.float64()), ("hi", pa.float64()), ("step", pa.float64())]
)
DEFAULT_RANGES = [(0.0, 1.0, 0.01)]


def hour_key(hour_start: int) -> str:
    return datetime.fromtimestamp(hour_start, timezone.utc).strftime("%Y-%m-%dT%H")


def hour_residue(hour_start: int, mod: int) -> int:
    return int(hashlib.sha256(hour_key(hour_start).encode()).hexdigest(), 16) % mod


def sampled_hours(start: datetime, end: datetime, mod: int, residue: int) -> list[int]:
    t = int(start.timestamp()) // 3600 * 3600
    stop = int(end.timestamp())
    hours = []
    while t < stop:
        if hour_residue(t, mod) == residue:
            hours.append(t)
        t += 3600
    return hours


def _write_table(table: pa.Table, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(table, tmp)
    os.replace(tmp, path)


def write_rows(rows: list, schema: pa.Schema, path: Path) -> None:
    """Rows (tuples in schema order, or dicts) to parquet with a fixed schema, even when empty."""
    if rows and isinstance(rows[0], dict):
        cols = {f.name: [r[f.name] for r in rows] for f in schema}
    else:
        cols = {f.name: [r[i] for r in rows] for i, f in enumerate(schema)}
    _write_table(pa.table(cols, schema=schema), path)


def _write_text_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _write_df_atomic(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def free_gb(path: Path) -> float:
    path.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(path).free / 1e9


# series ------------------------------------------------------------------------------------


def _series_row(s: dict) -> dict:
    mult = s.get("fee_multiplier")
    return {
        "series": s.get("ticker", ""),
        "category": s.get("category") or "",
        "fee_type": s.get("fee_type") or "",
        "fee_multiplier": 1.0 if mult is None else float(mult),
        "title": s.get("title") or "",
    }


def ingest_series(client: Kalshi, data_dir: Path) -> pd.DataFrame:
    rows = [_series_row(s) for s in client.series() if s.get("ticker")]
    df = pd.DataFrame(rows).drop_duplicates("series")
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_df_atomic(df, data_dir / "series.parquet")
    log.info("series: %d, categories: %s", len(df), sorted(df["category"].unique()))
    return df


def load_series(data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(data_dir / "series.parquet")


def excluded_series(series: pd.DataFrame, excluded: Iterable[str]) -> set[str]:
    excluded = set(excluded)
    return set(series.loc[series["category"].isin(excluded), "series"])


def ingest_missing_series(client: Kalshi, data_dir: Path) -> int:
    """Fetch one by one the series of downloaded markets that the listing did not return."""
    series = load_series(data_dir)
    in_markets: set[str] = set()
    for p in sorted((data_dir / "markets").glob("*.parquet")):
        in_markets.update(pq.read_table(p, columns=["series"]).column("series").to_pylist())
    missing = sorted(in_markets - set(series["series"]))
    rows = [_series_row(s) for s in map(client.series_one, missing) if s and s.get("ticker")]
    if rows:
        df = pd.concat([series, pd.DataFrame(rows)], ignore_index=True).drop_duplicates("series")
        _write_df_atomic(df, data_dir / "series.parquet")
    log.info("series missing from the listing: %d, fetched: %d", len(missing), len(rows))
    return len(rows)


# trades ------------------------------------------------------------------------------------


def trades_for_hour(client: Kalshi, hour_start: int, drop_series: set[str]) -> list[tuple]:
    """All trades created in [hour_start, hour_start + 3600), non-excluded series only.

    Bounds are widened by a second on each side and enforced locally on microsecond timestamps,
    so the boundary semantics of `min_ts` and `max_ts` do not matter.
    """
    lo, hi = hour_start, hour_start + 3600
    seen: set[str] = set()
    rows = []
    for historical in (False, True):  # live first, see the module docstring
        for t in client.trades(lo - 1, hi + 1, historical=historical):
            row = normalize_trade(t)
            if row is None or row[1] in seen:
                continue
            seen.add(row[1])
            if series_of(row[0]) in drop_series:
                continue
            if lo * 1_000_000 <= row[5] < hi * 1_000_000:
                rows.append(row)
    return rows


def _hours_manifest(data_dir: Path, residue: int) -> Path:
    return data_dir / f"hours_r{residue}.json"


def hour_counts(data_dir: Path, residue: int) -> dict[str, int]:
    path = _hours_manifest(data_dir, residue)
    return json.loads(path.read_text()) if path.exists() else {}


def ingest_trades(
    client: Kalshi, data_dir: Path, residue: int, min_free_gb: float = 3.0
) -> list[Path]:
    drop = excluded_series(load_series(data_dir), PREREG.excluded_categories)
    hours = sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, residue)
    out_dir = data_dir / f"trades_r{residue}"
    manifest = _hours_manifest(data_dir, residue)
    counts = hour_counts(data_dir, residue)

    def fetch(h: int) -> None:
        if free_gb(data_dir) < min_free_gb:
            raise RuntimeError(f"less than {min_free_gb} GB free on {data_dir}, stopping")
        rows = trades_for_hour(client, h, drop)
        write_rows(rows, TRADE_SCHEMA, out_dir / f"{hour_key(h)}.parquet")
        counts[hour_key(h)] = len(rows)
        _write_text_atomic(manifest, json.dumps(counts, sort_keys=True))

    for i, h in enumerate(hours):
        if hour_key(h) in counts and (out_dir / f"{hour_key(h)}.parquet").exists():
            continue
        fetch(h)
        if i % 20 == 0:
            log.info(
                "trades r%d: hour %d of %d (%s): %d rows, %d requests so far",
                residue,
                i + 1,
                len(hours),
                hour_key(h),
                counts[hour_key(h)],
                client.requests,
            )
    for h in hours:  # one more attempt for every hour that came back empty
        if counts.get(hour_key(h), 0) == 0:
            fetch(h)
    empty = sum(1 for h in hours if counts.get(hour_key(h), 0) == 0)
    log.info("trades r%d complete: %d hours, %d empty", residue, len(hours), empty)
    return [out_dir / f"{hour_key(h)}.parquet" for h in hours]


# markets -----------------------------------------------------------------------------------


def _todo_tickers(data_dir: Path, trade_paths: Iterable[Path]) -> tuple[int, int, Path]:
    """Tickers of the trade files whose latest market record is not final, sorted into a
    parquet file, with the number of tickers in the trades and of final tickers on disk.

    A later part supersedes an earlier one, as in the backtest. The sets live in a DuckDB file
    under a memory cap, so they spill to disk: Python sets of the tickers of the second sample
    (the holdout, with the first sample's markets on disk) exceeded the container's 1,400 MB,
    and on synthetic data with 6.5 million tickers in trades and 5 million final they peak at
    1.7 GB against 0.74 GB here.
    """
    files = [str(p) for p in trade_paths if p.exists()]
    out = data_dir / "markets_todo.parquet"
    db = data_dir / "markets_todo.duckdb"
    tmp = data_dir / "duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    finals = ", ".join(f"'{s}'" for s in FINAL_STATUSES)
    for p in (db, db.with_suffix(".duckdb.wal")):
        p.unlink(missing_ok=True)
    con = duckdb.connect(str(db))
    try:
        con.execute("SET memory_limit='500MB'")
        con.execute("SET threads=1")
        con.execute(f"SET temp_directory='{tmp}'")
        con.execute("SET preserve_insertion_order=false")
        listed = ", ".join(f"'{f}'" for f in files)
        src = f"read_parquet([{listed}])" if files else "(SELECT NULL::VARCHAR AS ticker LIMIT 0)"
        con.execute(f"CREATE TABLE w AS SELECT DISTINCT ticker FROM {src}")
        con.execute("CREATE TABLE f (ticker VARCHAR)")
        if list((data_dir / "markets").glob("*.parquet")):
            rec = (
                "SELECT ticker, status, result, "
                "regexp_extract(filename, '(part-[0-9]+)[.]parquet$', 1) AS part "
                f"FROM read_parquet('{data_dir}/markets/*.parquet', filename = true)"
            )
            con.execute(
                f"""
                INSERT INTO f
                SELECT r.ticker FROM ({rec}) r
                JOIN (SELECT ticker, max(part) AS part FROM ({rec}) GROUP BY 1) lp
                  USING (ticker, part)
                WHERE r.status IN ({finals})  -- schema.is_final
                  AND lower(coalesce(r.result, '')) IN ('yes', 'no', 'scalar')
                """
            )
        n_wanted = con.execute("SELECT count(*) FROM w").fetchone()[0]
        n_final = con.execute("SELECT count(*) FROM f").fetchone()[0]
        con.execute(
            "COPY (SELECT ticker FROM w ANTI JOIN f USING (ticker) WHERE ticker IS NOT NULL "
            f"ORDER BY 1) TO '{out}' (FORMAT parquet)"
        )
    finally:
        con.close()
        for p in (db, db.with_suffix(".duckdb.wal")):
            p.unlink(missing_ok=True)
    return int(n_wanted), int(n_final), out


def ingest_markets(client: Kalshi, data_dir: Path, trade_paths: Iterable[Path]) -> dict:
    """Market records for every ticker in the trade files, in numbered parts.

    A later part supersedes an earlier one for the same ticker. Price grids other than the plain
    one-cent grid are written to `ranges/` under the same part number.
    """
    n_wanted, n_final, todo_path = _todo_tickers(data_dir, trade_paths)
    todo = pq.ParquetFile(todo_path)
    n_todo = todo.metadata.num_rows
    log.info("markets: %d tickers in trades, %d final, %d to fetch", n_wanted, n_final, n_todo)
    out_dir = data_dir / "markets"
    part = len(list(out_dir.glob("*.parquet"))) if out_dir.exists() else 0
    rows: list[dict] = []
    not_found = 0

    def flush() -> None:
        # the ranges part first: a market part on disk means its price grids are there too
        nonlocal rows, part
        if not rows:
            return
        ranges = []
        for r in rows:
            parsed = parse_ranges(r["price_ranges"])
            if parsed != DEFAULT_RANGES:
                ranges += [(r["ticker"], lo, hi, step) for lo, hi, step in parsed]
        write_rows(ranges, RANGE_SCHEMA, data_dir / "ranges" / f"part-{part:05d}.parquet")
        write_rows(rows, MARKET_SCHEMA, out_dir / f"part-{part:05d}.parquet")
        rows, part = [], part + 1

    done = 0
    for rb in todo.iter_batches(batch_size=MARKET_BATCH, columns=["ticker"]):
        batch = rb.column(0).to_pylist()
        got = {m["ticker"]: m for m in client.markets_by_tickers(batch, historical=False)}
        missing = [t for t in batch if t not in got]
        if missing:
            hist = client.markets_by_tickers(missing, historical=True)
            got.update({m["ticker"]: m for m in hist})
        not_found += sum(1 for t in batch if t not in got)
        rows.extend(normalize_market(m) for m in got.values())
        done += len(batch)
        if len(rows) >= MARKET_PART_ROWS:
            flush()
            log.info("markets: %d of %d fetched, %d requests so far", done, n_todo, client.requests)
    flush()
    todo_path.unlink(missing_ok=True)
    return {"tickers": n_wanted, "fetched": n_todo, "not_found": not_found}


def write_manifest(data_dir: Path, residue: int, extra: dict) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    body = json.dumps({"residue": residue, "written_at": stamp, **extra}, indent=2)
    _write_text_atomic(data_dir / f"manifest_r{residue}.json", body)


def load_markets(data_dir: Path) -> pd.DataFrame:
    """All market parts in memory, later parts first; for small data (tests, inspection)."""
    parts = sorted((data_dir / "markets").glob("*.parquet"))
    if not parts:
        return pd.DataFrame(columns=MARKET_COLUMNS)
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    return df.drop_duplicates("ticker", keep="last").reset_index(drop=True)
