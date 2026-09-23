"""Command line: `kmaker pipeline | backtest | paper | report`.

`pipeline` is what the one-shot container runs: download the primary sample, decide, report,
then download the holdout hours and add them to the report. Every step is resumable, so a
restart after a crash or a reboot continues where it stopped.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import backtest, ingest, report, telegram
from .client import Kalshi
from .config import PREREG, Settings
from .paper import PaperMaker

log = logging.getLogger("kmaker")


def _client(s: Settings) -> Kalshi:
    return Kalshi(s.api_bases, rate=s.rate)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def cmd_pipeline(s: Settings, holdout: bool) -> None:
    with _client(s) as c:
        if not (s.data_dir / "series.parquet").exists():
            ingest.ingest_series(c, s.data_dir)
        residues = [PREREG.primary_residue] + ([PREREG.holdout_residue] if holdout else [])
        for residue in residues:
            paths = ingest.ingest_trades(c, s.data_dir, residue, s.min_free_gb)
            markets = ingest.ingest_markets(c, s.data_dir, paths)
            ingest.ingest_missing_series(c, s.data_dir, markets)
            ingest.write_manifest(
                s.data_dir,
                residue,
                {"hours": len(paths), "markets": len(markets), "requests": c.requests},
            )
            primary = residue == PREREG.primary_residue
            summary = backtest.run(s.data_dir, s.reports_dir, residue, write_gate=primary)
            text = report.backtest_report(s.reports_dir, s.data_dir)
            _write(s.reports_dir / "BACKTEST.md", text)
            if primary:
                gate = json.loads((s.data_dir / "gate.json").read_text())
                lines = [
                    "kalshi-maker backtest (primary sample)",
                    f"pairs tested {gate['pairs_tested']}, qualifying {len(gate['qualifying'])}",
                    "replication check FAILED"
                    if summary["replication_fails"]
                    else "replication check ok: " + json.dumps(summary["replication_A_pooled"]),
                ]
                lines += [
                    f"{q['variant']} {q['category']} {q['side']} b{q['bucket']}: "
                    f"{q['exploration_mean_c']:.2f}c t{q['exploration_t']} / "
                    f"{q['confirmation_mean_c']:.2f}c t{q['confirmation_t']}"
                    for q in gate["qualifying"][:15]
                ]
                telegram.send(s.telegram_token, s.telegram_chat, "\n".join(lines))
            else:
                telegram.send(
                    s.telegram_token,
                    s.telegram_chat,
                    "kalshi-maker: holdout hours added to BACKTEST.md",
                )


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
    if not gate.get("qualifying") or gate.get("replication_fails"):
        log.info("gate has no qualifying pair (or replication failed): idle")
        while True:
            time.sleep(3600)
    with _client(s) as c:
        maker = PaperMaker(s, c, gate, _series_map(s, c))
        maker.run_forever()


def cmd_report(s: Settings, loop: bool, hour: int) -> None:
    def once() -> None:
        if not (s.data_dir / "gate.json").exists():
            log.info("no gate yet, no forward report")
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
    bt = sub.add_parser("backtest", help="recompute statistics from downloaded data")
    bt.add_argument("--residue", type=int, default=PREREG.primary_residue)
    sub.add_parser("paper", help="run the forward paper maker")
    rp = sub.add_parser("report", help="forward report now, or daily with --loop")
    rp.add_argument("--loop", action="store_true")
    rp.add_argument("--hour", type=int, default=7)
    args = p.parse_args(argv)
    s = Settings()
    logging.basicConfig(level=s.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.cmd == "pipeline":
        cmd_pipeline(s, holdout=not args.no_holdout)
    elif args.cmd == "backtest":
        backtest.run(
            s.data_dir,
            s.reports_dir,
            args.residue,
            write_gate=args.residue == PREREG.primary_residue,
        )
        _write(s.reports_dir / "BACKTEST.md", report.backtest_report(s.reports_dir, s.data_dir))
    elif args.cmd == "paper":
        cmd_paper(s)
    elif args.cmd == "report":
        cmd_report(s, args.loop, args.hour)


if __name__ == "__main__":
    main()
