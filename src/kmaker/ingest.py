"""Download the pre-registered sample: series, the trades of the sampled hours, their markets.

Everything is resumable. Each sampled hour is one parquet file written atomically, so an
interrupted run restarts at the first missing hour; markets are fetched only for tickers not yet
stored with a final result. Sports series are dropped when trades are written, which keeps the
files small (sports is most of Kalshi's volume and is excluded by the pre-registration).
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

import pandas as pd

from .client import Kalshi
from .config import PREREG
from .schema import (
    MARKET_COLUMNS,
    TRADE_COLUMNS,
    normalize_market,
    normalize_trade,
    parse_ranges,
    series_of,
)

log = logging.getLogger(__name__)

MARKET_BATCH = 50


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


def _write_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def free_gb(path: Path) -> float:
    path.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(path).free / 1e9


# series ------------------------------------------------------------------------------------


def _series_row(s: dict) -> dict:
    return {
        "series": s.get("ticker", ""),
        "category": s.get("category") or "",
        "fee_type": s.get("fee_type") or "",
        "fee_multiplier": float(s.get("fee_multiplier") or 1.0),
        "title": s.get("title") or "",
    }


def ingest_series(client: Kalshi, data_dir: Path) -> pd.DataFrame:
    rows = [_series_row(s) for s in client.series() if s.get("ticker")]
    df = pd.DataFrame(rows).drop_duplicates("series")
    _write_atomic(df, data_dir / "series.parquet")
    log.info("series: %d, categories: %s", len(df), sorted(df["category"].unique()))
    return df


def load_series(data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(data_dir / "series.parquet")


def ingest_missing_series(client: Kalshi, data_dir: Path, markets: pd.DataFrame) -> int:
    """Fetch one by one the series of downloaded markets that the listing did not return."""
    series = load_series(data_dir)
    missing = sorted(set(markets["series"]) - set(series["series"]))
    rows = [_series_row(s) for s in map(client.series_one, missing) if s and s.get("ticker")]
    if rows:
        df = pd.concat([series, pd.DataFrame(rows)], ignore_index=True).drop_duplicates("series")
        _write_atomic(df, data_dir / "series.parquet")
    log.info("series missing from the listing: %d, fetched: %d", len(missing), len(rows))
    return len(rows)


def excluded_series(series: pd.DataFrame, excluded: Iterable[str]) -> set[str]:
    excluded = set(excluded)
    return set(series.loc[series["category"].isin(excluded), "series"])


# trades ------------------------------------------------------------------------------------


def trades_for_hour(
    client: Kalshi, hour_start: int, cutoff_s: int, drop_series: set[str]
) -> pd.DataFrame:
    """All trades created in [hour_start, hour_start + 3600), non-excluded series only.

    Trades created before Kalshi's historical cutoff are served by `/historical/trades`, later
    ones by `/markets/trades`; an hour straddling the cutoff is read from both. Bounds are
    widened by a second on each side and enforced locally on microsecond timestamps, and trades
    are deduplicated by id, so boundary semantics of `min_ts` / `max_ts` do not matter.
    """
    lo, hi = hour_start, hour_start + 3600
    sources = []
    if lo < cutoff_s:
        sources.append(True)
    if hi > cutoff_s:
        sources.append(False)
    rows = []
    for historical in sources:
        for t in client.trades(lo - 1, hi + 1, historical=historical):
            row = normalize_trade(t)
            if row is None or series_of(row[0]) in drop_series:
                continue
            if lo * 1_000_000 <= row[5] < hi * 1_000_000:
                rows.append(row)
    df = pd.DataFrame(rows, columns=TRADE_COLUMNS)
    return df.drop_duplicates("trade_id", keep="first") if len(df) else df


def ingest_trades(
    client: Kalshi, data_dir: Path, residue: int, min_free_gb: float = 3.0
) -> list[Path]:
    series = load_series(data_dir)
    drop = excluded_series(series, PREREG.excluded_categories)
    cutoff = client.cutoff()
    cutoff_s = int(
        datetime.fromisoformat(cutoff["trades_created_ts"].replace("Z", "+00:00")).timestamp()
    )
    hours = sampled_hours(PREREG.window_start, PREREG.window_end, PREREG.hour_mod, residue)
    out_dir = data_dir / f"trades_r{residue}"
    done = 0
    for i, h in enumerate(hours):
        path = out_dir / f"{hour_key(h)}.parquet"
        if path.exists():
            done += 1
            continue
        if free_gb(data_dir) < min_free_gb:
            raise RuntimeError(f"less than {min_free_gb} GB free on {data_dir}, stopping")
        df = trades_for_hour(client, h, cutoff_s, drop)
        _write_atomic(df, path)
        done += 1
        if i % 20 == 0:
            log.info(
                "trades r%d: %d/%d hours, last %s: %d rows, %d requests",
                residue,
                done,
                len(hours),
                hour_key(h),
                len(df),
                client.requests,
            )
    log.info("trades r%d complete: %d hours", residue, len(hours))
    return sorted(out_dir.glob("*.parquet"))


# markets -----------------------------------------------------------------------------------


def _tickers_in(paths: Iterable[Path]) -> set[str]:
    tickers: set[str] = set()
    for p in paths:
        tickers.update(pd.read_parquet(p, columns=["ticker"])["ticker"].unique())
    return tickers


def load_markets(data_dir: Path) -> pd.DataFrame:
    parts = sorted((data_dir / "markets").glob("*.parquet"))
    if not parts:
        return pd.DataFrame(columns=MARKET_COLUMNS)
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    # later parts supersede earlier ones for the same ticker (a market re-fetched once settled)
    return df.drop_duplicates("ticker", keep="last").reset_index(drop=True)


def ingest_markets(client: Kalshi, data_dir: Path, trade_paths: Iterable[Path]) -> pd.DataFrame:
    wanted = _tickers_in(trade_paths)
    have = load_markets(data_dir)
    final = set(have.loc[have["result"].isin(["yes", "no", "scalar"]), "ticker"])
    todo = sorted(wanted - final)
    log.info(
        "markets: %d tickers in trades, %d final, %d to fetch", len(wanted), len(final), len(todo)
    )
    out_dir = data_dir / "markets"
    start_part = len(list(out_dir.glob("*.parquet"))) if out_dir.exists() else 0
    part_rows: list[dict] = []
    part = start_part
    for i in range(0, len(todo), MARKET_BATCH):
        batch = todo[i : i + MARKET_BATCH]
        got = {m["ticker"]: m for m in client.markets_by_tickers(batch, historical=False)}
        missing = [t for t in batch if t not in got]
        if missing:
            got.update(
                {m["ticker"]: m for m in client.markets_by_tickers(missing, historical=True)}
            )
        part_rows.extend(normalize_market(m) for m in got.values())
        if len(part_rows) >= 20_000 or i + MARKET_BATCH >= len(todo):
            _write_atomic(
                pd.DataFrame(part_rows, columns=MARKET_COLUMNS),
                out_dir / f"part-{part:05d}.parquet",
            )
            log.info(
                "markets: %d/%d fetched, %d requests",
                min(i + MARKET_BATCH, len(todo)),
                len(todo),
                client.requests,
            )
            part_rows, part = [], part + 1
    return load_markets(data_dir)


def ranges_table(markets: pd.DataFrame) -> pd.DataFrame:
    """One row per (ticker, start, end, step) from each market's `price_ranges`."""
    rows = []
    for ticker, pr in zip(markets["ticker"], markets["price_ranges"], strict=True):
        for start, end, step in parse_ranges(pr):
            rows.append((ticker, start, end, step))
    return pd.DataFrame(rows, columns=["ticker", "lo", "hi", "step"])


def write_manifest(data_dir: Path, residue: int, extra: dict) -> None:
    path = data_dir / f"manifest_r{residue}.json"
    path.write_text(
        json.dumps(
            {"residue": residue, "written_at": datetime.now(timezone.utc).isoformat(), **extra},
            indent=2,
        )
    )
