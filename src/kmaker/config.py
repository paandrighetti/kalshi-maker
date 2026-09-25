"""Settings. Pre-registered values are constants; only operational knobs come from the environment.

Every constant in `PREREG` is stated in PREREGISTRATION.md. Changing one here without changing
that file would make the reports disagree with the hash they print, so they live in code, not in
`.env`.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class Prereg:
    window_start: datetime = _utc("2025-12-01T00:00:00")
    window_end: datetime = _utc("2026-09-08T00:00:00")
    split: datetime = _utc("2026-05-01T00:00:00")  # on latest_expiration_time (Amendment 3)
    latest_expiration_cutoff: datetime = _utc("2026-09-15T00:00:00")
    final_statuses: tuple[str, ...] = ("finalized", "settled")
    hour_mod: int = 12
    primary_residue: int = 0
    holdout_residue: int = 1
    excluded_categories: tuple[str, ...] = ("Sports",)
    buckets: tuple[float, ...] = (0.0, 0.10, 0.30, 0.70, 0.90)
    penny_fill_cap: float = 10.0
    maker_fee_coef: float = 0.0175
    min_clusters: int = 30
    min_events: int = 100
    min_contracts: float = 500.0
    min_losing_clusters: int = 10
    min_t: float = 2.0
    # data validity (Amendment 2)
    max_empty_hour_share: float = 0.02
    max_unmatched_share: float = 0.05
    max_unsettled_share: float = 0.01
    # forward test
    quote_size: float = 10.0
    max_days_to_expiry: float = 7.0
    live_delay_s: float = 1.0
    max_contracts_per_market: float = 100.0
    max_risk_per_event: float = 500.0
    max_risk_total: float = 5000.0
    success_min_events: int = 200
    # forward success is checked twice (Amendment 4): the one-sided error of t >= 2 (2.3 %) is
    # split between the two looks (Bonferroni), 1.14 % each, hence t >= 2.28
    forward_look_t: float = 2.28
    forward_final_day: float = 60.0
    forward_abandon_day: float = 30.0


PREREG = Prereg()


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("KM_DATA_DIR", "data")))
    reports_dir: Path = field(default_factory=lambda: Path(os.getenv("KM_REPORTS_DIR", "reports")))
    rate: float = field(default_factory=lambda: float(os.getenv("KM_RATE", "6")))
    rate_paper: float = field(default_factory=lambda: float(os.getenv("KM_RATE_PAPER", "4")))
    api_bases: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            b.strip()
            for b in os.getenv(
                "KM_API_BASES",
                "https://api.elections.kalshi.com/trade-api/v2,"
                "https://external-api.kalshi.com/trade-api/v2",
            ).split(",")
            if b.strip()
        )
    )
    cycle_s: float = field(default_factory=lambda: float(os.getenv("KM_CYCLE_S", "20")))
    max_markets: int = field(default_factory=lambda: int(os.getenv("KM_MAX_MARKETS", "400")))
    min_free_gb: float = field(default_factory=lambda: float(os.getenv("KM_MIN_FREE_GB", "3")))
    telegram_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    log_level: str = field(default_factory=lambda: os.getenv("KM_LOG_LEVEL", "INFO"))


def prereg_sha256() -> str:
    """Hash of PREREGISTRATION.md, looked up next to the package or in the working directory."""
    candidates = [
        Path(os.getenv("KM_PREREG_PATH", "")),
        Path(__file__).resolve().parents[2] / "PREREGISTRATION.md",
        Path("/app/PREREGISTRATION.md"),
        Path("PREREGISTRATION.md"),
    ]
    for p in candidates:
        if p.name and p.is_file():
            return hashlib.sha256(p.read_bytes()).hexdigest()
    return "missing"
