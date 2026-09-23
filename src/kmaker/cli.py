"""Command line: `kmaker pipeline | backtest | paper | report`.

`pipeline` is what the backtest container runs: download the primary sample, decide, report,
then download the holdout hours and add them to the report, then idle. Every step is
resumable, so a restart after a crash or a reboot continues where it stopped.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from . import backtest, ingest, report, telegram
from .client import Kalshi, KalshiClientError, KalshiError
from .config import PREREG, Settings
from .paper import PaperMaker

log = logging.getLogger("kmaker")


def _client(s: Settings, rate: float | None = None, paper: bool = False) -> Kalshi:
    if paper:  # fail fast, so that the tape watchdog can act within its two minutes
        return Kalshi(s.api_bases, rate=s.rate_paper, timeout=10.0, max_tries=2)
    return Kalshi(s.api_bases, rate=s.rate if rate is None else rate)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _gate_digest(gate: dict, summary: dict) -> str:
    lines = ["kalshi-maker backtest (primary sample)"]
    if not gate.get("valid", True):
        return "\n".join(
            lines + ["NO CONCLUSION, invalid data: " + "; ".join(gate.get("invalid_reasons", []))]
        )
    lines.append(f"pairs tested {gate['pairs_tested']}, qualifying {len(gate['qualifying'])}")
    lines.append(
        "replication check FAILED"
        if summary["replication_fails"]
        else "replication (A, cents per contract): "
        + ", ".join(f"{k} {v['mean_c']:.2f}" for k, v in summary["replication_A_pooled"].items())
    )
    lines += [
        f"{q['variant']} {q['category']} {q['side']} b{q['bucket']}: "
        f"{q['exploration_mean_c']:.2f}c t{q['exploration_t']} / "
        f"{q['confirmation_mean_c']:.2f}c t{q['confirmation_t']}"
        for q in gate["qualifying"][:15]
    ]
    return "\n".join(lines)


def _retry(fn, *args, tries: int = 12, wait_s: float = 300.0):
    """Retry transient failures (API unreachable, 429 or 5xx after the client's own retries,
    file system errors) for about an hour, so that a long download does not burn the
    container's few restarts on network hiccups."""
    for i in range(tries):
        try:
            return fn(*args)
        except KalshiClientError:
            raise
        except (KalshiError, httpx.HTTPError, OSError) as exc:
            if i == tries - 1:
                raise
            log.warning(
                "transient failure: %s; retry %d of %d in %.0f s", exc, i + 1, tries, wait_s
            )
            time.sleep(wait_s)
    return None


def _download(s: Settings, c: Kalshi, residue: int) -> None:
    paths = _retry(ingest.ingest_trades, c, s.data_dir, residue, s.min_free_gb)
    info = _retry(ingest.ingest_markets, c, s.data_dir, paths)
    _retry(ingest.ingest_missing_series, c, s.data_dir)
    ingest.write_manifest(s.data_dir, residue, {**info, "requests": c.requests})


def _first_attempt(data_dir: Path) -> float:
    path = data_dir / "first_decision_attempt.txt"
    if not path.exists():
        tmp = path.with_suffix(".tmp")
        tmp.write_text(f"{time.time():.0f}")
        tmp.replace(path)
    return float(path.read_text())


def _outside_other_reports(now: datetime | None = None) -> float:
    """Seconds to wait so that the DuckDB phase avoids 05:30 to 07:30 UTC, when updown-desk's
    reporter (up to 3 GB) runs on the same 4 GB host."""
    now = now or datetime.now(timezone.utc)
    start = now.replace(hour=5, minute=30, second=0, microsecond=0)
    end = now.replace(hour=7, minute=30, second=0, microsecond=0)
    return (end - now).total_seconds() if start <= now < end else 0.0


def _backtest(s: Settings, residue: int, write_gate: bool, final_attempt: bool) -> dict:
    wait = _outside_other_reports()
    if wait:
        log.info("waiting %.0f s for updown-desk's daily report to finish", wait)
        time.sleep(wait)
    return backtest.run(s.data_dir, s.reports_dir, residue, write_gate, final_attempt)


def cmd_pipeline(s: Settings, holdout: bool, retry_wait_s: float = 86400.0) -> None:
    """Download, decide once, report; then the holdout. A restart resumes and never re-decides.

    If the data checks fail, the download of empty hours and non-final markets is repeated
    every day, and the gate is written as invalid only after 6 days (Amendment 3).
    """
    gate_path = s.data_dir / "gate.json"
    with _client(s) as c:
        if not (s.data_dir / "series.parquet").exists():
            _retry(ingest.ingest_series, c, s.data_dir)
        primary = PREREG.primary_residue
        first = None
        while not gate_path.exists():
            _download(s, c, primary)
            first = first or _first_attempt(s.data_dir)
            final = time.time() - first >= 6 * 86400
            summary = _backtest(s, primary, True, final)
            _write(s.reports_dir / "BACKTEST.md", report.backtest_report(s.reports_dir, s.data_dir))
            if summary["gate_written"]:
                gate = json.loads(gate_path.read_text())
                telegram.send(s.telegram_token, s.telegram_chat, _gate_digest(gate, summary))
                break
            reasons = "; ".join(summary["validity"]["reasons"])
            telegram.send(
                s.telegram_token,
                s.telegram_chat,
                f"kalshi-maker: data checks failed ({reasons}); new download in 24 h",
            )
            time.sleep(retry_wait_s)
        label = f"r{PREREG.holdout_residue}"
        if holdout and not (s.reports_dir / "backtest" / label / "summary.json").exists():
            _download(s, c, PREREG.holdout_residue)
            _backtest(s, PREREG.holdout_residue, False, True)
            _write(s.reports_dir / "BACKTEST.md", report.backtest_report(s.reports_dir, s.data_dir))
            telegram.send(
                s.telegram_token,
                s.telegram_chat,
                "kalshi-maker: holdout hours added to BACKTEST.md",
            )


