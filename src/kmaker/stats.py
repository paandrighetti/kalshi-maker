"""Cluster-robust means for cells, and the pre-registered decision rule.

A cell's mean is sum(s) / sum(w), where s is the sum of weight x value and w the sum of weights.
Its variance is the linearization of a ratio estimator with clusters as sampling units (Cameron
and Miller 2015), with the small-sample factor G / (G - 1):

    var(m) = G / (G - 1) * sum_g (s_g - m w_g)^2 / (sum_g w_g)^2

Clusters are a category and a settlement date (PREREGISTRATION.md, Amendment 1). The backtest
computes the per-cell sums in DuckDB and calls `finish`; the forward report, which is small,
uses `cluster_table` on per-fill rows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import PREREG

VARIANT_STAT = {"PENNY": "B", "JOIN": "C"}
# Webb's six-point distribution: mean 0, variance 1, usable with few clusters (Webb 2023)
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
SAMPLES = ("exploration", "confirmation")
OUT_COLUMNS = ["clusters", "events", "losing", "contracts", "rows", "mean_c", "se_c", "t"]


def finish(cells: pd.DataFrame) -> pd.DataFrame:
    """Mean, standard error and t (cents per contract) from G, W, m and the residual sum e2."""
    out = cells.copy()
    G = out["clusters"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        var = np.where(
            (G > 1) & (out["e2"] > 0), G / (G - 1) * out["e2"] / out["contracts"] ** 2, np.nan
        )
        se = np.sqrt(var)
        out["t"] = out["m"] / se
    out["mean_c"] = 100 * out["m"]
    out["se_c"] = 100 * se
    return out.drop(columns=["m", "e2"])


def cluster_table(
    df: pd.DataFrame, keys: list[str], cluster: str = "cluster", event: str = "event"
) -> pd.DataFrame:
    """Per-group statistics from rows holding `s` (weight x value), `w` and `n`."""
    g = df.groupby(keys + [cluster], as_index=False, observed=True)[["s", "w", "n"]].sum()
    tot = g.groupby(keys, as_index=False, observed=True).agg(
        s_tot=("s", "sum"), contracts=("w", "sum"), rows=("n", "sum"), clusters=(cluster, "size")
    )
    tot["m"] = tot["s_tot"] / tot["contracts"]
    g = g.merge(tot[keys + ["m"]], on=keys, how="left")
    g["e2"] = (g["s"] - g["m"] * g["w"]) ** 2
    g["neg"] = (g["s"] < 0).astype(int)
    agg = g.groupby(keys, as_index=False, observed=True).agg(
        e2=("e2", "sum"), losing=("neg", "sum")
    )
    ev = df.groupby(keys, as_index=False, observed=True).agg(events=(event, "nunique"))
    out = tot.merge(agg, on=keys).merge(ev, on=keys)
    return finish(out)[keys + OUT_COLUMNS]


def _ratio_t(s: np.ndarray, w: np.ndarray) -> np.ndarray:
    """t of `finish` for one set of cluster sums per row of `s` (shape draws x G)."""
    G, W = s.shape[-1], w.sum()
    m = s.sum(axis=-1) / W
    e2 = ((s - m[..., None] * w) ** 2).sum(axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        # zero residual variance has no t, as in `finish`
        return np.where(e2 > 0, m / (np.sqrt(G / (G - 1) * e2) / W), np.nan)


def wild_cluster_p(s, w, draws: int, seed: int, chunk: int = 5_000) -> float | None:
    """One-sided p of a positive mean, by the wild cluster bootstrap with the null imposed.

    `s` and `w` are per-cluster sums of weight x value and of weights. Under the null the mean
    is zero, so a cluster's restricted residual is its sum: each draw multiplies the sums by
    Webb weights and recomputes the t of `finish` (Cameron, Gelbach and Miller 2008; MacKinnon
    and Webb 2017). Reported only (Amendment 5); None when the t itself is not defined.
    """
    s, w = np.asarray(s, dtype=float), np.asarray(w, dtype=float)
    if len(s) < 2 or w.sum() <= 0:
        return None
    t0 = float(_ratio_t(s, w))
    if not np.isfinite(t0):
        return None
    rng = np.random.default_rng(seed)
    hits, done = 0, 0
    while done < draws:
        n = min(chunk, draws - done)
        t = _ratio_t(WEBB[rng.integers(0, 6, size=(n, len(s)))] * s, w)
        hits += int((t >= t0).sum())  # an undefined t (nan) never counts
        done += n
    return (hits + 1) / (draws + 1)


def leave_one_out(s, w) -> tuple[float, float] | None:
    """Lowest and highest mean, in cents per contract, with one cluster left out."""
    s, w = np.asarray(s, dtype=float), np.asarray(w, dtype=float)
    rest = w.sum() - w
    keep = rest > 0
    if len(s) < 2 or not keep.any():
        return None
    means = 100 * (s.sum() - s[keep]) / rest[keep]
    return float(means.min()), float(means.max())


def passes(row: pd.Series | None) -> bool:
    if row is None:
        return False
    t = float(row["t"])
    return bool(
        row["clusters"] >= PREREG.min_clusters
        and row["events"] >= PREREG.min_events
        and row["contracts"] >= PREREG.min_contracts
        and row["losing"] >= PREREG.min_losing_clusters
        and row["mean_c"] > 0
        and np.isfinite(t)
        and t >= PREREG.min_t
    )


def decide(cells: pd.DataFrame) -> tuple[list[dict], int]:
    """Qualifying (variant, category, side, bucket) pairs and the number of pairs tested.

    `cells` holds one row per (stat, sample, category, side, bucket). A pair qualifies when its
    variant's statistic passes in the exploration and in the confirmation sample separately.
    """
    idx = cells.set_index(["stat", "sample", "category", "side", "bucket"])
    qualifying, tested = [], 0
    for variant, stat in VARIANT_STAT.items():
        sub = cells[(cells["stat"] == stat) & (cells["sample"].isin(SAMPLES))]
        for (category, side, bucket), _ in sub.groupby(["category", "side", "bucket"]):
            tested += 1
            rows = []
            for sample in SAMPLES:
                key = (stat, sample, category, side, bucket)
                rows.append(idx.loc[key] if key in idx.index else None)
            if all(passes(r) for r in rows):
                qualifying.append(
                    {
                        "variant": variant,
                        "category": category,
                        "side": side,
                        "bucket": int(bucket),
                        "exploration_mean_c": round(float(rows[0]["mean_c"]), 4),
                        "exploration_t": round(float(rows[0]["t"]), 2),
                        "confirmation_mean_c": round(float(rows[1]["mean_c"]), 4),
                        "confirmation_t": round(float(rows[1]["t"]), 2),
                    }
                )
    return qualifying, tested
