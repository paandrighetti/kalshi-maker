# History rewrite of 25 September 2026

On 25 September 2026 the author and committer of every commit were set to the repository
owner. The commit messages are unchanged, including the co-author line that credits Claude.
Trees, dates and file contents are unchanged, so the SHA-256 of `PREREGISTRATION.md` printed
in the reports is unaffected. The signatures, which covered the previous identities, were
dropped. Old and new commit ids, oldest first:

| old | new | commit |
|---|---|---|
| 3fcaf68 | 18b8959 | Pre-register the Kalshi maker premium test before downloading any sample trade |
| 74fa21b | 21a87d5 | Amend inference before any download: category-day clusters, floors on events and losing clusters |
| fde014c | fa182de | Tape backtest, forward paper maker and reports for the pre-registered test |
| 9490271 | 08cc61d | Amend the pre-registration after an independent review, before any download |
| 75429bd | d5588fe | Correct the tick example of Amendment 2 before any download |
| 40a9d14 | f108628 | Fix the review findings: memory, cutoff, validity, write-once gate, lost fills |
| e4925ba | ab219bf | Amendment 3 before any download: split periods on latest expiration, not settlement |
| 219d208 | 857b2ed | Fix the second review: period on latest expiration, spillable event counts, no lost fills |
| 75c6717 | 9f275ca | Correct Amendment 3 before any download: how a moved latest expiration is detected |
| 7fc99ce | 2418b84 | Fix the third review: never exit the pipeline, spillable market dedup, sliced catch-up |
| bab735e | f8accef | Keep request URLs and the Telegram token out of the logs; add .dockerignore |
| 3859b28 | 85c1755 | README: check Telegram with exec in the running reporter |
| 9afe1e3 | f57f805 | Digest: count the market download as progress |
| 4f52998 | 2406a3a | config: the period split comment follows Amendment 3 |
| 02976d8 | de09c9b | README: three amendments, split on latest expiration, retry schedule, decision |
| 25b050f | 0672b41 | Backtest decision of 24 September 2026 (primary sample) |
| 100d5ad | 436e3c9 | Amendment 4: two looks for the forward test, t >= 2.28, end at day 60 |
| ba941ec | 6cc67a9 | Holdout market step within memory; alert and back off on repeated starts |
