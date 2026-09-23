# kalshi-maker

Does a small, slow maker earn the retail-flow premium on Kalshi? Three studies with tens of
millions of trades find that Kalshi's takers overpay for YES and for longshots, and that makers
earn a positive return at settlement on average (Becker 2026; Burgi, Deng and Whelan 2025;
Bartlett and O'Hara 2026). An average over all makers is not a strategy: the maker who is
first in the queue and reacts in milliseconds collects most of it. This project measures what is
left for a maker who is last in the queue or has to improve the price to be first, reacts in
tens of seconds, and pays Kalshi's maker fees, on trades that none of these studies used. Then
it runs that maker forward on paper.

It follows a negative result on Polymarket's 15-minute crypto markets, where the flow is fast
and informed and the fills that empty their price level lose. Kalshi's non-sports markets
(mentions, entertainment, weather, economics, politics) have a slower, more retail flow, and the
published maker premium is largest there.

## Rules first

[PREREGISTRATION.md](PREREGISTRATION.md) fixes the sample, the statistics, the cells, the
decision rule, the holdout and the forward test before any sample trade was downloaded. It was
the first commit of this repository, and its two amendments, both made before any download, are
logged at its end with their reasons: a synthetic run and an independent review of the code
found weaknesses in the inference and a look-ahead in the selection of markets. Its SHA-256 is
printed in every report and stored in `data/gate.json`; the constants it names live in
`src/kmaker/config.py`, not in `.env`.

## What runs

```
backtest (one shot, resumable)
  ingest    /series, then every trade of the sampled hours (one UTC hour in twelve, chosen by
            hash) from /historical/trades or /markets/trades around Kalshi's cutoff, sports
            series dropped on write, then the markets of those trades
  backtest  DuckDB: taker orders and their levels, statistics A, B and C per
            (category, side, price bucket, sample), clustered by category and settlement date
  checks    no gate if hours came back empty, trades lack a market record, eligible markets
            are not final, or a period has no data (missing data never reads as "no edge")
  gate      pairs that pass in both periods -> data/gate.json, written once, never rewritten
  holdout   the same on another twelfth of the hours, reported, never decides
paper (continuous)
  waits for the gate; every 20 s: new trades from the public tape fill the virtual quotes,
  then the top of book of the active markets moves them (PENNY one tick inside, JOIN at the
  best price with the displayed size ahead); fills and settlements go to data/paper.sqlite
reporter (daily, 07:00 UTC)
  reports/FORWARD.md and a Telegram digest: settled profit per contract by cell, under the
  pre-registered position limits, with clustered t
```

The statistics, in cents per contract, with d = -1 when the taker gained YES exposure and +1
otherwise, o the outcome and p the YES price:

- A, every maker: d(o - p) minus the maker fee, weighted by contracts. The replication.
- B, a maker one tick inside the best price: the first level of each taker order, at most 10
  contracts, one tick worse for the maker. Decides the PENNY variant.
- C, the last order in the queue: only the levels a taker order emptied. Decides the JOIN
  variant. A lower bound, since sweeps are the most informed orders.

Markets are selected on `latest_expiration_time` (on or before 15 September 2026), which is
fixed at listing, rather than on having settled by the download date, which would keep the
markets that resolved early. A pair (variant, category, side, bucket) qualifies when it is
positive with t >= 2 in the exploration period (markets settled before 1 May 2026) and in the
confirmation period (after), each with
at least 30 clusters, 100 events, 500 contracts and 10 losing clusters. A cluster is a category
and a settlement date, so markets that share a shock on one day count once. The paper maker
quotes only qualifying pairs.

## Run

```
cp .env.example .env              # Telegram optional
docker compose up -d --build      # backtest, paper and reporter
docker compose logs -f backtest   # progress of the download, then the verdict
```

`KM_RATE` (download, 6 requests per second) and `KM_RATE_PAPER` (paper maker, 4) keep the two
well under Kalshi's basic limit of about 20 per second together. The backtest's DuckDB work
file needs about 1 GB plus 130 bytes per downloaded trade of free disk (measured: 36 million
synthetic trades in 137 s, 943 MB of memory, 3.7 GB of disk); the download stops below 3 GB.
Transient API failures are retried for about an hour inside the pipeline; if the data checks
fail, the missing parts are downloaded again every day for up to 6 days before the gate is
written as invalid. A failed pipeline sends a Telegram message and is restarted at most three
times; every step resumes where it stopped.

Without Docker: `pip install -e .[dev]`, then `kmaker pipeline`, `kmaker paper`,
`kmaker report`, and `pytest -q`. `KM_DATA_DIR` and `KM_REPORTS_DIR` default to `data/` and
`reports/`. To publish reports, add the crontab line in `scripts/publish_reports.sh`.

## Outputs

- `reports/BACKTEST.md`: verdict, replication of the published premium, sample counts, every
  cell, holdout.
- `reports/backtest/<sample>/`: `cells.csv`, `overall.csv`, `volume.csv`, `calibration.csv`,
  `horizon_expost.csv`, `summary.json`.
- `reports/FORWARD.md` and `reports/forward/YYYY-MM-DD.md`: forward results.
- `data/gate.json`, `data/paper.sqlite` (fills, settlements, cycle log).

## Limits

- The tape has no order book. B assumes the improved quote was alone at its price and that the
  taker order would have traded against it; C only sees levels emptied by sweeps. The forward
  test replaces both assumptions with the live top of book, but not with the full depth.
- Virtual quotes do not move the market. A real quote one tick inside would attract competing
  makers who improve on it, and some takers who would not have traded otherwise.
- Queue ahead only shrinks with traded volume, never with cancellations: conservative for fills,
  and it ignores that a cancellation ahead of a quote moves it forward.
- The forward maker polls: a quote can stand for up to one cycle after the market moved, and is
  then filled against the crossing book. That is the cost of being slow, and it is counted.
- B credits an improved price even where the spread was one tick and no improvement was
  possible; the PENNY rule joins the best price there. The forward universe (the 400 most
  active markets closing within 7 days) is narrower than the backtest's cells, which pool all
  horizons; `horizon_expost.csv` shows how the premium varies with time to settlement.
- The holdout draws other trades on the same markets: it tests the sampling of trades, not new
  outcomes.
- Fee types are today's; Kalshi does not publish their history, and it has added maker fees
  over time, which makes the correction conservative for most series.
- Kalshi restricts access by country. This project reads public market data only and places no
  order.

## References

- Bartlett, R. and O'Hara, M. (2026). Adverse Selection in Prediction Markets: Evidence from
  Kalshi. SSRN 6615739.
- Becker, J. (2026). The Microstructure of Wealth Transfer in Prediction Markets. SSRN 7217640.
- Burgi, C., Deng, W. and Whelan, K. (2025). Makers and Takers: The Economics of the Kalshi
  Prediction Market. CEPR Discussion Paper 20631.
- Cameron, A. C. and Miller, D. L. (2015). A Practitioner's Guide to Cluster-Robust Inference.
  Journal of Human Resources 50(2), 317-372.
- Glosten, L. (1994). Is the electronic open limit order book inevitable? Journal of Finance
  49(4), 1127-1161.
- Kalshi API documentation: order direction, historical data, rate limits; Kalshi fee schedule.