def pipeline_forever(s: Settings, holdout: bool) -> None:
    """Run the pipeline to completion, then idle; never exit.

    The container restarts only after a reboot or a Docker restart, and then resumes. A
    failure is reported on Telegram and retried after 30 minutes; after four failures in a day
    the pipeline waits a day before trying again, with a message each time.
    """
    failures: list[float] = []
    while True:
        try:
            cmd_pipeline(s, holdout)
            break
        except Exception as exc:
            log.exception("pipeline failed")
            now = time.time()
            failures = [t for t in failures if t > now - 86400] + [now]
            wait = 86400 if len(failures) >= 4 else 1800
            telegram.send(
                s.telegram_token,
                s.telegram_chat,
                f"kalshi-maker pipeline failed ({type(exc).__name__}: {exc}); "
                f"{len(failures)} failure(s) in 24 h, next attempt in {wait // 60:.0f} min",
            )
            time.sleep(wait)
    log.info("pipeline complete, idle")
    while True:
        time.sleep(86400)


def _pending_digest(s: Settings) -> str:
    """Daily message while there is no gate: where the download stands."""
    hours = ingest.sampled_hours(
        PREREG.window_start, PREREG.window_end, PREREG.hour_mod, PREREG.primary_residue
    )
    done = ingest.hour_counts(s.data_dir, PREREG.primary_residue)
    path = s.data_dir / f"hours_r{PREREG.primary_residue}.json"
    age = (time.time() - path.stat().st_mtime) / 3600 if path.exists() else float("nan")
    lines = [
        f"kalshi-maker: no gate yet; {len(done)} of {len(hours)} sampled hours downloaded, "
        f"last progress {age:.1f} h ago"
    ]
    summary = s.reports_dir / "backtest" / "primary" / "summary.json"
    if summary.exists():
        reasons = json.loads(summary.read_text()).get("validity", {}).get("reasons", [])
        if reasons:
            lines.append("data checks failed: " + "; ".join(reasons))
    return "\n".join(lines)


def _series_map(s: Settings, c: Kalshi) -> dict:
    path = s.data_dir / "series.parquet"
    df = ingest.load_series(s.data_dir) if path.exists() else ingest.ingest_series(c, s.data_dir)
    return {
        r.series: (r.category, r.fee_type, r.fee_multiplier) for r in df.itertuples(index=False)
    }


def cmd_paper(s: Settings) -> None:
    gate_path = s.data_dir / "gate.json"
    while not gate_path.exists():
        log.info("no gate yet, waiting for the backtest")
        time.sleep(600)
    gate = json.loads(gate_path.read_text())
    if not gate.get("valid", True) or not gate.get("qualifying") or gate.get("replication_fails"):
        log.info("the gate allows no quoting (invalid data, no pair, or failed replication): idle")
        while True:
            time.sleep(3600)
    with _client(s, paper=True) as c:
        maker = PaperMaker(s, c, gate, _series_map(s, c))
        maker.run_forever()


def cmd_report(s: Settings, loop: bool, hour: int) -> None:
    def once() -> None:
        if not (s.data_dir / "gate.json").exists():
            telegram.send(s.telegram_token, s.telegram_chat, _pending_digest(s))
            return
        text, digest = report.forward_report(s.data_dir)
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _write(s.reports_dir / "forward" / f"{day}.md", text)
        _write(s.reports_dir / "FORWARD.md", text)
        telegram.send(s.telegram_token, s.telegram_chat, digest)

    if not loop:
        once()
        return
    while True:
        now = datetime.now(timezone.utc)
        nxt = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if nxt <= now:
            nxt += timedelta(days=1)
        time.sleep((nxt - now).total_seconds())
        try:
            once()
        except Exception:
            log.exception("forward report failed")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="kmaker")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("pipeline", help="download the sample, decide, report")
    pp.add_argument("--no-holdout", action="store_true")
    bt = sub.add_parser(
        "backtest", help="recompute statistics from downloaded data (never writes the gate)"
    )
    bt.add_argument("--residue", type=int, default=PREREG.primary_residue)
    sub.add_parser("paper", help="run the forward paper maker")
    rp = sub.add_parser("report", help="forward report now, or daily with --loop")
    rp.add_argument("--loop", action="store_true")
    rp.add_argument("--hour", type=int, default=7)
    args = p.parse_args(argv)
    s = Settings()
    logging.basicConfig(level=s.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.cmd == "pipeline":
        pipeline_forever(s, holdout=not args.no_holdout)
    elif args.cmd == "backtest":
        # by hand: statistics only; the gate belongs to the pipeline and its schedule
        backtest.run(s.data_dir, s.reports_dir, args.residue, write_gate=False)
    elif args.cmd == "paper":
        cmd_paper(s)
    elif args.cmd == "report":
        cmd_report(s, args.loop, args.hour)


if __name__ == "__main__":
    main()
