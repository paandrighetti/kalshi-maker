# Pre-registration: the retail-flow premium for a small Kalshi maker

Written on 23 September 2026, before any trade of the sample below was downloaded. The SHA-256
of this file is printed in every report and stored in `gate.json`. The decision rule is what
`kmaker backtest` implements; changing it means changing this file, which changes the hash.

## Question

Takers on Kalshi buy YES and longshots too often, and makers have earned a positive return at
settlement on average. Does that premium survive for a small maker who cannot be first in the
queue and reacts in tens of seconds, after Kalshi's maker fees, on trades that none of the
published studies used?

## Prior evidence

- Becker (2026), 72.1 million Kalshi trades to 25 November 2025: makers +1.12 % excess return,
  takers -1.12 %, gross of fees. Maker minus taker gap by category: finance 0.17 percentage
  points, politics 1.02, sports 2.23, weather 2.57, crypto 2.69, entertainment 4.79, media 7.28,
  world events 7.32. The gap turned in favor of makers after October 2024.
- Burgi, Deng and Whelan (2025), over 300,000 contracts from 2021 to April 2025: contracts
  priced under 10 cents lose about 60 % after fees; makers buying contracts priced 50 cents or
  more earn 2.6 % after fees.
- Bartlett and O'Hara (2026), 41.6 million trades: makers earn 1.91 cents per contract in
  single-name markets and 0.82 in broad-based ones; one-sided order flow predicts maker losses
  in single-name markets.
- Against: on Polymarket's 15-minute crypto markets (September 2026, this project's author),
  fills that empty their price level lose, so a maker at the back of the queue kept nothing.

## Data

- Kalshi public REST API, no authentication: `/series`, `/markets`, `/historical/markets`,
  `/markets/trades`, `/historical/trades`, `/historical/cutoff`.
- Window: trades created from 2025-12-01 00:00 UTC to 2026-09-08 00:00 UTC. The start follows
  the end of Becker's sample; the end leaves a week for short-dated markets to settle.
- Time sample: every trade of the UTC hours whose key `YYYY-MM-DDTHH` has a SHA-256 digest equal
  to 0 modulo 12 (primary sample, about one hour in twelve). Hours equal to 1 modulo 12 form the
  holdout sample, used only after the decision, as described below.
- Exclusions: series whose `category` is `Sports` (institutional market makers, maker fees on
  the main series, most of the volume); multivariate markets (`mve_collection_ticker` set, or a
  series starting with `KXMVE`); block trades; markets whose `result` is not `yes` or `no` when
  downloaded.
- Split: exploration = trades created before 2026-05-01 00:00 UTC; confirmation = trades created
  on or after that time.

## Definitions

- A print is one trade record. A taker order is the set of prints with the same market, the
  same `created_time` to the microsecond and the same `taker_outcome_side`. Its levels are its
  distinct prices, ranked from the best for the taker (ascending YES price when the taker gains
  YES exposure, descending otherwise). The first level is the best price available when the
  order arrived.
- Maker direction: d = -1 when `taker_outcome_side` is `yes` (the maker sold YES exposure),
  d = +1 otherwise. With p the YES price in dollars and o = 1 if the market resolved YES, 0
  otherwise, the maker's settlement profit per contract is d(o - p), minus the maker fee.
- Maker fee per contract: 0.0175 x `fee_multiplier` x p(1 - p) for series whose `fee_type`
  starts with `quadratic_with`, zero otherwise. Rounded up to the cent per fill where a fill
  size is defined (statistic B), unrounded otherwise.
- Tick at price p: the `step` of the market's `price_ranges` interval containing p, 0.01 by
  default.
- Side: `short_yes` (d = -1) or `long_yes` (d = +1). Price bucket of the maker's fill price:
  [0, 0.10), [0.10, 0.30), [0.30, 0.70), [0.70, 0.90), [0.90, 1].

## Statistics, in cents per contract

- A, all makers: every print, weight = contracts, value = d(o - p) - fee. A replication of the
  literature, not a decision statistic.
- B, a small maker that improves the best price by one tick: every taker order, fill
  q = min(order size, 10) at a = first-level price - tick when the taker gains YES exposure,
  + tick otherwise; value = d(o - a) - fee(q, a)/q, weight = q. Orders where a falls outside
  (0, 1) are dropped. B assumes the quote was alone at the improved price, which the tape cannot
  show; the forward test measures it.
- C, a maker at the back of the queue: prints at every level of a taker order except its last
  level (these levels were emptied, so the last order in their queue was filled), weight =
  contracts, value as in A. A lower bound: sweeps are the largest and most informed orders.
- Inference: the mean is the ratio of sums over the cell; its standard error is cluster-robust
  with the G/(G - 1) correction; t = mean / standard error. A cluster is a category and a UTC
  date of market settlement (the trade date when the settlement time is missing), so markets
  sharing a shock on the same day, such as hourly crypto or index markets, count once
  (Amendment 1).

## Cells and decision rule

Cells: category (each category with data, plus all categories pooled) x side x price bucket.
Two tradeable variants: PENNY is decided by B, JOIN by C.

A (variant, cell) pair qualifies if, in the exploration sample and in the confirmation sample
separately: at least 30 clusters, 100 distinct events and 500 contracts, at least 10 clusters
whose total is negative (Amendment 1), mean > 0 and t >= 2. The paper maker
quotes only qualifying pairs. If none qualifies, the conclusion is that a small maker has no
demonstrated edge on Kalshi's non-sports markets, and the paper maker does not quote.

Multiple testing: about 16 category groups, 2 sides, 5 buckets and 2 variants make about 320
tests. Requiring t >= 2 on two disjoint periods caps the expected number of false
qualifications near 320 x 0.023^2, about 0.17, if cells were independent. The number of cells
tested is printed with the result.

Holdout: once the gate is written, the same statistics are computed on the holdout hours. A
qualifying pair whose holdout mean is negative is reported as contradicted. The holdout neither
adds nor removes pairs.

Replication check: if statistic A pooled over all categories is negative in both samples, the
literature does not replicate on this data, and the data handling is audited before any result
is used.

## Forward test (paper)

- Universe: open, non-multivariate markets in the categories of qualifying pairs, expected
  expiration within 7 days, with both a bid and an ask.
- Every cycle (target 20 s), for each qualifying (variant, side): PENNY quotes one tick inside
  the best price when the spread is at least two ticks and joins the best price otherwise; JOIN
  always joins the best price. Size 10 contracts. A quote goes live one second after the book it
  was computed from was received.
- Fills: a taker order printed after the quote went live fills it for min(remaining, volume
  printed at or through the quote price - queue ahead). The queue ahead is the displayed size at
  the quote price when the quote joined it (zero when it improved the price), reduced only by
  traded volume, never by cancellations. A quote crossed by the opposite best price at the next
  book is filled against that best size, less the queue ahead. A quote whose price is no longer
  the target is canceled and replaced with a new queue position.
- Positions are held to settlement. Strategy view: fills in qualifying pairs, at most 100
  contracts per market and variant, 500 USD at risk per event, 5,000 USD in total.
- Success: pooled strategy-view profit per contract > 0 with t >= 2 (clusters as in the
  backtest) once 200 events have settled and at least 10 clusters are negative. A variant is
  abandoned if its mean is negative after 30 days.

## Amendments

Amendment 1, 23 September 2026, before any trade of the sample was downloaded. A run on
synthetic data made two weaknesses of the first version visible, and both concern inference
only:

- Clusters were events. Markets on one underlying settle on the same day across many events
  (every hourly Bitcoin or index market of a day moves with the same path), so event clusters
  treat correlated outcomes as independent and overstate t. Clusters are now a category and a
  settlement date.
- For contracts far from 0.5, the maker loses rarely and heavily. A cell with few losing
  clusters has a variance estimate that has not yet seen the tail, and its t is not credible.
  The usual condition for a normal approximation to a binomial is about ten occurrences of each
  outcome, hence the floor of 10 negative clusters, together with 100 distinct events.

## References

- Bartlett, R. and O'Hara, M. (2026). Adverse Selection in Prediction Markets: Evidence from
  Kalshi. SSRN 6615739.
- Becker, J. (2026). The Microstructure of Wealth Transfer in Prediction Markets. SSRN 7217640.
- Burgi, C., Deng, W. and Whelan, K. (2025). Makers and Takers: The Economics of the Kalshi
  Prediction Market. CEPR Discussion Paper 20631; SSRN 5502658.
- Kalshi. Fee Schedule (maker fee series list) and API documentation (order direction, historical
  data).
