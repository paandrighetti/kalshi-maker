# Backtest: the retail-flow premium for a small Kalshi maker

Generated 2026-09-24T11:20:36+00:00 from `reports/backtest/primary/`. Pre-registration SHA-256 `02e4f9180ac2b8b08b46401119b2e9bce9614561dbfd912b78dc922045da8f45`.

## Verdict

7 of 289 pre-registered (variant, cell) pairs qualify: positive with t >= 2 in both the exploration and the confirmation samples.

| variant | category | side | bucket | exploration_mean_c | exploration_t | confirmation_mean_c | confirmation_t |
|---|---|---|---|---|---|---|---|
| PENNY | Entertainment | short_yes | [0.00, 0.10) | 3.1023 | 6.68 | 1.7305 | 3.08 |
| PENNY | Entertainment | short_yes | [0.10, 0.30) | 7.8879 | 3.48 | 9.9746 | 5.44 |
| PENNY | Mentions | short_yes | [0.10, 0.30) | 7.1444 | 4.82 | 6.266 | 4.38 |
| PENNY | Mentions | short_yes | [0.30, 0.70) | 14.2088 | 7.3 | 7.8598 | 5.11 |
| PENNY | Politics | short_yes | [0.00, 0.10) | 2.8181 | 2.97 | 3.6412 | 7.8 |
| JOIN | Climate and Weather | short_yes | [0.00, 0.10) | 1.1463 | 2.66 | 1.4576 | 2.79 |
| JOIN | Entertainment | short_yes | [0.10, 0.30) | 10.6929 | 4.87 | 6.4856 | 2.62 |


## Replication of the published maker premium (statistic A, all categories pooled)

| sample | mean, cents per contract | t, maker short YES | t, maker long YES |
|---|---|---|---|
| all | 0.227 | 0.03 | 0.65 |
| confirmation | 0.152 | -0.30 | 0.73 |
| exploration | 0.626 | 1.72 | -0.42 |

The pooled maker premium does not contradict the literature on this sample.

## Sample and validity checks

Sampled hours: 576; empty 0.52% (limit 2%); trades without a market record 0.00% (limit 5%); eligible trades in non-final markets 0.00% (limit 1%). Markets settled more than a day after their latest expiration, which would reveal a moved field: 1487.

| count | value |
|---|---|
| events | 43393 |
| levels | 28674589 |
| markets | 230739 |
| markets_settled_after_latest_expiration | 1487 |
| markets_without_settlement_time | 0 |
| orders | 24149206 |
| trades | 52975705 |
| trades_block | 2 |
| trades_late_expiration | 1270909 |
| trades_multivariate | 9967010 |
| trades_not_binary | 12111 |
| trades_not_final | 5 |
| trades_ok | 41722550 |
| trades_unknown_series | 3118 |

| category | sample | events | markets | contracts | taker_yes_share |
|---|---|---|---|---|---|
| Climate and Weather | confirmation | 6332 | 34742 | 34564050.509997144 | 0.633 |
| Climate and Weather | exploration | 3403 | 17812 | 32926430.57999996 | 0.649 |
| Commodities | confirmation | 1907 | 19289 | 66856279.48999539 | 0.532 |
| Commodities | exploration | 168 | 2371 | 3498552.899999997 | 0.577 |
| Companies | confirmation | 1 | 1 | 4678.81 | 0.206 |
| Companies | exploration | 16 | 52 | 1,376,065 | 0.575 |
| Crypto | confirmation | 14138 | 43459 | 2012035991.7279696 | 0.515 |
| Crypto | exploration | 7753 | 30613 | 284650585.4099966 | 0.534 |
| Economics | confirmation | 903 | 6038 | 13175087.78999989 | 0.661 |
| Economics | exploration | 283 | 1574 | 9771189.47 | 0.637 |
| Elections | confirmation | 112 | 414 | 6549284.529999993 | 0.570 |
| Elections | exploration | 29 | 100 | 2,019,666 | 0.636 |
| Entertainment | confirmation | 1330 | 7226 | 19230271.31999931 | 0.664 |
| Entertainment | exploration | 1116 | 5019 | 12416825.469999988 | 0.732 |
| Financials | confirmation | 1758 | 18876 | 18623727.030000005 | 0.528 |
| Financials | exploration | 617 | 5053 | 7609322.93 | 0.530 |
| Health | exploration | 14 | 20 | 21,454 | 0.616 |
| Mentions | confirmation | 1204 | 17971 | 39144217.08999746 | 0.645 |
| Mentions | exploration | 1136 | 15064 | 43916143.21999989 | 0.720 |
| Politics | confirmation | 498 | 2005 | 13677298.439999953 | 0.602 |
| Politics | exploration | 382 | 1085 | 16410866.349999992 | 0.487 |
| Science and Technology | confirmation | 261 | 1386 | 4412389.180000009 | 0.702 |
| Science and Technology | exploration | 113 | 526 | 4632265.150000001 | 0.744 |
| Social | confirmation | 3 | 5 | 14,559 | 0.453 |
| Social | exploration | 8 | 17 | 32,344 | 0.707 |
| Transportation | exploration | 1 | 1 | 432 | 0.912 |
| World | confirmation | 1 | 1 | 47.900000000000006 | 1.000 |
| World | exploration | 11 | 19 | 10,308 | 0.749 |

## By category and side, all buckets (cents per contract)

| stat | category | side | events_confirmation | events_exploration | mean_c_confirmation | mean_c_exploration | t_confirmation | t_exploration |
|---|---|---|---|---|---|---|---|---|
| A | ALL | long_yes | 26,625 | 13,684 | 0.60 | -0.35 | 0.73 | -0.42 |
| A | ALL | short_yes | 27,715 | 14,620 | -0.25 | 1.35 | -0.30 | 1.72 |
| A | Climate and Weather | long_yes | 6,126 | 3,293 | -0.79 | -0.30 | -2.76 | -0.44 |
| A | Climate and Weather | short_yes | 6,234 | 3,340 | 0.75 | 1.34 | 3.31 | 4.86 |
| A | Commodities | long_yes | 1,880 | 151 | -0.11 | -4.15 | -0.11 | -0.77 |
| A | Commodities | short_yes | 1,881 | 168 | 0.99 | 9.30 | 1.04 | 2.55 |
| A | Companies | long_yes | 1 | 15 | -2.08 | -8.38 | n/a | -3.18 |
| A | Companies | short_yes | 1 | 12 | 6.36 | 9.66 | n/a | 2.85 |
| A | Crypto | long_yes | 13,345 | 7,055 | 0.71 | -0.14 | 0.80 | -0.13 |
| A | Crypto | short_yes | 13,910 | 7,589 | -0.46 | 0.89 | -0.49 | 0.74 |
| A | Economics | long_yes | 808 | 257 | -4.92 | -2.52 | -1.82 | -1.25 |
| A | Economics | short_yes | 852 | 275 | 0.97 | 2.31 | 0.86 | 2.59 |
| A | Elections | long_yes | 106 | 26 | 2.38 | -4.31 | 0.42 | -0.91 |
| A | Elections | short_yes | 104 | 25 | -3.05 | 4.48 | -0.47 | 0.54 |
| A | Entertainment | long_yes | 1,020 | 863 | -0.28 | 0.42 | -0.33 | 0.23 |
| A | Entertainment | short_yes | 1,218 | 1,029 | 1.83 | 1.87 | 2.92 | 2.19 |
| A | Financials | long_yes | 1,497 | 499 | 0.73 | -4.30 | 0.32 | -1.43 |
| A | Financials | short_yes | 1,600 | 587 | 0.33 | 1.80 | 0.14 | 0.63 |
| A | Health | long_yes | nan | 10 | n/a | -5.56 | n/a | -2.12 |
| A | Health | short_yes | nan | 12 | n/a | 6.47 | n/a | 3.51 |
| A | Mentions | long_yes | 1,121 | 1,056 | -0.67 | -1.99 | -1.08 | -1.94 |
| A | Mentions | short_yes | 1,195 | 1,126 | 2.53 | 2.93 | 3.36 | 3.24 |
| A | Politics | long_yes | 480 | 344 | -4.31 | 2.50 | -1.73 | 0.70 |
| A | Politics | short_yes | 476 | 330 | 4.40 | -0.93 | 2.15 | -0.18 |
| A | Science and Technology | long_yes | 239 | 97 | -3.68 | 0.33 | -2.80 | 0.11 |
| A | Science and Technology | short_yes | 241 | 110 | 2.12 | 1.56 | 1.82 | 1.00 |
| A | Social | long_yes | 2 | 7 | -3.60 | -0.12 | -18.42 | -0.04 |
| A | Social | short_yes | 2 | 8 | -14.72 | 5.29 | -8.91 | 3.16 |
| A | Transportation | long_yes | nan | 1 | n/a | -6.42 | n/a | n/a |
| A | Transportation | short_yes | nan | 1 | n/a | 18.88 | n/a | n/a |
| A | World | long_yes | nan | 10 | n/a | -3.13 | n/a | -15.79 |
| A | World | short_yes | 1 | 8 | 6.08 | 4.76 | n/a | 91.31 |
| B | ALL | long_yes | 26,354 | 13,495 | -0.12 | -1.32 | -0.15 | -1.50 |
| B | ALL | short_yes | 27,283 | 14,379 | -1.14 | 0.89 | -1.39 | 0.99 |
| B | Climate and Weather | long_yes | 6,023 | 3,200 | -2.18 | -0.92 | -7.75 | -3.95 |
| B | Climate and Weather | short_yes | 6,116 | 3,256 | -1.20 | 0.13 | -4.26 | 0.44 |
| B | Commodities | long_yes | 1,878 | 151 | -1.23 | -8.39 | -1.17 | -2.41 |
| B | Commodities | short_yes | 1,880 | 167 | -0.50 | 8.16 | -0.49 | 2.13 |
| B | Companies | long_yes | 1 | 15 | -5.75 | -8.35 | n/a | -1.76 |
| B | Companies | short_yes | 1 | 12 | 5.06 | 16.02 | n/a | 11.75 |
| B | Crypto | long_yes | 13,263 | 7,020 | 0.10 | -1.00 | 0.11 | -0.91 |
| B | Crypto | short_yes | 13,710 | 7,509 | -1.43 | -0.66 | -1.53 | -0.57 |
| B | Economics | long_yes | 803 | 255 | -3.00 | -5.85 | -1.60 | -2.90 |
| B | Economics | short_yes | 850 | 273 | 1.80 | 7.21 | 0.89 | 3.25 |
| B | Elections | long_yes | 106 | 26 | 4.50 | 2.45 | 0.67 | 0.21 |
| B | Elections | short_yes | 103 | 25 | 1.00 | 2.01 | 0.15 | 0.22 |
| B | Entertainment | long_yes | 992 | 848 | -1.38 | -3.14 | -1.23 | -2.01 |
| B | Entertainment | short_yes | 1,185 | 1,009 | 2.93 | 4.33 | 1.91 | 2.75 |
| B | Financials | long_yes | 1,493 | 496 | -0.99 | -2.00 | -0.64 | -0.66 |
| B | Financials | short_yes | 1,591 | 580 | -2.62 | 2.25 | -1.64 | 0.84 |
| B | Health | long_yes | nan | 10 | n/a | -10.06 | n/a | -1.63 |
| B | Health | short_yes | nan | 12 | n/a | 6.42 | n/a | 2.75 |
| B | Mentions | long_yes | 1,079 | 1,020 | -5.20 | -5.66 | -4.77 | -4.98 |
| B | Mentions | short_yes | 1,128 | 1,088 | 5.75 | 9.12 | 5.47 | 7.05 |
| B | Politics | long_yes | 476 | 342 | -4.74 | 6.21 | -1.53 | 1.00 |
| B | Politics | short_yes | 475 | 322 | 4.64 | -0.53 | 1.58 | -0.07 |
| B | Science and Technology | long_yes | 238 | 94 | -4.17 | -2.72 | -2.28 | -0.92 |
| B | Science and Technology | short_yes | 241 | 109 | 1.41 | 0.91 | 0.70 | 0.46 |
| B | Social | long_yes | 2 | 7 | -11.30 | -6.42 | -6.36 | -1.51 |
| B | Social | short_yes | 2 | 8 | -22.02 | 6.09 | -8.48 | 2.86 |
| B | Transportation | long_yes | nan | 1 | n/a | -8.67 | n/a | n/a |
| B | Transportation | short_yes | nan | 1 | n/a | 16.60 | n/a | n/a |
| B | World | long_yes | nan | 10 | n/a | -4.88 | n/a | n/a |
| B | World | short_yes | 1 | 8 | 5.19 | 2.47 | n/a | 2.86 |
| C | ALL | long_yes | 21,467 | 10,117 | 0.74 | -0.07 | 0.90 | -0.07 |
| C | ALL | short_yes | 22,977 | 11,157 | -0.47 | 1.97 | -0.55 | 2.03 |
| C | Climate and Weather | long_yes | 4,915 | 2,642 | -1.55 | -0.87 | -2.48 | -1.47 |
| C | Climate and Weather | short_yes | 5,474 | 2,819 | 1.06 | 2.36 | 2.26 | 4.01 |
| C | Commodities | long_yes | 1,557 | 116 | 0.34 | -4.25 | 0.35 | -0.61 |
| C | Commodities | short_yes | 1,613 | 138 | 0.75 | 12.64 | 0.78 | 2.26 |
| C | Companies | long_yes | 1 | 5 | -5.00 | -11.57 | n/a | -5.30 |
| C | Companies | short_yes | 1 | 9 | 5.07 | -2.46 | n/a | -0.36 |
| C | Crypto | long_yes | 11,432 | 5,248 | 0.87 | 0.36 | 0.99 | 0.28 |
| C | Crypto | short_yes | 11,863 | 5,681 | -0.66 | 1.48 | -0.71 | 1.09 |
| C | Economics | long_yes | 528 | 190 | -4.56 | -7.21 | -1.13 | -1.88 |
| C | Economics | short_yes | 603 | 227 | -1.76 | 3.53 | -0.86 | 1.79 |
| C | Elections | long_yes | 86 | 16 | 0.55 | -1.47 | 0.06 | -0.13 |
| C | Elections | short_yes | 77 | 17 | -7.88 | -16.21 | -0.96 | -0.80 |
| C | Entertainment | long_yes | 644 | 501 | 0.07 | 0.88 | 0.04 | 0.19 |
| C | Entertainment | short_yes | 787 | 631 | 2.11 | 2.79 | 1.57 | 1.26 |
| C | Financials | long_yes | 800 | 219 | 3.67 | 15.14 | 1.44 | 1.29 |
| C | Financials | short_yes | 926 | 307 | 1.21 | 3.94 | 0.48 | 1.12 |
| C | Health | long_yes | nan | 4 | n/a | -19.12 | n/a | -2.20 |
| C | Health | short_yes | nan | 5 | n/a | 10.71 | n/a | 1.74 |
| C | Mentions | long_yes | 967 | 875 | -2.86 | -4.29 | -2.17 | -2.30 |
| C | Mentions | short_yes | 1,073 | 987 | 2.85 | 4.42 | 2.00 | 3.26 |
| C | Politics | long_yes | 387 | 228 | -5.10 | 0.93 | -1.96 | 0.18 |
| C | Politics | short_yes | 374 | 240 | 4.95 | 0.35 | 2.15 | 0.08 |
| C | Science and Technology | long_yes | 149 | 64 | -6.96 | 5.21 | -1.58 | 0.70 |
| C | Science and Technology | short_yes | 184 | 82 | 4.66 | 1.55 | 1.19 | 0.43 |
| C | Social | long_yes | 1 | 6 | 20.29 | 0.94 | n/a | 0.18 |
| C | Social | short_yes | 2 | 7 | -1.76 | 2.71 | -1.49 | 1.76 |
| C | Transportation | long_yes | nan | 1 | n/a | -7.00 | n/a | n/a |
| C | Transportation | short_yes | nan | 1 | n/a | 19.31 | n/a | n/a |
| C | World | long_yes | nan | 2 | n/a | -9.61 | n/a | n/a |
| C | World | short_yes | nan | 6 | n/a | 6.17 | n/a | n/a |

## Every cell (statistics B and C decide PENNY and JOIN)

`rows` counts price levels of taker orders for A and C, and taker orders for B.

| stat | sample | category | side | bucket | clusters | events | losing | contracts | rows | mean_c | se_c | t |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | confirmation | ALL | long_yes | [0.00, 0.10) | 1159 | 18712 | 944 | 177586649 | 1752926 | 0.837 | 0.615 | 1.36 |
| A | exploration | ALL | long_yes | [0.00, 0.10) | 894 | 9205 | 717 | 34639946 | 347324 | -0.687 | 0.356 | -1.93 |
| A | confirmation | ALL | long_yes | [0.10, 0.30) | 1188 | 19213 | 800 | 151551164 | 1803835 | -0.050 | 1.268 | -0.04 |
| A | exploration | ALL | long_yes | [0.10, 0.30) | 875 | 9561 | 613 | 29220551 | 441311 | -2.453 | 1.174 | -2.09 |
| A | confirmation | ALL | long_yes | [0.30, 0.70) | 1227 | 22037 | 650 | 369978150 | 4310493 | 0.560 | 1.276 | 0.44 |
| A | exploration | ALL | long_yes | [0.30, 0.70) | 863 | 10615 | 487 | 50995282 | 867881 | -0.414 | 1.677 | -0.25 |
| A | confirmation | ALL | long_yes | [0.70, 0.90) | 1124 | 15139 | 394 | 164465059 | 1727579 | 1.205 | 1.305 | 0.92 |
| A | exploration | ALL | long_yes | [0.70, 0.90) | 822 | 7022 | 251 | 26533679 | 362160 | 1.065 | 1.334 | 0.80 |
| A | confirmation | ALL | long_yes | [0.90, 1.00] | 1099 | 14379 | 162 | 198451391 | 1627277 | 0.435 | 0.402 | 1.08 |
| A | exploration | ALL | long_yes | [0.90, 1.00] | 795 | 6767 | 116 | 37863866 | 286544 | 0.680 | 0.421 | 1.62 |
| A | confirmation | ALL | short_yes | [0.00, 0.10) | 1154 | 18107 | 165 | 247736561 | 1896177 | -0.151 | 0.543 | -0.28 |
| A | exploration | ALL | short_yes | [0.00, 0.10) | 906 | 9543 | 104 | 77688849 | 429142 | 1.049 | 0.328 | 3.20 |
| A | confirmation | ALL | short_yes | [0.10, 0.30) | 1203 | 18894 | 396 | 191023044 | 2088316 | 0.339 | 1.205 | 0.28 |
| A | exploration | ALL | short_yes | [0.10, 0.30) | 913 | 10161 | 237 | 39981351 | 548156 | 2.223 | 1.398 | 1.59 |
| A | confirmation | ALL | short_yes | [0.30, 0.70) | 1243 | 22920 | 617 | 410828047 | 4989439 | -0.347 | 1.354 | -0.26 |
| A | exploration | ALL | short_yes | [0.30, 0.70) | 901 | 11488 | 373 | 65165876 | 1113636 | 2.061 | 1.663 | 1.24 |
| A | confirmation | ALL | short_yes | [0.70, 0.90) | 1191 | 17326 | 748 | 146582138 | 1767866 | -1.055 | 1.394 | -0.76 |
| A | exploration | ALL | short_yes | [0.70, 0.90) | 846 | 8177 | 505 | 28226736 | 411386 | 0.016 | 1.305 | 0.01 |
| A | confirmation | ALL | short_yes | [0.90, 1.00] | 1153 | 16078 | 917 | 170085680 | 1627446 | -0.139 | 0.459 | -0.30 |
| A | exploration | ALL | short_yes | [0.90, 1.00] | 843 | 7471 | 613 | 28976315 | 275695 | 0.691 | 0.545 | 1.27 |
| A | confirmation | Climate and Weather | long_yes | [0.00, 0.10) | 143 | 5509 | 105 | 4906736 | 121528 | -0.426 | 0.294 | -1.45 |
| A | exploration | Climate and Weather | long_yes | [0.00, 0.10) | 141 | 2916 | 96 | 3560387 | 78157 | 0.981 | 0.703 | 1.40 |
| A | confirmation | Climate and Weather | long_yes | [0.10, 0.30) | 142 | 4854 | 88 | 2320327 | 112230 | -0.338 | 0.853 | -0.40 |
| A | exploration | Climate and Weather | long_yes | [0.10, 0.30) | 141 | 2787 | 81 | 2006297 | 82310 | -0.436 | 0.932 | -0.47 |
| A | confirmation | Climate and Weather | long_yes | [0.30, 0.70) | 142 | 4855 | 86 | 2140926 | 124750 | -2.890 | 0.921 | -3.14 |
| A | exploration | Climate and Weather | long_yes | [0.30, 0.70) | 140 | 2609 | 69 | 1585704 | 74775 | -0.977 | 1.148 | -0.85 |
| A | confirmation | Climate and Weather | long_yes | [0.70, 0.90) | 137 | 2396 | 62 | 665381 | 30340 | -3.069 | 2.386 | -1.29 |
| A | exploration | Climate and Weather | long_yes | [0.70, 0.90) | 133 | 1051 | 48 | 470324 | 16172 | 3.217 | 2.165 | 1.49 |
| A | confirmation | Climate and Weather | long_yes | [0.90, 1.00] | 137 | 3143 | 29 | 2667820 | 27351 | 0.395 | 0.397 | 1.00 |
| A | exploration | Climate and Weather | long_yes | [0.90, 1.00] | 129 | 1629 | 19 | 3942497 | 17403 | -1.539 | 1.908 | -0.81 |
| A | confirmation | Climate and Weather | short_yes | [0.00, 0.10) | 142 | 5264 | 22 | 11857278 | 112027 | 0.840 | 0.222 | 3.78 |
| A | exploration | Climate and Weather | short_yes | [0.00, 0.10) | 141 | 3035 | 26 | 14032126 | 81315 | 0.761 | 0.177 | 4.31 |
| A | confirmation | Climate and Weather | short_yes | [0.10, 0.30) | 142 | 4826 | 54 | 2792166 | 114251 | 0.610 | 0.828 | 0.74 |
| A | exploration | Climate and Weather | short_yes | [0.10, 0.30) | 141 | 2874 | 44 | 2594411 | 85161 | 2.520 | 0.869 | 2.90 |
| A | confirmation | Climate and Weather | short_yes | [0.30, 0.70) | 143 | 5169 | 70 | 3596874 | 191143 | 0.263 | 0.633 | 0.42 |
| A | exploration | Climate and Weather | short_yes | [0.30, 0.70) | 141 | 2797 | 62 | 2773480 | 105276 | 2.174 | 1.333 | 1.63 |
| A | confirmation | Climate and Weather | short_yes | [0.70, 0.90) | 141 | 2983 | 83 | 1290612 | 61122 | 0.866 | 1.733 | 0.50 |
| A | exploration | Climate and Weather | short_yes | [0.70, 0.90) | 134 | 1287 | 80 | 723476 | 23665 | 0.647 | 2.035 | 0.32 |
| A | confirmation | Climate and Weather | short_yes | [0.90, 1.00] | 139 | 3037 | 101 | 2325932 | 48997 | 1.141 | 0.885 | 1.29 |
| A | exploration | Climate and Weather | short_yes | [0.90, 1.00] | 133 | 1190 | 98 | 1237728 | 15796 | 4.047 | 3.006 | 1.35 |
| A | confirmation | Commodities | long_yes | [0.00, 0.10) | 111 | 1317 | 89 | 6358275 | 72995 | 0.059 | 0.472 | 0.13 |
| A | exploration | Commodities | long_yes | [0.00, 0.10) | 54 | 114 | 40 | 283399 | 5413 | 1.982 | 4.529 | 0.44 |
| A | confirmation | Commodities | long_yes | [0.10, 0.30) | 112 | 1473 | 70 | 4987906 | 97506 | 0.719 | 1.772 | 0.41 |
| A | exploration | Commodities | long_yes | [0.10, 0.30) | 54 | 125 | 41 | 257775 | 5126 | -8.655 | 2.587 | -3.35 |
| A | confirmation | Commodities | long_yes | [0.30, 0.70) | 113 | 1755 | 54 | 10381704 | 223943 | -0.525 | 1.961 | -0.27 |
| A | exploration | Commodities | long_yes | [0.30, 0.70) | 51 | 133 | 32 | 391700 | 8884 | -11.362 | 7.945 | -1.43 |
| A | confirmation | Commodities | long_yes | [0.70, 0.90) | 110 | 1390 | 39 | 4504434 | 87197 | -1.256 | 1.967 | -0.64 |
| A | exploration | Commodities | long_yes | [0.70, 0.90) | 43 | 104 | 21 | 342041 | 3975 | -0.034 | 9.659 | -0.00 |
| A | confirmation | Commodities | long_yes | [0.90, 1.00] | 109 | 1138 | 18 | 5063338 | 62224 | 0.700 | 0.683 | 1.02 |
| A | exploration | Commodities | long_yes | [0.90, 1.00] | 34 | 77 | 12 | 205943 | 2074 | -0.068 | 2.600 | -0.03 |
| A | confirmation | Commodities | short_yes | [0.00, 0.10) | 111 | 1150 | 20 | 5687415 | 59082 | 1.258 | 0.521 | 2.42 |
| A | exploration | Commodities | short_yes | [0.00, 0.10) | 48 | 98 | 6 | 378927 | 3598 | 2.802 | 1.155 | 2.43 |
| A | confirmation | Commodities | short_yes | [0.10, 0.30) | 113 | 1402 | 44 | 5147065 | 91719 | -1.683 | 1.973 | -0.85 |
| A | exploration | Commodities | short_yes | [0.10, 0.30) | 53 | 127 | 5 | 394344 | 7119 | 8.862 | 2.518 | 3.52 |
| A | confirmation | Commodities | short_yes | [0.30, 0.70) | 114 | 1797 | 57 | 12535530 | 273222 | 1.203 | 1.829 | 0.66 |
| A | exploration | Commodities | short_yes | [0.30, 0.70) | 55 | 158 | 17 | 605744 | 15665 | 14.152 | 6.900 | 2.05 |
| A | confirmation | Commodities | short_yes | [0.70, 0.90) | 113 | 1518 | 67 | 5849018 | 115021 | 3.495 | 1.951 | 1.79 |
| A | exploration | Commodities | short_yes | [0.70, 0.90) | 49 | 133 | 19 | 323681 | 6302 | 16.616 | 8.105 | 2.05 |
| A | confirmation | Commodities | short_yes | [0.90, 1.00] | 110 | 1332 | 83 | 6341595 | 79857 | 0.205 | 0.583 | 0.35 |
| A | exploration | Commodities | short_yes | [0.90, 1.00] | 39 | 111 | 24 | 314998 | 2925 | 0.847 | 2.036 | 0.42 |
| A | confirmation | Companies | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 3702 | 9 | -2.040 | n/a | n/a |
| A | exploration | Companies | long_yes | [0.00, 0.10) | 3 | 14 | 3 | 11909 | 92 | -3.783 | 2.228 | -1.70 |
| A | confirmation | Companies | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 15 | 1 | -11.000 | n/a | n/a |
| A | exploration | Companies | long_yes | [0.10, 0.30) | 3 | 3 | 2 | 309149 | 695 | -14.803 | 0.762 | -19.42 |
| A | exploration | Companies | long_yes | [0.30, 0.70) | 2 | 2 | 1 | 98489 | 862 | -12.898 | 7.717 | -1.67 |
| A | exploration | Companies | long_yes | [0.70, 0.90) | 2 | 2 | 0 | 32362 | 271 | 15.102 | 10.001 | 1.51 |
| A | exploration | Companies | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 133247 | 366 | 3.757 | n/a | n/a |
| A | confirmation | Companies | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 907 | 15 | 5.719 | n/a | n/a |
| A | exploration | Companies | short_yes | [0.00, 0.10) | 3 | 10 | 0 | 23675 | 201 | 4.584 | 0.395 | 11.59 |
| A | confirmation | Companies | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 55 | 2 | 16.982 | n/a | n/a |
| A | exploration | Companies | short_yes | [0.10, 0.30) | 3 | 5 | 1 | 508006 | 2452 | 13.745 | 3.940 | 3.49 |
| A | exploration | Companies | short_yes | [0.30, 0.70) | 2 | 2 | 1 | 129533 | 2107 | 13.217 | 2.388 | 5.53 |
| A | exploration | Companies | short_yes | [0.70, 0.90) | 2 | 2 | 2 | 54231 | 440 | -19.330 | 2.791 | -6.92 |
| A | exploration | Companies | short_yes | [0.90, 1.00] | 2 | 2 | 1 | 75464 | 372 | -1.472 | 0.052 | -28.50 |
| A | confirmation | Crypto | long_yes | [0.00, 0.10) | 129 | 8330 | 86 | 155335528 | 1477423 | 0.973 | 0.702 | 1.39 |
| A | exploration | Crypto | long_yes | [0.00, 0.10) | 131 | 4070 | 101 | 23049046 | 215180 | -0.684 | 0.500 | -1.37 |
| A | confirmation | Crypto | long_yes | [0.10, 0.30) | 132 | 9417 | 76 | 138511970 | 1512443 | 0.127 | 1.388 | 0.09 |
| A | exploration | Crypto | long_yes | [0.10, 0.30) | 131 | 4810 | 89 | 22387873 | 301541 | -2.152 | 1.400 | -1.54 |
| A | confirmation | Crypto | long_yes | [0.30, 0.70) | 136 | 11855 | 64 | 349669977 | 3826430 | 0.710 | 1.352 | 0.53 |
| A | exploration | Crypto | long_yes | [0.30, 0.70) | 133 | 6004 | 70 | 43329127 | 696284 | 0.340 | 1.924 | 0.18 |
| A | confirmation | Crypto | long_yes | [0.70, 0.90) | 131 | 8604 | 49 | 154783134 | 1546773 | 1.291 | 1.388 | 0.93 |
| A | exploration | Crypto | long_yes | [0.70, 0.90) | 131 | 4298 | 43 | 22443040 | 299718 | 0.524 | 1.526 | 0.34 |
| A | confirmation | Crypto | long_yes | [0.90, 1.00] | 131 | 7611 | 29 | 176543807 | 1472094 | 0.439 | 0.447 | 0.98 |
| A | exploration | Crypto | long_yes | [0.90, 1.00] | 130 | 3507 | 25 | 21315399 | 214797 | 0.873 | 0.598 | 1.46 |
| A | confirmation | Crypto | short_yes | [0.00, 0.10) | 129 | 8361 | 36 | 195298476 | 1594669 | -0.416 | 0.677 | -0.61 |
| A | exploration | Crypto | short_yes | [0.00, 0.10) | 131 | 4136 | 24 | 26446171 | 227778 | 1.043 | 0.511 | 2.04 |
| A | confirmation | Crypto | short_yes | [0.10, 0.30) | 132 | 9092 | 59 | 172477768 | 1726472 | 0.103 | 1.331 | 0.08 |
| A | exploration | Crypto | short_yes | [0.10, 0.30) | 133 | 4881 | 40 | 28231371 | 332945 | 1.286 | 1.731 | 0.74 |
| A | confirmation | Crypto | short_yes | [0.30, 0.70) | 136 | 11926 | 71 | 382937008 | 4263584 | -0.513 | 1.455 | -0.35 |
| A | exploration | Crypto | short_yes | [0.30, 0.70) | 134 | 6294 | 64 | 52818467 | 797429 | 1.070 | 2.002 | 0.53 |
| A | confirmation | Crypto | short_yes | [0.70, 0.90) | 136 | 9406 | 87 | 133988246 | 1504277 | -1.372 | 1.523 | -0.90 |
| A | exploration | Crypto | short_yes | [0.70, 0.90) | 132 | 4861 | 84 | 23298004 | 323185 | 0.257 | 1.552 | 0.17 |
| A | confirmation | Crypto | short_yes | [0.90, 1.00] | 131 | 8350 | 100 | 152490077 | 1440530 | -0.208 | 0.502 | -0.41 |
| A | exploration | Crypto | short_yes | [0.90, 1.00] | 131 | 4253 | 92 | 21332087 | 219648 | 0.398 | 0.619 | 0.64 |
| A | confirmation | Economics | long_yes | [0.00, 0.10) | 139 | 556 | 125 | 1433631 | 5753 | -1.882 | 0.477 | -3.95 |
| A | exploration | Economics | long_yes | [0.00, 0.10) | 81 | 195 | 74 | 1258435 | 2673 | -2.365 | 0.302 | -7.82 |
| A | confirmation | Economics | long_yes | [0.10, 0.30) | 141 | 556 | 104 | 528626 | 7161 | -2.519 | 4.431 | -0.57 |
| A | exploration | Economics | long_yes | [0.10, 0.30) | 83 | 170 | 66 | 292083 | 2464 | -7.610 | 5.280 | -1.44 |
| A | confirmation | Economics | long_yes | [0.30, 0.70) | 137 | 557 | 81 | 779766 | 11494 | -20.115 | 8.027 | -2.51 |
| A | exploration | Economics | long_yes | [0.30, 0.70) | 78 | 156 | 50 | 391381 | 4027 | -15.060 | 6.315 | -2.38 |
| A | confirmation | Economics | long_yes | [0.70, 0.90) | 133 | 424 | 41 | 525029 | 6236 | 1.130 | 6.378 | 0.18 |
| A | exploration | Economics | long_yes | [0.70, 0.90) | 77 | 147 | 19 | 336097 | 2235 | -6.749 | 9.627 | -0.70 |
| A | confirmation | Economics | long_yes | [0.90, 1.00] | 133 | 372 | 23 | 1200234 | 5572 | -2.384 | 2.829 | -0.84 |
| A | exploration | Economics | long_yes | [0.90, 1.00] | 70 | 126 | 7 | 1267180 | 2972 | 3.504 | 0.602 | 5.82 |
| A | confirmation | Economics | short_yes | [0.00, 0.10) | 136 | 465 | 14 | 4398822 | 11121 | 1.728 | 0.315 | 5.48 |
| A | exploration | Economics | short_yes | [0.00, 0.10) | 84 | 199 | 4 | 3836766 | 8896 | 2.785 | 0.146 | 19.07 |
| A | confirmation | Economics | short_yes | [0.10, 0.30) | 137 | 548 | 37 | 971380 | 11542 | 6.971 | 2.899 | 2.41 |
| A | exploration | Economics | short_yes | [0.10, 0.30) | 79 | 188 | 15 | 639290 | 6188 | 8.530 | 3.172 | 2.69 |
| A | confirmation | Economics | short_yes | [0.30, 0.70) | 140 | 638 | 64 | 888799 | 18777 | -0.792 | 5.669 | -0.14 |
| A | exploration | Economics | short_yes | [0.30, 0.70) | 82 | 188 | 32 | 527207 | 8210 | 5.205 | 6.664 | 0.78 |
| A | confirmation | Economics | short_yes | [0.70, 0.90) | 136 | 563 | 96 | 803683 | 10299 | -2.968 | 5.396 | -0.55 |
| A | exploration | Economics | short_yes | [0.70, 0.90) | 81 | 170 | 55 | 348447 | 2893 | -6.003 | 3.873 | -1.55 |
| A | confirmation | Economics | short_yes | [0.90, 1.00] | 141 | 562 | 118 | 1645117 | 6685 | -1.707 | 1.120 | -1.52 |
| A | exploration | Economics | short_yes | [0.90, 1.00] | 83 | 177 | 68 | 874303 | 3289 | -2.724 | 1.027 | -2.65 |
| A | confirmation | Elections | long_yes | [0.00, 0.10) | 50 | 73 | 40 | 503748 | 1948 | 18.512 | 10.589 | 1.75 |
| A | exploration | Elections | long_yes | [0.00, 0.10) | 14 | 23 | 12 | 347092 | 574 | -3.414 | 0.835 | -4.09 |
| A | confirmation | Elections | long_yes | [0.10, 0.30) | 54 | 73 | 38 | 240950 | 1427 | 7.112 | 10.313 | 0.69 |
| A | exploration | Elections | long_yes | [0.10, 0.30) | 11 | 11 | 8 | 243827 | 484 | -8.307 | 7.032 | -1.18 |
| A | confirmation | Elections | long_yes | [0.30, 0.70) | 53 | 64 | 28 | 524061 | 2872 | 10.072 | 17.350 | 0.58 |
| A | exploration | Elections | long_yes | [0.30, 0.70) | 9 | 9 | 5 | 46587 | 541 | 7.353 | 32.656 | 0.23 |
| A | confirmation | Elections | long_yes | [0.70, 0.90) | 39 | 56 | 13 | 259176 | 1398 | -2.002 | 12.793 | -0.16 |
| A | exploration | Elections | long_yes | [0.70, 0.90) | 6 | 8 | 1 | 29257 | 210 | -10.989 | 5.209 | -2.11 |
| A | confirmation | Elections | long_yes | [0.90, 1.00] | 33 | 51 | 2 | 1288668 | 2271 | -7.057 | 10.568 | -0.67 |
| A | exploration | Elections | long_yes | [0.90, 1.00] | 6 | 9 | 1 | 69044 | 196 | 0.241 | 0.926 | 0.26 |
| A | confirmation | Elections | short_yes | [0.00, 0.10) | 45 | 78 | 5 | 1037118 | 2776 | -23.523 | 12.676 | -1.86 |
| A | exploration | Elections | short_yes | [0.00, 0.10) | 15 | 22 | 2 | 618389 | 879 | 4.074 | 1.330 | 3.06 |
| A | confirmation | Elections | short_yes | [0.10, 0.30) | 54 | 74 | 21 | 457952 | 1867 | -16.098 | 16.805 | -0.96 |
| A | exploration | Elections | short_yes | [0.10, 0.30) | 14 | 15 | 4 | 572714 | 1342 | 9.134 | 13.483 | 0.68 |
| A | confirmation | Elections | short_yes | [0.30, 0.70) | 59 | 71 | 27 | 814521 | 4953 | 4.775 | 13.207 | 0.36 |
| A | exploration | Elections | short_yes | [0.30, 0.70) | 9 | 11 | 3 | 46500 | 483 | -37.886 | 16.327 | -2.32 |
| A | confirmation | Elections | short_yes | [0.70, 0.90) | 49 | 64 | 33 | 374939 | 2247 | 7.638 | 13.679 | 0.56 |
| A | exploration | Elections | short_yes | [0.70, 0.90) | 5 | 7 | 4 | 24801 | 197 | -8.637 | 4.001 | -2.16 |
| A | confirmation | Elections | short_yes | [0.90, 1.00] | 42 | 65 | 37 | 1048152 | 2654 | 13.011 | 15.355 | 0.85 |
| A | exploration | Elections | short_yes | [0.90, 1.00] | 7 | 10 | 6 | 21455 | 111 | -1.087 | 0.394 | -2.76 |
| A | confirmation | Entertainment | long_yes | [0.00, 0.10) | 129 | 742 | 111 | 2335631 | 17009 | -1.217 | 0.302 | -4.03 |
| A | exploration | Entertainment | long_yes | [0.00, 0.10) | 121 | 587 | 112 | 1171286 | 9097 | -2.445 | 0.291 | -8.40 |
| A | confirmation | Entertainment | long_yes | [0.10, 0.30) | 122 | 550 | 88 | 759926 | 13953 | -6.761 | 1.765 | -3.83 |
| A | exploration | Entertainment | long_yes | [0.10, 0.30) | 100 | 359 | 69 | 515686 | 6607 | -2.430 | 3.722 | -0.65 |
| A | confirmation | Entertainment | long_yes | [0.30, 0.70) | 130 | 508 | 61 | 776466 | 17236 | 0.281 | 3.570 | 0.08 |
| A | exploration | Entertainment | long_yes | [0.30, 0.70) | 103 | 337 | 59 | 526931 | 7504 | 5.352 | 9.125 | 0.59 |
| A | confirmation | Entertainment | long_yes | [0.70, 0.90) | 123 | 437 | 42 | 604084 | 10935 | 3.270 | 3.990 | 0.82 |
| A | exploration | Entertainment | long_yes | [0.70, 0.90) | 115 | 317 | 32 | 297559 | 4455 | 4.127 | 4.010 | 1.03 |
| A | confirmation | Entertainment | long_yes | [0.90, 1.00] | 125 | 515 | 13 | 1979250 | 10435 | 2.006 | 0.387 | 5.18 |
| A | exploration | Entertainment | long_yes | [0.90, 1.00] | 112 | 347 | 11 | 821370 | 4344 | 1.806 | 0.664 | 2.72 |
| A | confirmation | Entertainment | short_yes | [0.00, 0.10) | 133 | 738 | 21 | 8142718 | 32451 | 1.727 | 0.212 | 8.13 |
| A | exploration | Entertainment | short_yes | [0.00, 0.10) | 123 | 664 | 5 | 6197939 | 21786 | 1.944 | 0.360 | 5.40 |
| A | confirmation | Entertainment | short_yes | [0.10, 0.30) | 128 | 607 | 32 | 1483279 | 27154 | 8.593 | 1.872 | 4.59 |
| A | exploration | Entertainment | short_yes | [0.10, 0.30) | 122 | 527 | 25 | 1058828 | 12695 | 9.756 | 1.629 | 5.99 |
| A | confirmation | Entertainment | short_yes | [0.30, 0.70) | 132 | 599 | 73 | 1177031 | 28010 | 1.096 | 3.739 | 0.29 |
| A | exploration | Entertainment | short_yes | [0.30, 0.70) | 116 | 452 | 45 | 894708 | 13942 | -5.717 | 5.494 | -1.04 |
| A | confirmation | Entertainment | short_yes | [0.70, 0.90) | 135 | 543 | 89 | 697130 | 13465 | -4.352 | 3.034 | -1.43 |
| A | exploration | Entertainment | short_yes | [0.70, 0.90) | 113 | 388 | 63 | 429039 | 6089 | -1.226 | 3.603 | -0.34 |
| A | confirmation | Entertainment | short_yes | [0.90, 1.00] | 132 | 781 | 107 | 1274757 | 10373 | -1.339 | 0.609 | -2.20 |
| A | exploration | Entertainment | short_yes | [0.90, 1.00] | 126 | 552 | 87 | 503479 | 4935 | 0.466 | 1.507 | 0.31 |
| A | confirmation | Financials | long_yes | [0.00, 0.10) | 105 | 981 | 85 | 1948007 | 19265 | 1.264 | 2.045 | 0.62 |
| A | exploration | Financials | long_yes | [0.00, 0.10) | 97 | 373 | 73 | 517270 | 3969 | 1.940 | 3.418 | 0.57 |
| A | confirmation | Financials | long_yes | [0.10, 0.30) | 106 | 972 | 73 | 1708446 | 14622 | -2.212 | 2.479 | -0.89 |
| A | exploration | Financials | long_yes | [0.10, 0.30) | 102 | 344 | 73 | 808359 | 5316 | -7.052 | 3.088 | -2.28 |
| A | confirmation | Financials | long_yes | [0.30, 0.70) | 111 | 1033 | 57 | 2681497 | 26083 | 1.189 | 3.821 | 0.31 |
| A | exploration | Financials | long_yes | [0.30, 0.70) | 90 | 289 | 51 | 1305675 | 9443 | -11.765 | 5.268 | -2.23 |
| A | confirmation | Financials | long_yes | [0.70, 0.90) | 100 | 705 | 26 | 1534964 | 13658 | 3.058 | 5.720 | 0.53 |
| A | exploration | Financials | long_yes | [0.70, 0.90) | 81 | 210 | 25 | 542373 | 4045 | 8.083 | 3.725 | 2.17 |
| A | confirmation | Financials | long_yes | [0.90, 1.00] | 99 | 540 | 10 | 917447 | 7844 | -0.140 | 2.635 | -0.05 |
| A | exploration | Financials | long_yes | [0.90, 1.00] | 83 | 198 | 14 | 403985 | 2232 | 0.708 | 1.770 | 0.40 |
| A | confirmation | Financials | short_yes | [0.00, 0.10) | 105 | 709 | 12 | 1744468 | 8179 | 2.157 | 0.673 | 3.20 |
| A | exploration | Financials | short_yes | [0.00, 0.10) | 102 | 377 | 11 | 876281 | 5052 | -0.159 | 2.685 | -0.06 |
| A | confirmation | Financials | short_yes | [0.10, 0.30) | 108 | 891 | 37 | 1968684 | 15283 | -0.616 | 3.220 | -0.19 |
| A | exploration | Financials | short_yes | [0.10, 0.30) | 108 | 429 | 29 | 792213 | 6934 | 5.449 | 3.507 | 1.55 |
| A | confirmation | Financials | short_yes | [0.30, 0.70) | 108 | 1175 | 59 | 2710820 | 31234 | -1.035 | 3.799 | -0.27 |
| A | exploration | Financials | short_yes | [0.30, 0.70) | 104 | 383 | 45 | 1330102 | 11587 | 4.761 | 6.300 | 0.76 |
| A | confirmation | Financials | short_yes | [0.70, 0.90) | 109 | 907 | 75 | 1743198 | 15187 | 3.017 | 6.360 | 0.47 |
| A | exploration | Financials | short_yes | [0.70, 0.90) | 92 | 243 | 60 | 579564 | 4284 | -5.379 | 4.350 | -1.24 |
| A | confirmation | Financials | short_yes | [0.90, 1.00] | 102 | 849 | 84 | 1666194 | 15399 | -1.035 | 0.832 | -1.24 |
| A | exploration | Financials | short_yes | [0.90, 1.00] | 89 | 242 | 59 | 453500 | 3260 | -0.332 | 1.309 | -0.25 |
| A | exploration | Health | long_yes | [0.00, 0.10) | 5 | 9 | 5 | 7540 | 83 | -3.241 | 0.119 | -27.28 |
| A | exploration | Health | long_yes | [0.10, 0.30) | 2 | 2 | 2 | 173 | 8 | -27.543 | 0.082 | -336.19 |
| A | exploration | Health | long_yes | [0.30, 0.70) | 3 | 3 | 3 | 396 | 9 | -33.217 | 0.878 | -37.83 |
| A | exploration | Health | long_yes | [0.70, 0.90) | 1 | 1 | 1 | 39 | 2 | -89.000 | n/a | n/a |
| A | exploration | Health | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 94 | 2 | 0.032 | n/a | n/a |
| A | exploration | Health | short_yes | [0.00, 0.10) | 6 | 10 | 0 | 11561 | 134 | 4.685 | 0.052 | 89.70 |
| A | exploration | Health | short_yes | [0.10, 0.30) | 4 | 4 | 0 | 1462 | 35 | 17.540 | 1.745 | 10.05 |
| A | exploration | Health | short_yes | [0.30, 0.70) | 2 | 2 | 0 | 180 | 9 | 31.594 | 2.064 | 15.31 |
| A | exploration | Health | short_yes | [0.90, 1.00] | 1 | 1 | 1 | 9 | 2 | -1.000 | n/a | n/a |
| A | confirmation | Mentions | long_yes | [0.00, 0.10) | 147 | 700 | 115 | 2132981 | 24842 | 0.317 | 0.887 | 0.36 |
| A | exploration | Mentions | long_yes | [0.00, 0.10) | 131 | 515 | 103 | 2293703 | 24432 | -0.627 | 0.662 | -0.95 |
| A | confirmation | Mentions | long_yes | [0.10, 0.30) | 175 | 846 | 124 | 1151752 | 34438 | -3.638 | 2.419 | -1.50 |
| A | exploration | Mentions | long_yes | [0.10, 0.30) | 141 | 751 | 101 | 1283481 | 30430 | -3.343 | 4.435 | -0.75 |
| A | confirmation | Mentions | long_yes | [0.30, 0.70) | 183 | 953 | 103 | 2139200 | 65521 | -6.782 | 2.328 | -2.91 |
| A | exploration | Mentions | long_yes | [0.30, 0.70) | 146 | 908 | 92 | 2067900 | 55429 | -9.027 | 2.104 | -4.29 |
| A | confirmation | Mentions | long_yes | [0.70, 0.90) | 180 | 835 | 71 | 1121008 | 25625 | -1.216 | 2.184 | -0.56 |
| A | exploration | Mentions | long_yes | [0.70, 0.90) | 145 | 768 | 43 | 1141375 | 23535 | 1.439 | 3.572 | 0.40 |
| A | confirmation | Mentions | long_yes | [0.90, 1.00] | 169 | 710 | 13 | 7341134 | 33270 | 1.375 | 0.134 | 10.25 |
| A | exploration | Mentions | long_yes | [0.90, 1.00] | 144 | 740 | 21 | 5500486 | 34010 | -0.318 | 0.880 | -0.36 |
| A | confirmation | Mentions | short_yes | [0.00, 0.10) | 155 | 866 | 16 | 13062976 | 58437 | 0.693 | 0.473 | 1.47 |
| A | exploration | Mentions | short_yes | [0.00, 0.10) | 136 | 624 | 9 | 19587601 | 63450 | 0.178 | 1.033 | 0.17 |
| A | confirmation | Mentions | short_yes | [0.10, 0.30) | 180 | 969 | 50 | 3670753 | 86739 | 5.692 | 1.612 | 3.53 |
| A | exploration | Mentions | short_yes | [0.10, 0.30) | 144 | 874 | 47 | 3363571 | 80753 | 4.987 | 3.026 | 1.65 |
| A | confirmation | Mentions | short_yes | [0.30, 0.70) | 183 | 1071 | 75 | 5079396 | 164005 | 6.072 | 2.131 | 2.85 |
| A | exploration | Mentions | short_yes | [0.30, 0.70) | 146 | 1016 | 52 | 4607940 | 145145 | 12.859 | 2.156 | 5.96 |
| A | confirmation | Mentions | short_yes | [0.70, 0.90) | 180 | 979 | 82 | 1388729 | 40417 | 3.579 | 1.623 | 2.21 |
| A | exploration | Mentions | short_yes | [0.70, 0.90) | 146 | 939 | 75 | 1682312 | 37822 | 0.939 | 2.032 | 0.46 |
| A | confirmation | Mentions | short_yes | [0.90, 1.00] | 170 | 755 | 134 | 2056288 | 17298 | -0.864 | 0.413 | -2.09 |
| A | exploration | Mentions | short_yes | [0.90, 1.00] | 143 | 790 | 99 | 2387775 | 20942 | 4.795 | 2.910 | 1.65 |
| A | confirmation | Politics | long_yes | [0.00, 0.10) | 138 | 342 | 125 | 2063386 | 9631 | -3.167 | 0.673 | -4.70 |
| A | exploration | Politics | long_yes | [0.00, 0.10) | 79 | 293 | 66 | 1546969 | 5339 | -2.565 | 0.545 | -4.70 |
| A | confirmation | Politics | long_yes | [0.10, 0.30) | 141 | 348 | 91 | 1208965 | 8489 | -11.989 | 2.130 | -5.63 |
| A | exploration | Politics | long_yes | [0.10, 0.30) | 78 | 154 | 55 | 974530 | 5228 | 0.373 | 11.832 | 0.03 |
| A | confirmation | Politics | long_yes | [0.30, 0.70) | 155 | 337 | 74 | 675962 | 9406 | -6.953 | 8.489 | -0.82 |
| A | exploration | Politics | long_yes | [0.30, 0.70) | 82 | 131 | 40 | 1112206 | 8984 | 8.232 | 11.328 | 0.73 |
| A | confirmation | Politics | long_yes | [0.70, 0.90) | 116 | 179 | 36 | 326141 | 3496 | 2.024 | 7.405 | 0.27 |
| A | exploration | Politics | long_yes | [0.70, 0.90) | 62 | 77 | 12 | 773152 | 6620 | 10.122 | 4.691 | 2.16 |
| A | confirmation | Politics | long_yes | [0.90, 1.00] | 106 | 167 | 17 | 1174512 | 4142 | 1.370 | 2.044 | 0.67 |
| A | exploration | Politics | long_yes | [0.90, 1.00] | 57 | 78 | 5 | 4004175 | 6958 | 1.914 | 0.470 | 4.08 |
| A | confirmation | Politics | short_yes | [0.00, 0.10) | 134 | 328 | 15 | 4323195 | 12330 | 3.091 | 0.284 | 10.88 |
| A | exploration | Politics | short_yes | [0.00, 0.10) | 74 | 257 | 9 | 2944005 | 8860 | 2.967 | 0.726 | 4.09 |
| A | confirmation | Politics | short_yes | [0.10, 0.30) | 143 | 360 | 49 | 1844252 | 11165 | 11.211 | 2.974 | 3.77 |
| A | exploration | Politics | short_yes | [0.10, 0.30) | 80 | 179 | 22 | 1546828 | 10538 | -6.652 | 14.403 | -0.46 |
| A | confirmation | Politics | short_yes | [0.30, 0.70) | 161 | 344 | 84 | 878700 | 11454 | 4.273 | 8.981 | 0.48 |
| A | exploration | Politics | short_yes | [0.30, 0.70) | 81 | 144 | 41 | 1269287 | 12200 | 0.994 | 12.247 | 0.08 |
| A | confirmation | Politics | short_yes | [0.70, 0.90) | 134 | 228 | 95 | 248090 | 3271 | -1.078 | 5.858 | -0.18 |
| A | exploration | Politics | short_yes | [0.70, 0.90) | 64 | 99 | 47 | 593266 | 5056 | -7.650 | 5.158 | -1.48 |
| A | confirmation | Politics | short_yes | [0.90, 1.00] | 125 | 185 | 102 | 934095 | 3007 | -1.433 | 1.085 | -1.32 |
| A | exploration | Politics | short_yes | [0.90, 1.00] | 58 | 82 | 50 | 1646448 | 2820 | -1.561 | 1.169 | -1.34 |
| A | confirmation | Science and Technology | long_yes | [0.00, 0.10) | 66 | 160 | 61 | 558461 | 2510 | -2.225 | 0.361 | -6.15 |
| A | exploration | Science and Technology | long_yes | [0.00, 0.10) | 31 | 80 | 26 | 586774 | 2209 | -1.003 | 0.896 | -1.12 |
| A | confirmation | Science and Technology | long_yes | [0.10, 0.30) | 61 | 122 | 47 | 132278 | 1562 | -6.670 | 3.732 | -1.79 |
| A | exploration | Science and Technology | long_yes | [0.10, 0.30) | 24 | 40 | 21 | 140613 | 1074 | -4.654 | 11.458 | -0.41 |
| A | confirmation | Science and Technology | long_yes | [0.30, 0.70) | 66 | 119 | 41 | 207445 | 2734 | -15.953 | 5.768 | -2.77 |
| A | exploration | Science and Technology | long_yes | [0.30, 0.70) | 23 | 31 | 13 | 138941 | 1127 | -6.762 | 12.539 | -0.54 |
| A | confirmation | Science and Technology | long_yes | [0.70, 0.90) | 55 | 113 | 15 | 141707 | 1921 | 0.154 | 3.871 | 0.04 |
| A | exploration | Science and Technology | long_yes | [0.70, 0.90) | 24 | 37 | 6 | 125137 | 905 | 16.030 | 1.754 | 9.14 |
| A | confirmation | Science and Technology | long_yes | [0.90, 1.00] | 55 | 130 | 8 | 274927 | 2065 | 2.064 | 0.628 | 3.28 |
| A | exploration | Science and Technology | long_yes | [0.90, 1.00] | 25 | 51 | 1 | 196355 | 1180 | 2.910 | 0.860 | 3.38 |
| A | confirmation | Science and Technology | short_yes | [0.00, 0.10) | 62 | 146 | 4 | 2183140 | 5088 | 1.501 | 0.471 | 3.19 |
| A | exploration | Science and Technology | short_yes | [0.00, 0.10) | 36 | 97 | 7 | 2708536 | 6931 | 1.680 | 0.712 | 2.36 |
| A | confirmation | Science and Technology | short_yes | [0.10, 0.30) | 63 | 122 | 12 | 209490 | 2120 | 6.931 | 2.937 | 2.36 |
| A | exploration | Science and Technology | short_yes | [0.10, 0.30) | 27 | 52 | 5 | 276252 | 1939 | 13.336 | 2.853 | 4.67 |
| A | confirmation | Science and Technology | short_yes | [0.30, 0.70) | 65 | 128 | 35 | 208098 | 3038 | 8.040 | 8.568 | 0.94 |
| A | exploration | Science and Technology | short_yes | [0.30, 0.70) | 24 | 36 | 9 | 162484 | 1564 | -7.676 | 12.649 | -0.61 |
| A | confirmation | Science and Technology | short_yes | [0.70, 0.90) | 57 | 134 | 41 | 198420 | 2556 | 1.337 | 6.715 | 0.20 |
| A | exploration | Science and Technology | short_yes | [0.70, 0.90) | 25 | 45 | 14 | 169621 | 1445 | -8.383 | 6.667 | -1.26 |
| A | confirmation | Science and Technology | short_yes | [0.90, 1.00] | 59 | 160 | 49 | 298423 | 2627 | -0.325 | 1.879 | -0.17 |
| A | exploration | Science and Technology | short_yes | [0.90, 1.00] | 27 | 57 | 25 | 127552 | 1586 | -1.539 | 2.330 | -0.66 |
| A | confirmation | Social | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 6562 | 13 | -4.477 | n/a | n/a |
| A | exploration | Social | long_yes | [0.00, 0.10) | 4 | 5 | 4 | 3896 | 69 | -4.046 | 1.051 | -3.85 |
| A | confirmation | Social | long_yes | [0.10, 0.30) | 1 | 1 | 0 | 3 | 3 | 17.667 | n/a | n/a |
| A | exploration | Social | long_yes | [0.10, 0.30) | 3 | 3 | 3 | 383 | 22 | -15.258 | 0.728 | -20.97 |
| A | confirmation | Social | long_yes | [0.30, 0.70) | 1 | 1 | 1 | 1146 | 24 | -0.693 | n/a | n/a |
| A | exploration | Social | long_yes | [0.30, 0.70) | 3 | 3 | 2 | 245 | 12 | -33.029 | 0.844 | -39.11 |
| A | exploration | Social | long_yes | [0.70, 0.90) | 2 | 2 | 0 | 921 | 17 | 20.471 | 3.274 | 6.25 |
| A | confirmation | Social | long_yes | [0.90, 1.00] | 2 | 2 | 0 | 254 | 9 | 5.622 | 3.964 | 1.42 |
| A | exploration | Social | long_yes | [0.90, 1.00] | 2 | 2 | 0 | 4030 | 8 | 2.401 | 2.323 | 1.03 |
| A | exploration | Social | short_yes | [0.00, 0.10) | 4 | 5 | 0 | 19431 | 174 | 4.767 | 0.983 | 4.85 |
| A | confirmation | Social | short_yes | [0.10, 0.30) | 1 | 1 | 1 | 200 | 1 | -72.000 | n/a | n/a |
| A | exploration | Social | short_yes | [0.10, 0.30) | 3 | 3 | 0 | 1409 | 41 | 20.219 | 2.660 | 7.60 |
| A | confirmation | Social | short_yes | [0.30, 0.70) | 2 | 2 | 2 | 1271 | 19 | -52.627 | 0.034 | -1546.42 |
| A | exploration | Social | short_yes | [0.30, 0.70) | 4 | 4 | 2 | 243 | 18 | 27.724 | 16.746 | 1.66 |
| A | confirmation | Social | short_yes | [0.70, 0.90) | 1 | 1 | 0 | 73 | 4 | 83.096 | n/a | n/a |
| A | exploration | Social | short_yes | [0.70, 0.90) | 2 | 2 | 2 | 269 | 6 | -14.413 | 0.219 | -65.69 |
| A | confirmation | Social | short_yes | [0.90, 1.00] | 2 | 2 | 2 | 5050 | 19 | -4.320 | 0.244 | -17.68 |
| A | exploration | Social | short_yes | [0.90, 1.00] | 4 | 4 | 3 | 1517 | 9 | -2.041 | 2.288 | -0.89 |
| A | exploration | Transportation | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 36 | 2 | -6.167 | n/a | n/a |
| A | exploration | Transportation | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 2 | 1 | -11.000 | n/a | n/a |
| A | exploration | Transportation | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 19 | 2 | 7.632 | n/a | n/a |
| A | exploration | Transportation | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 349 | 12 | 15.404 | n/a | n/a |
| A | exploration | Transportation | short_yes | [0.30, 0.70) | 1 | 1 | 0 | 1 | 1 | 50.000 | n/a | n/a |
| A | exploration | Transportation | short_yes | [0.70, 0.90) | 1 | 1 | 0 | 25 | 2 | 74.680 | n/a | n/a |
| A | exploration | World | long_yes | [0.00, 0.10) | 1 | 10 | 1 | 2202 | 35 | -1.357 | n/a | n/a |
| A | exploration | World | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 319 | 5 | -16.207 | n/a | n/a |
| A | exploration | World | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 62 | 2 | 1.000 | n/a | n/a |
| A | confirmation | World | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 47 | 2 | 6.000 | n/a | n/a |
| A | exploration | World | short_yes | [0.00, 0.10) | 2 | 8 | 1 | 7423 | 86 | 4.511 | 0.054 | 83.29 |
| A | confirmation | World | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 1 | 1 | 10.000 | n/a | n/a |
| A | exploration | World | short_yes | [0.10, 0.30) | 1 | 2 | 0 | 302 | 2 | 10.980 | n/a | n/a |
| B | confirmation | ALL | long_yes | [0.00, 0.10) | 1145 | 18335 | 938 | 8855185 | 1233921 | 0.052 | 0.597 | 0.09 |
| B | exploration | ALL | long_yes | [0.00, 0.10) | 878 | 8904 | 718 | 2028496 | 274866 | -1.297 | 0.418 | -3.11 |
| B | confirmation | ALL | long_yes | [0.10, 0.30) | 1178 | 19007 | 810 | 10745423 | 1527270 | -1.436 | 1.067 | -1.35 |
| B | exploration | ALL | long_yes | [0.10, 0.30) | 877 | 9396 | 635 | 2591203 | 366677 | -3.124 | 0.986 | -3.17 |
| B | confirmation | ALL | long_yes | [0.30, 0.70) | 1226 | 21955 | 678 | 28938768 | 3818292 | -0.350 | 1.136 | -0.31 |
| B | exploration | ALL | long_yes | [0.30, 0.70) | 861 | 10616 | 500 | 5209500 | 723978 | -1.303 | 1.481 | -0.88 |
| B | confirmation | ALL | long_yes | [0.70, 0.90) | 1123 | 15049 | 442 | 12515983 | 1575547 | 1.002 | 1.160 | 0.86 |
| B | exploration | ALL | long_yes | [0.70, 0.90) | 812 | 6983 | 298 | 2372654 | 311967 | -0.248 | 1.227 | -0.20 |
| B | confirmation | ALL | long_yes | [0.90, 1.00] | 1055 | 12901 | 242 | 9689636 | 1171519 | 0.401 | 0.507 | 0.79 |
| B | exploration | ALL | long_yes | [0.90, 1.00] | 777 | 5856 | 173 | 1701408 | 209985 | -0.119 | 0.643 | -0.18 |
| B | confirmation | ALL | short_yes | [0.00, 0.10) | 1143 | 16889 | 257 | 10994557 | 1328371 | -0.510 | 0.670 | -0.76 |
| B | exploration | ALL | short_yes | [0.00, 0.10) | 898 | 8895 | 184 | 2426308 | 291088 | 0.682 | 0.497 | 1.37 |
| B | confirmation | ALL | short_yes | [0.10, 0.30) | 1196 | 18676 | 443 | 15126969 | 1911355 | -0.280 | 1.138 | -0.25 |
| B | exploration | ALL | short_yes | [0.10, 0.30) | 906 | 10016 | 257 | 3588697 | 458466 | 2.029 | 1.098 | 1.85 |
| B | confirmation | ALL | short_yes | [0.30, 0.70) | 1244 | 22787 | 638 | 33424896 | 4405544 | -1.210 | 1.132 | -1.07 |
| B | exploration | ALL | short_yes | [0.30, 0.70) | 898 | 11352 | 383 | 6839771 | 920898 | 1.366 | 1.442 | 0.95 |
| B | confirmation | ALL | short_yes | [0.70, 0.90) | 1177 | 16887 | 772 | 10836196 | 1521313 | -2.857 | 1.092 | -2.62 |
| B | exploration | ALL | short_yes | [0.70, 0.90) | 847 | 7949 | 502 | 2443952 | 339455 | -0.965 | 1.081 | -0.89 |
| B | confirmation | ALL | short_yes | [0.90, 1.00] | 1118 | 15484 | 899 | 8012113 | 1110510 | -0.967 | 0.407 | -2.38 |
| B | exploration | ALL | short_yes | [0.90, 1.00] | 819 | 7004 | 609 | 1520158 | 208176 | -0.645 | 0.517 | -1.25 |
| B | confirmation | Climate and Weather | long_yes | [0.00, 0.10) | 143 | 5435 | 115 | 572096 | 90397 | -1.555 | 0.237 | -6.57 |
| B | exploration | Climate and Weather | long_yes | [0.00, 0.10) | 141 | 2875 | 105 | 408897 | 61605 | -0.900 | 0.348 | -2.59 |
| B | confirmation | Climate and Weather | long_yes | [0.10, 0.30) | 142 | 4862 | 101 | 481681 | 81799 | -2.440 | 0.642 | -3.80 |
| B | exploration | Climate and Weather | long_yes | [0.10, 0.30) | 141 | 2793 | 90 | 396143 | 65603 | -1.223 | 0.746 | -1.64 |
| B | confirmation | Climate and Weather | long_yes | [0.30, 0.70) | 142 | 4829 | 90 | 541873 | 93301 | -2.918 | 0.637 | -4.58 |
| B | exploration | Climate and Weather | long_yes | [0.30, 0.70) | 140 | 2624 | 65 | 363281 | 60620 | -0.955 | 0.718 | -1.33 |
| B | confirmation | Climate and Weather | long_yes | [0.70, 0.90) | 137 | 2335 | 72 | 139591 | 22352 | -2.029 | 1.401 | -1.45 |
| B | exploration | Climate and Weather | long_yes | [0.70, 0.90) | 132 | 1014 | 51 | 79673 | 12188 | 1.516 | 1.770 | 0.86 |
| B | confirmation | Climate and Weather | long_yes | [0.90, 1.00] | 135 | 2078 | 47 | 98548 | 14656 | -0.651 | 0.654 | -1.00 |
| B | exploration | Climate and Weather | long_yes | [0.90, 1.00] | 127 | 944 | 32 | 62976 | 8359 | -1.932 | 1.372 | -1.41 |
| B | confirmation | Climate and Weather | short_yes | [0.00, 0.10) | 142 | 4695 | 52 | 444735 | 64574 | 0.066 | 0.325 | 0.20 |
| B | exploration | Climate and Weather | short_yes | [0.00, 0.10) | 140 | 2743 | 49 | 341452 | 46916 | 0.011 | 0.400 | 0.03 |
| B | confirmation | Climate and Weather | short_yes | [0.10, 0.30) | 143 | 4690 | 70 | 503107 | 76515 | -0.915 | 0.653 | -1.40 |
| B | exploration | Climate and Weather | short_yes | [0.10, 0.30) | 141 | 2818 | 58 | 426197 | 61876 | 0.322 | 0.640 | 0.50 |
| B | confirmation | Climate and Weather | short_yes | [0.30, 0.70) | 143 | 5105 | 85 | 790580 | 126124 | -1.176 | 0.629 | -1.87 |
| B | exploration | Climate and Weather | short_yes | [0.30, 0.70) | 141 | 2749 | 78 | 474968 | 68146 | 0.287 | 0.776 | 0.37 |
| B | confirmation | Climate and Weather | short_yes | [0.70, 0.90) | 141 | 2854 | 98 | 249684 | 39973 | -3.647 | 1.072 | -3.40 |
| B | exploration | Climate and Weather | short_yes | [0.70, 0.90) | 135 | 1208 | 87 | 102379 | 14803 | -1.676 | 1.742 | -0.96 |
| B | confirmation | Climate and Weather | short_yes | [0.90, 1.00] | 138 | 2917 | 106 | 199798 | 32615 | -1.744 | 0.433 | -4.03 |
| B | exploration | Climate and Weather | short_yes | [0.90, 1.00] | 131 | 1090 | 102 | 74236 | 11153 | 1.008 | 1.590 | 0.63 |
| B | confirmation | Commodities | long_yes | [0.00, 0.10) | 111 | 1286 | 88 | 417202 | 55194 | -0.504 | 0.598 | -0.84 |
| B | exploration | Commodities | long_yes | [0.00, 0.10) | 51 | 104 | 40 | 32863 | 4507 | -2.225 | 0.951 | -2.34 |
| B | confirmation | Commodities | long_yes | [0.10, 0.30) | 113 | 1460 | 81 | 592618 | 81698 | -1.013 | 1.724 | -0.59 |
| B | exploration | Commodities | long_yes | [0.10, 0.30) | 54 | 125 | 46 | 28454 | 4066 | -10.506 | 1.724 | -6.09 |
| B | confirmation | Commodities | long_yes | [0.30, 0.70) | 113 | 1754 | 58 | 1468290 | 194808 | -1.486 | 1.688 | -0.88 |
| B | exploration | Commodities | long_yes | [0.30, 0.70) | 51 | 132 | 31 | 46838 | 6540 | -11.291 | 5.938 | -1.90 |
| B | confirmation | Commodities | long_yes | [0.70, 0.90) | 110 | 1402 | 44 | 599973 | 77627 | -2.509 | 1.671 | -1.50 |
| B | exploration | Commodities | long_yes | [0.70, 0.90) | 43 | 104 | 21 | 22954 | 3228 | -10.882 | 6.856 | -1.59 |
| B | confirmation | Commodities | long_yes | [0.90, 1.00] | 110 | 1148 | 26 | 436186 | 53040 | 0.380 | 0.699 | 0.54 |
| B | exploration | Commodities | long_yes | [0.90, 1.00] | 35 | 74 | 13 | 14411 | 1892 | -4.838 | 3.494 | -1.38 |
| B | confirmation | Commodities | short_yes | [0.00, 0.10) | 111 | 1165 | 30 | 426514 | 50113 | 0.418 | 0.624 | 0.67 |
| B | exploration | Commodities | short_yes | [0.00, 0.10) | 49 | 100 | 8 | 29685 | 3446 | 2.942 | 0.946 | 3.11 |
| B | confirmation | Commodities | short_yes | [0.10, 0.30) | 113 | 1404 | 43 | 643285 | 82016 | -0.808 | 1.806 | -0.45 |
| B | exploration | Commodities | short_yes | [0.10, 0.30) | 52 | 124 | 5 | 41075 | 5357 | 9.906 | 1.865 | 5.31 |
| B | confirmation | Commodities | short_yes | [0.30, 0.70) | 114 | 1796 | 61 | 1820208 | 241988 | -0.490 | 1.482 | -0.33 |
| B | exploration | Commodities | short_yes | [0.30, 0.70) | 55 | 159 | 21 | 92817 | 12549 | 9.938 | 6.364 | 1.56 |
| B | confirmation | Commodities | short_yes | [0.70, 0.90) | 114 | 1498 | 79 | 705567 | 97866 | -0.412 | 1.591 | -0.26 |
| B | exploration | Commodities | short_yes | [0.70, 0.90) | 48 | 127 | 21 | 34459 | 4819 | 8.633 | 6.108 | 1.41 |
| B | confirmation | Commodities | short_yes | [0.90, 1.00] | 110 | 1303 | 90 | 435669 | 59286 | -1.162 | 0.481 | -2.42 |
| B | exploration | Commodities | short_yes | [0.90, 1.00] | 38 | 103 | 21 | 15924 | 2174 | 2.059 | 2.732 | 0.75 |
| B | confirmation | Companies | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 70 | 8 | -4.858 | n/a | n/a |
| B | exploration | Companies | long_yes | [0.00, 0.10) | 3 | 13 | 3 | 525 | 65 | -4.175 | 1.331 | -3.14 |
| B | confirmation | Companies | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 10 | 1 | -12.000 | n/a | n/a |
| B | exploration | Companies | long_yes | [0.10, 0.30) | 3 | 3 | 2 | 4767 | 557 | -12.975 | 6.785 | -1.91 |
| B | exploration | Companies | long_yes | [0.30, 0.70) | 2 | 2 | 1 | 4566 | 561 | -16.968 | 7.465 | -2.27 |
| B | exploration | Companies | long_yes | [0.70, 0.90) | 2 | 2 | 1 | 1732 | 203 | 2.643 | 8.234 | 0.32 |
| B | exploration | Companies | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 3354 | 371 | 3.606 | n/a | n/a |
| B | confirmation | Companies | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 121 | 13 | 4.240 | n/a | n/a |
| B | exploration | Companies | short_yes | [0.00, 0.10) | 3 | 11 | 0 | 1964 | 205 | 4.473 | 0.112 | 39.89 |
| B | confirmation | Companies | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 10 | 1 | 15.000 | n/a | n/a |
| B | exploration | Companies | short_yes | [0.10, 0.30) | 3 | 4 | 1 | 20424 | 2233 | 14.891 | 1.561 | 9.54 |
| B | exploration | Companies | short_yes | [0.30, 0.70) | 2 | 2 | 1 | 14395 | 1897 | 23.849 | 1.552 | 15.36 |
| B | exploration | Companies | short_yes | [0.70, 0.90) | 2 | 2 | 1 | 2101 | 304 | 2.818 | 2.398 | 1.18 |
| B | exploration | Companies | short_yes | [0.90, 1.00] | 2 | 2 | 1 | 1816 | 321 | -5.623 | 1.108 | -5.07 |
| B | confirmation | Crypto | long_yes | [0.00, 0.10) | 129 | 8204 | 90 | 7431677 | 1029814 | 0.309 | 0.709 | 0.44 |
| B | exploration | Crypto | long_yes | [0.00, 0.10) | 131 | 3933 | 102 | 1314941 | 172448 | -1.190 | 0.630 | -1.89 |
| B | confirmation | Crypto | long_yes | [0.10, 0.30) | 132 | 9244 | 73 | 9248086 | 1305311 | -1.242 | 1.236 | -1.00 |
| B | exploration | Crypto | long_yes | [0.10, 0.30) | 131 | 4653 | 93 | 1884472 | 260360 | -3.120 | 1.314 | -2.38 |
| B | confirmation | Crypto | long_yes | [0.30, 0.70) | 136 | 11814 | 68 | 26228903 | 3433638 | -0.107 | 1.253 | -0.09 |
| B | exploration | Crypto | long_yes | [0.30, 0.70) | 133 | 5999 | 75 | 4320027 | 596448 | -0.496 | 1.763 | -0.28 |
| B | confirmation | Crypto | long_yes | [0.70, 0.90) | 132 | 8601 | 53 | 11423964 | 1427663 | 1.287 | 1.268 | 1.01 |
| B | exploration | Crypto | long_yes | [0.70, 0.90) | 131 | 4319 | 55 | 2014342 | 264979 | -0.645 | 1.420 | -0.45 |
| B | confirmation | Crypto | long_yes | [0.90, 1.00] | 131 | 7440 | 32 | 8882359 | 1070981 | 0.415 | 0.553 | 0.75 |
| B | exploration | Crypto | long_yes | [0.90, 1.00] | 130 | 3453 | 37 | 1385694 | 172895 | -0.010 | 0.774 | -0.01 |
| B | confirmation | Crypto | short_yes | [0.00, 0.10) | 129 | 7941 | 40 | 9369959 | 1129642 | -0.715 | 0.784 | -0.91 |
| B | exploration | Crypto | short_yes | [0.00, 0.10) | 132 | 3964 | 33 | 1459901 | 176570 | 0.091 | 0.793 | 0.11 |
| B | confirmation | Crypto | short_yes | [0.10, 0.30) | 133 | 9119 | 63 | 13021478 | 1634629 | -0.637 | 1.314 | -0.48 |
| B | exploration | Crypto | short_yes | [0.10, 0.30) | 132 | 4860 | 43 | 2322581 | 295880 | 0.662 | 1.556 | 0.43 |
| B | confirmation | Crypto | short_yes | [0.30, 0.70) | 136 | 11904 | 74 | 29382842 | 3841701 | -1.578 | 1.287 | -1.23 |
| B | exploration | Crypto | short_yes | [0.30, 0.70) | 134 | 6259 | 70 | 5110788 | 691120 | -1.126 | 1.809 | -0.62 |
| B | confirmation | Crypto | short_yes | [0.70, 0.90) | 134 | 9188 | 89 | 9458384 | 1320401 | -3.149 | 1.246 | -2.53 |
| B | exploration | Crypto | short_yes | [0.70, 0.90) | 132 | 4729 | 84 | 2000217 | 277899 | -1.438 | 1.301 | -1.11 |
| B | confirmation | Crypto | short_yes | [0.90, 1.00] | 131 | 8150 | 104 | 7102954 | 979233 | -0.949 | 0.456 | -2.08 |
| B | exploration | Crypto | short_yes | [0.90, 1.00] | 131 | 4058 | 104 | 1265546 | 169681 | -0.879 | 0.603 | -1.46 |
| B | confirmation | Economics | long_yes | [0.00, 0.10) | 137 | 525 | 112 | 33014 | 4421 | -2.025 | 0.532 | -3.80 |
| B | exploration | Economics | long_yes | [0.00, 0.10) | 80 | 189 | 74 | 16247 | 2133 | -3.847 | 0.378 | -10.19 |
| B | confirmation | Economics | long_yes | [0.10, 0.30) | 139 | 550 | 100 | 38245 | 5427 | -3.717 | 2.619 | -1.42 |
| B | exploration | Economics | long_yes | [0.10, 0.30) | 83 | 167 | 68 | 13059 | 1770 | -7.249 | 2.973 | -2.44 |
| B | confirmation | Economics | long_yes | [0.30, 0.70) | 139 | 556 | 80 | 60722 | 8561 | -4.543 | 3.509 | -1.29 |
| B | exploration | Economics | long_yes | [0.30, 0.70) | 76 | 156 | 48 | 21164 | 2822 | -17.334 | 4.270 | -4.06 |
| B | confirmation | Economics | long_yes | [0.70, 0.90) | 133 | 416 | 45 | 35204 | 4790 | -0.583 | 3.192 | -0.18 |
| B | exploration | Economics | long_yes | [0.70, 0.90) | 76 | 144 | 25 | 12186 | 1614 | -0.513 | 3.401 | -0.15 |
| B | confirmation | Economics | long_yes | [0.90, 1.00] | 133 | 369 | 30 | 32511 | 4074 | -2.903 | 1.715 | -1.69 |
| B | exploration | Economics | long_yes | [0.90, 1.00] | 70 | 126 | 12 | 20465 | 2590 | 2.132 | 1.008 | 2.12 |
| B | confirmation | Economics | short_yes | [0.00, 0.10) | 138 | 463 | 21 | 66514 | 8051 | 0.809 | 0.934 | 0.87 |
| B | exploration | Economics | short_yes | [0.00, 0.10) | 83 | 198 | 8 | 65520 | 7158 | 2.893 | 0.429 | 6.74 |
| B | confirmation | Economics | short_yes | [0.10, 0.30) | 137 | 531 | 37 | 66517 | 8992 | 2.373 | 2.846 | 0.83 |
| B | exploration | Economics | short_yes | [0.10, 0.30) | 79 | 182 | 18 | 38651 | 4926 | 7.710 | 2.767 | 2.79 |
| B | confirmation | Economics | short_yes | [0.30, 0.70) | 139 | 630 | 61 | 102572 | 14342 | 4.229 | 3.787 | 1.12 |
| B | exploration | Economics | short_yes | [0.30, 0.70) | 82 | 187 | 26 | 46372 | 6030 | 16.748 | 5.817 | 2.88 |
| B | confirmation | Economics | short_yes | [0.70, 0.90) | 137 | 556 | 93 | 52584 | 7981 | -0.235 | 2.925 | -0.08 |
| B | exploration | Economics | short_yes | [0.70, 0.90) | 82 | 171 | 49 | 18084 | 2465 | 4.261 | 4.464 | 0.95 |
| B | confirmation | Economics | short_yes | [0.90, 1.00] | 140 | 538 | 112 | 35865 | 5013 | -1.396 | 0.879 | -1.59 |
| B | exploration | Economics | short_yes | [0.90, 1.00] | 83 | 169 | 63 | 16605 | 2597 | -0.392 | 1.864 | -0.21 |
| B | confirmation | Elections | long_yes | [0.00, 0.10) | 49 | 73 | 40 | 12012 | 1498 | 17.535 | 12.293 | 1.43 |
| B | exploration | Elections | long_yes | [0.00, 0.10) | 14 | 23 | 12 | 3851 | 472 | -3.328 | 1.213 | -2.74 |
| B | confirmation | Elections | long_yes | [0.10, 0.30) | 54 | 72 | 39 | 9434 | 1219 | 0.926 | 7.513 | 0.12 |
| B | exploration | Elections | long_yes | [0.10, 0.30) | 11 | 11 | 8 | 3743 | 439 | 4.317 | 15.766 | 0.27 |
| B | confirmation | Elections | long_yes | [0.30, 0.70) | 52 | 63 | 28 | 19887 | 2361 | 10.541 | 14.392 | 0.73 |
| B | exploration | Elections | long_yes | [0.30, 0.70) | 9 | 9 | 5 | 2394 | 415 | 16.167 | 25.512 | 0.63 |
| B | confirmation | Elections | long_yes | [0.70, 0.90) | 39 | 56 | 14 | 9574 | 1112 | 3.681 | 8.030 | 0.46 |
| B | exploration | Elections | long_yes | [0.70, 0.90) | 6 | 7 | 1 | 1204 | 149 | -6.400 | 21.390 | -0.30 |
| B | confirmation | Elections | long_yes | [0.90, 1.00] | 30 | 49 | 2 | 15219 | 1764 | -10.958 | 14.184 | -0.77 |
| B | exploration | Elections | long_yes | [0.90, 1.00] | 6 | 8 | 1 | 687 | 77 | -7.585 | 5.664 | -1.34 |
| B | confirmation | Elections | short_yes | [0.00, 0.10) | 45 | 78 | 7 | 17397 | 2041 | -25.596 | 15.494 | -1.65 |
| B | exploration | Elections | short_yes | [0.00, 0.10) | 15 | 22 | 2 | 6646 | 702 | 3.200 | 1.541 | 2.08 |
| B | confirmation | Elections | short_yes | [0.10, 0.30) | 53 | 71 | 21 | 12840 | 1459 | -13.615 | 11.412 | -1.19 |
| B | exploration | Elections | short_yes | [0.10, 0.30) | 14 | 13 | 4 | 10774 | 1174 | 9.914 | 8.998 | 1.10 |
| B | confirmation | Elections | short_yes | [0.30, 0.70) | 59 | 69 | 30 | 36347 | 4290 | 7.846 | 9.867 | 0.80 |
| B | exploration | Elections | short_yes | [0.30, 0.70) | 9 | 10 | 3 | 2659 | 342 | -30.783 | 17.122 | -1.80 |
| B | confirmation | Elections | short_yes | [0.70, 0.90) | 45 | 63 | 31 | 14963 | 1916 | 3.706 | 10.682 | 0.35 |
| B | exploration | Elections | short_yes | [0.70, 0.90) | 7 | 9 | 5 | 1011 | 135 | -1.261 | 6.455 | -0.20 |
| B | confirmation | Elections | short_yes | [0.90, 1.00] | 40 | 62 | 37 | 14536 | 1849 | 25.851 | 22.127 | 1.17 |
| B | exploration | Elections | short_yes | [0.90, 1.00] | 6 | 8 | 5 | 656 | 89 | -1.925 | 1.856 | -1.04 |
| B | confirmation | Entertainment | long_yes | [0.00, 0.10) | 129 | 724 | 107 | 103949 | 13455 | -1.967 | 0.509 | -3.86 |
| B | exploration | Entertainment | long_yes | [0.00, 0.10) | 120 | 566 | 112 | 56230 | 7237 | -3.259 | 0.427 | -7.63 |
| B | confirmation | Entertainment | long_yes | [0.10, 0.30) | 123 | 557 | 90 | 76344 | 10125 | -7.520 | 1.553 | -4.84 |
| B | exploration | Entertainment | long_yes | [0.10, 0.30) | 102 | 365 | 76 | 35497 | 4472 | -6.879 | 2.136 | -3.22 |
| B | confirmation | Entertainment | long_yes | [0.30, 0.70) | 130 | 497 | 65 | 86613 | 11430 | -1.843 | 2.956 | -0.62 |
| B | exploration | Entertainment | long_yes | [0.30, 0.70) | 103 | 326 | 68 | 39328 | 4860 | -6.817 | 5.208 | -1.31 |
| B | confirmation | Entertainment | long_yes | [0.70, 0.90) | 122 | 419 | 40 | 61594 | 7708 | 4.983 | 2.861 | 1.74 |
| B | exploration | Entertainment | long_yes | [0.70, 0.90) | 109 | 299 | 40 | 24765 | 3124 | 2.859 | 3.394 | 0.84 |
| B | confirmation | Entertainment | long_yes | [0.90, 1.00] | 118 | 455 | 25 | 55876 | 6702 | 1.786 | 0.831 | 2.15 |
| B | exploration | Entertainment | long_yes | [0.90, 1.00] | 110 | 329 | 15 | 27319 | 3094 | 1.845 | 0.975 | 1.89 |
| B | confirmation | Entertainment | short_yes | [0.00, 0.10) | 130 | 680 | 33 | 195763 | 21365 | 1.730 | 0.562 | 3.08 |
| B | exploration | Entertainment | short_yes | [0.00, 0.10) | 122 | 624 | 12 | 127691 | 13561 | 3.102 | 0.464 | 6.68 |
| B | confirmation | Entertainment | short_yes | [0.10, 0.30) | 127 | 573 | 45 | 170557 | 19870 | 9.975 | 1.835 | 5.44 |
| B | exploration | Entertainment | short_yes | [0.10, 0.30) | 122 | 492 | 23 | 73805 | 8592 | 7.888 | 2.266 | 3.48 |
| B | confirmation | Entertainment | short_yes | [0.30, 0.70) | 132 | 580 | 73 | 149827 | 19691 | 1.933 | 3.361 | 0.58 |
| B | exploration | Entertainment | short_yes | [0.30, 0.70) | 113 | 425 | 41 | 78164 | 9821 | 5.456 | 4.815 | 1.13 |
| B | confirmation | Entertainment | short_yes | [0.70, 0.90) | 133 | 538 | 88 | 71458 | 10355 | -4.811 | 4.168 | -1.15 |
| B | exploration | Entertainment | short_yes | [0.70, 0.90) | 114 | 388 | 69 | 34001 | 4529 | 2.195 | 3.979 | 0.55 |
| B | confirmation | Entertainment | short_yes | [0.90, 1.00] | 129 | 740 | 103 | 56349 | 7900 | -1.759 | 0.910 | -1.93 |
| B | exploration | Entertainment | short_yes | [0.90, 1.00] | 121 | 515 | 84 | 25278 | 3697 | -0.417 | 1.249 | -0.33 |
| B | confirmation | Financials | long_yes | [0.00, 0.10) | 104 | 939 | 86 | 92142 | 14989 | -1.967 | 0.659 | -2.99 |
| B | exploration | Financials | long_yes | [0.00, 0.10) | 94 | 357 | 66 | 23274 | 3387 | 1.220 | 1.733 | 0.70 |
| B | confirmation | Financials | long_yes | [0.10, 0.30) | 106 | 970 | 67 | 90481 | 13126 | -1.665 | 1.606 | -1.04 |
| B | exploration | Financials | long_yes | [0.10, 0.30) | 101 | 347 | 68 | 35307 | 4916 | -1.371 | 3.940 | -0.35 |
| B | confirmation | Financials | long_yes | [0.30, 0.70) | 111 | 1034 | 61 | 153570 | 23146 | -0.297 | 2.556 | -0.12 |
| B | exploration | Financials | long_yes | [0.30, 0.70) | 90 | 293 | 45 | 69833 | 8778 | -4.246 | 4.418 | -0.96 |
| B | confirmation | Financials | long_yes | [0.70, 0.90) | 101 | 701 | 34 | 73329 | 12225 | -0.030 | 2.778 | -0.01 |
| B | exploration | Financials | long_yes | [0.70, 0.90) | 82 | 209 | 24 | 29060 | 3745 | 0.229 | 4.029 | 0.06 |
| B | confirmation | Financials | long_yes | [0.90, 1.00] | 95 | 527 | 18 | 38329 | 5582 | -1.697 | 2.484 | -0.68 |
| B | exploration | Financials | long_yes | [0.90, 1.00] | 75 | 184 | 18 | 16637 | 2040 | -2.305 | 2.890 | -0.80 |
| B | confirmation | Financials | short_yes | [0.00, 0.10) | 103 | 708 | 27 | 52815 | 6935 | 0.957 | 0.565 | 1.69 |
| B | exploration | Financials | short_yes | [0.00, 0.10) | 101 | 371 | 24 | 40097 | 4627 | 0.218 | 1.082 | 0.20 |
| B | confirmation | Financials | short_yes | [0.10, 0.30) | 108 | 869 | 48 | 96100 | 13366 | -5.242 | 3.079 | -1.70 |
| B | exploration | Financials | short_yes | [0.10, 0.30) | 105 | 418 | 33 | 46590 | 6006 | 3.670 | 2.569 | 1.43 |
| B | confirmation | Financials | short_yes | [0.30, 0.70) | 110 | 1166 | 63 | 203029 | 27873 | -2.426 | 2.313 | -1.05 |
| B | exploration | Financials | short_yes | [0.30, 0.70) | 104 | 368 | 47 | 81855 | 10433 | 3.466 | 4.648 | 0.75 |
| B | confirmation | Financials | short_yes | [0.70, 0.90) | 105 | 874 | 72 | 88962 | 13187 | -2.765 | 2.364 | -1.17 |
| B | exploration | Financials | short_yes | [0.70, 0.90) | 91 | 235 | 58 | 28199 | 3872 | -1.065 | 3.481 | -0.31 |
| B | confirmation | Financials | short_yes | [0.90, 1.00] | 99 | 790 | 79 | 74812 | 11976 | -2.151 | 0.586 | -3.67 |
| B | exploration | Financials | short_yes | [0.90, 1.00] | 82 | 211 | 58 | 15712 | 2741 | 2.877 | 2.984 | 0.96 |
| B | exploration | Health | long_yes | [0.00, 0.10) | 4 | 8 | 4 | 559 | 73 | -4.374 | 0.322 | -13.59 |
| B | exploration | Health | long_yes | [0.10, 0.30) | 3 | 3 | 3 | 44 | 7 | -11.295 | 1.281 | -8.81 |
| B | exploration | Health | long_yes | [0.30, 0.70) | 3 | 3 | 3 | 63 | 9 | -32.984 | 0.753 | -43.81 |
| B | exploration | Health | long_yes | [0.90, 1.00] | 1 | 1 | 1 | 21 | 3 | -90.048 | n/a | n/a |
| B | exploration | Health | short_yes | [0.00, 0.10) | 6 | 10 | 0 | 1200 | 126 | 4.050 | 0.189 | 21.38 |
| B | exploration | Health | short_yes | [0.10, 0.30) | 3 | 3 | 0 | 167 | 18 | 17.832 | 2.762 | 6.46 |
| B | exploration | Health | short_yes | [0.30, 0.70) | 2 | 2 | 0 | 33 | 5 | 37.061 | 0.228 | 162.74 |
| B | exploration | Health | short_yes | [0.90, 1.00] | 1 | 1 | 1 | 9 | 2 | -2.000 | n/a | n/a |
| B | confirmation | Mentions | long_yes | [0.00, 0.10) | 146 | 654 | 122 | 120038 | 14685 | -1.952 | 0.561 | -3.48 |
| B | exploration | Mentions | long_yes | [0.00, 0.10) | 128 | 457 | 105 | 122762 | 16746 | -2.070 | 0.562 | -3.69 |
| B | confirmation | Mentions | long_yes | [0.10, 0.30) | 171 | 821 | 121 | 150303 | 20774 | -5.722 | 1.426 | -4.01 |
| B | exploration | Mentions | long_yes | [0.10, 0.30) | 141 | 731 | 102 | 150293 | 19417 | -7.493 | 1.495 | -5.01 |
| B | confirmation | Mentions | long_yes | [0.30, 0.70) | 183 | 953 | 111 | 312391 | 42324 | -8.432 | 1.695 | -4.98 |
| B | exploration | Mentions | long_yes | [0.30, 0.70) | 146 | 907 | 99 | 281899 | 35619 | -11.004 | 1.809 | -6.08 |
| B | confirmation | Mentions | long_yes | [0.70, 0.90) | 180 | 828 | 88 | 142948 | 18292 | -4.826 | 2.202 | -2.19 |
| B | exploration | Mentions | long_yes | [0.70, 0.90) | 145 | 771 | 58 | 134957 | 16684 | 0.458 | 2.303 | 0.20 |
| B | confirmation | Mentions | long_yes | [0.90, 1.00] | 157 | 576 | 33 | 87360 | 9829 | 2.145 | 0.738 | 2.91 |
| B | exploration | Mentions | long_yes | [0.90, 1.00] | 143 | 620 | 37 | 124550 | 13579 | -1.545 | 1.485 | -1.04 |
| B | confirmation | Mentions | short_yes | [0.00, 0.10) | 150 | 686 | 24 | 309122 | 33333 | 1.643 | 0.885 | 1.86 |
| B | exploration | Mentions | short_yes | [0.00, 0.10) | 133 | 489 | 26 | 241266 | 25833 | 2.283 | 0.547 | 4.17 |
| B | confirmation | Mentions | short_yes | [0.10, 0.30) | 180 | 956 | 49 | 534098 | 64967 | 6.266 | 1.430 | 4.38 |
| B | exploration | Mentions | short_yes | [0.10, 0.30) | 144 | 879 | 43 | 522962 | 62594 | 7.144 | 1.482 | 4.82 |
| B | confirmation | Mentions | short_yes | [0.30, 0.70) | 183 | 1070 | 71 | 860665 | 119240 | 7.860 | 1.538 | 5.11 |
| B | exploration | Mentions | short_yes | [0.30, 0.70) | 146 | 1015 | 43 | 851887 | 110129 | 14.209 | 1.946 | 7.30 |
| B | confirmation | Mentions | short_yes | [0.70, 0.90) | 178 | 967 | 84 | 163658 | 25340 | 3.757 | 1.622 | 2.32 |
| B | exploration | Mentions | short_yes | [0.70, 0.90) | 145 | 939 | 64 | 184065 | 25635 | 3.626 | 2.046 | 1.77 |
| B | confirmation | Mentions | short_yes | [0.90, 1.00] | 161 | 668 | 125 | 60756 | 8379 | -2.475 | 0.504 | -4.91 |
| B | exploration | Mentions | short_yes | [0.90, 1.00] | 140 | 712 | 94 | 79921 | 12285 | 1.074 | 1.597 | 0.67 |
| B | confirmation | Politics | long_yes | [0.00, 0.10) | 130 | 334 | 117 | 55601 | 7286 | -3.759 | 0.322 | -11.68 |
| B | exploration | Politics | long_yes | [0.00, 0.10) | 76 | 285 | 64 | 32556 | 4225 | -3.056 | 0.816 | -3.74 |
| B | confirmation | Politics | long_yes | [0.10, 0.30) | 136 | 344 | 90 | 49533 | 6569 | -8.076 | 2.605 | -3.10 |
| B | exploration | Politics | long_yes | [0.10, 0.30) | 79 | 152 | 55 | 32374 | 4165 | 5.969 | 13.899 | 0.43 |
| B | confirmation | Politics | long_yes | [0.30, 0.70) | 153 | 338 | 75 | 52827 | 6966 | -9.666 | 6.913 | -1.40 |
| B | exploration | Politics | long_yes | [0.30, 0.70) | 82 | 132 | 43 | 53841 | 6562 | 6.840 | 10.037 | 0.68 |
| B | confirmation | Politics | long_yes | [0.70, 0.90) | 116 | 183 | 35 | 19924 | 2452 | 0.763 | 5.558 | 0.14 |
| B | exploration | Politics | long_yes | [0.70, 0.90) | 60 | 76 | 15 | 46684 | 5382 | 14.486 | 3.201 | 4.52 |
| B | confirmation | Politics | long_yes | [0.90, 1.00] | 89 | 131 | 18 | 30628 | 3300 | 3.813 | 1.342 | 2.84 |
| B | exploration | Politics | long_yes | [0.90, 1.00] | 53 | 68 | 4 | 37314 | 4059 | 3.265 | 1.086 | 3.01 |
| B | confirmation | Politics | short_yes | [0.00, 0.10) | 134 | 326 | 19 | 84865 | 9385 | 3.641 | 0.467 | 7.80 |
| B | exploration | Politics | short_yes | [0.00, 0.10) | 72 | 254 | 13 | 64561 | 7051 | 2.818 | 0.948 | 2.97 |
| B | confirmation | Politics | short_yes | [0.10, 0.30) | 141 | 346 | 50 | 67482 | 8140 | 6.985 | 3.176 | 2.20 |
| B | exploration | Politics | short_yes | [0.10, 0.30) | 80 | 173 | 24 | 73461 | 8429 | -1.906 | 14.602 | -0.13 |
| B | confirmation | Politics | short_yes | [0.30, 0.70) | 160 | 338 | 81 | 62503 | 8121 | 6.690 | 7.061 | 0.95 |
| B | exploration | Politics | short_yes | [0.30, 0.70) | 81 | 135 | 41 | 76590 | 9307 | 2.784 | 9.695 | 0.29 |
| B | confirmation | Politics | short_yes | [0.70, 0.90) | 132 | 210 | 96 | 16669 | 2244 | 0.190 | 5.306 | 0.04 |
| B | exploration | Politics | short_yes | [0.70, 0.90) | 63 | 94 | 46 | 30336 | 3778 | -11.101 | 4.175 | -2.66 |
| B | confirmation | Politics | short_yes | [0.90, 1.00] | 112 | 164 | 93 | 17107 | 2055 | -2.799 | 1.621 | -1.73 |
| B | exploration | Politics | short_yes | [0.90, 1.00] | 55 | 77 | 48 | 15482 | 2050 | -3.678 | 1.134 | -3.24 |
| B | confirmation | Science and Technology | long_yes | [0.00, 0.10) | 65 | 159 | 59 | 17314 | 2167 | -3.216 | 0.436 | -7.38 |
| B | exploration | Science and Technology | long_yes | [0.00, 0.10) | 30 | 79 | 25 | 15087 | 1877 | -2.317 | 1.235 | -1.88 |
| B | confirmation | Science and Technology | long_yes | [0.10, 0.30) | 60 | 125 | 46 | 8662 | 1216 | -6.522 | 3.722 | -1.75 |
| B | exploration | Science and Technology | long_yes | [0.10, 0.30) | 23 | 41 | 19 | 6910 | 882 | -9.340 | 6.066 | -1.54 |
| B | confirmation | Science and Technology | long_yes | [0.30, 0.70) | 66 | 116 | 41 | 13571 | 1743 | -10.684 | 6.101 | -1.75 |
| B | exploration | Science and Technology | long_yes | [0.30, 0.70) | 23 | 30 | 15 | 6195 | 734 | -9.393 | 11.124 | -0.84 |
| B | confirmation | Science and Technology | long_yes | [0.70, 0.90) | 53 | 108 | 17 | 9881 | 1326 | -1.981 | 3.249 | -0.61 |
| B | exploration | Science and Technology | long_yes | [0.70, 0.90) | 24 | 36 | 7 | 5025 | 663 | 6.447 | 4.797 | 1.34 |
| B | confirmation | Science and Technology | long_yes | [0.90, 1.00] | 55 | 126 | 11 | 12561 | 1582 | 1.449 | 1.021 | 1.42 |
| B | exploration | Science and Technology | long_yes | [0.90, 1.00] | 25 | 47 | 3 | 7950 | 1023 | 1.670 | 1.980 | 0.84 |
| B | confirmation | Science and Technology | short_yes | [0.00, 0.10) | 59 | 145 | 4 | 26732 | 2916 | 2.628 | 0.408 | 6.44 |
| B | exploration | Science and Technology | short_yes | [0.00, 0.10) | 35 | 95 | 8 | 44422 | 4683 | 1.345 | 1.205 | 1.12 |
| B | confirmation | Science and Technology | short_yes | [0.10, 0.30) | 59 | 115 | 16 | 11485 | 1399 | 3.717 | 4.342 | 0.86 |
| B | exploration | Science and Technology | short_yes | [0.10, 0.30) | 27 | 46 | 5 | 11806 | 1355 | 11.250 | 3.861 | 2.91 |
| B | confirmation | Science and Technology | short_yes | [0.30, 0.70) | 66 | 127 | 37 | 16219 | 2162 | 4.114 | 6.319 | 0.65 |
| B | exploration | Science and Technology | short_yes | [0.30, 0.70) | 24 | 36 | 10 | 9149 | 1104 | -3.469 | 8.421 | -0.41 |
| B | confirmation | Science and Technology | short_yes | [0.70, 0.90) | 57 | 138 | 42 | 14258 | 2049 | -2.877 | 3.181 | -0.90 |
| B | exploration | Science and Technology | short_yes | [0.70, 0.90) | 26 | 45 | 16 | 9060 | 1212 | -7.072 | 4.567 | -1.55 |
| B | confirmation | Science and Technology | short_yes | [0.90, 1.00] | 56 | 150 | 48 | 14151 | 2192 | -1.557 | 1.240 | -1.26 |
| B | exploration | Science and Technology | short_yes | [0.90, 1.00] | 26 | 55 | 25 | 8942 | 1383 | -2.299 | 3.311 | -0.69 |
| B | confirmation | Social | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 70 | 7 | -4.714 | n/a | n/a |
| B | exploration | Social | long_yes | [0.00, 0.10) | 4 | 4 | 4 | 464 | 57 | -4.446 | 0.103 | -43.11 |
| B | confirmation | Social | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 26 | 5 | -7.615 | n/a | n/a |
| B | exploration | Social | long_yes | [0.10, 0.30) | 3 | 3 | 3 | 111 | 19 | -15.856 | 0.438 | -36.18 |
| B | confirmation | Social | long_yes | [0.30, 0.70) | 1 | 1 | 1 | 120 | 14 | -24.933 | n/a | n/a |
| B | exploration | Social | long_yes | [0.30, 0.70) | 3 | 3 | 2 | 71 | 10 | -36.465 | 2.849 | -12.80 |
| B | exploration | Social | long_yes | [0.70, 0.90) | 2 | 2 | 0 | 72 | 8 | 19.611 | 3.673 | 5.34 |
| B | confirmation | Social | long_yes | [0.90, 1.00] | 2 | 2 | 0 | 61 | 9 | 6.377 | 3.526 | 1.81 |
| B | exploration | Social | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 30 | 3 | 6.667 | n/a | n/a |
| B | exploration | Social | short_yes | [0.00, 0.10) | 4 | 5 | 0 | 1421 | 155 | 4.884 | 0.710 | 6.88 |
| B | confirmation | Social | short_yes | [0.10, 0.30) | 1 | 1 | 1 | 10 | 1 | -73.000 | n/a | n/a |
| B | exploration | Social | short_yes | [0.10, 0.30) | 3 | 3 | 0 | 160 | 21 | 16.406 | 0.431 | 38.04 |
| B | confirmation | Social | short_yes | [0.30, 0.70) | 2 | 2 | 2 | 102 | 12 | -45.549 | 0.266 | -171.45 |
| B | exploration | Social | short_yes | [0.30, 0.70) | 4 | 4 | 2 | 82 | 14 | 24.756 | 17.127 | 1.45 |
| B | confirmation | Social | short_yes | [0.70, 0.90) | 1 | 1 | 0 | 10 | 1 | 77.000 | n/a | n/a |
| B | exploration | Social | short_yes | [0.70, 0.90) | 2 | 2 | 2 | 40 | 4 | -21.750 | 2.375 | -9.16 |
| B | confirmation | Social | short_yes | [0.90, 1.00] | 2 | 2 | 2 | 117 | 12 | -5.615 | 0.131 | -42.71 |
| B | exploration | Social | short_yes | [0.90, 1.00] | 3 | 3 | 3 | 30 | 3 | -5.667 | 1.667 | -3.40 |
| B | exploration | Transportation | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 10 | 1 | -8.000 | n/a | n/a |
| B | exploration | Transportation | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 2 | 1 | -12.000 | n/a | n/a |
| B | exploration | Transportation | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 20 | 2 | 7.000 | n/a | n/a |
| B | exploration | Transportation | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 45 | 5 | 13.667 | n/a | n/a |
| B | exploration | Transportation | short_yes | [0.30, 0.70) | 1 | 1 | 0 | 10 | 1 | 49.000 | n/a | n/a |
| B | exploration | World | long_yes | [0.00, 0.10) | 1 | 10 | 1 | 231 | 33 | -3.121 | n/a | n/a |
| B | exploration | World | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 26 | 3 | -20.462 | n/a | n/a |
| B | confirmation | World | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 21 | 3 | 5.190 | n/a | n/a |
| B | exploration | World | short_yes | [0.00, 0.10) | 2 | 8 | 1 | 460 | 53 | 2.470 | 0.865 | 2.86 |
| C | confirmation | ALL | long_yes | [0.00, 0.10) | 970 | 12511 | 794 | 49379592 | 466227 | 1.130 | 0.821 | 1.38 |
| C | exploration | ALL | long_yes | [0.00, 0.10) | 705 | 5496 | 592 | 5247921 | 49510 | 0.091 | 0.747 | 0.12 |
| C | confirmation | ALL | long_yes | [0.10, 0.30) | 1055 | 13781 | 726 | 27493367 | 231703 | 0.147 | 1.426 | 0.10 |
| C | exploration | ALL | long_yes | [0.10, 0.30) | 768 | 6376 | 534 | 5635201 | 75030 | -2.319 | 1.372 | -1.69 |
| C | confirmation | ALL | long_yes | [0.30, 0.70) | 1113 | 16789 | 609 | 63436320 | 487634 | 0.798 | 1.328 | 0.60 |
| C | exploration | ALL | long_yes | [0.30, 0.70) | 783 | 7443 | 442 | 10539876 | 145786 | 0.282 | 1.798 | 0.16 |
| C | confirmation | ALL | long_yes | [0.70, 0.90) | 988 | 10680 | 315 | 25601361 | 170672 | 1.136 | 1.541 | 0.74 |
| C | exploration | ALL | long_yes | [0.70, 0.90) | 711 | 4509 | 198 | 4679070 | 50368 | 1.022 | 1.499 | 0.68 |
| C | confirmation | ALL | long_yes | [0.90, 1.00] | 882 | 8480 | 142 | 45824053 | 427223 | 0.364 | 0.579 | 0.63 |
| C | exploration | ALL | long_yes | [0.90, 1.00] | 621 | 3532 | 85 | 4375275 | 38582 | 0.628 | 0.742 | 0.85 |
| C | confirmation | ALL | short_yes | [0.00, 0.10) | 1007 | 11606 | 144 | 52948323 | 485133 | -0.585 | 0.871 | -0.67 |
| C | exploration | ALL | short_yes | [0.00, 0.10) | 778 | 5631 | 91 | 8131674 | 57972 | 1.129 | 0.552 | 2.05 |
| C | confirmation | ALL | short_yes | [0.10, 0.30) | 1097 | 13946 | 348 | 29192154 | 228522 | -0.239 | 1.324 | -0.18 |
| C | exploration | ALL | short_yes | [0.10, 0.30) | 824 | 6892 | 227 | 7352706 | 87842 | 1.951 | 1.555 | 1.25 |
| C | confirmation | ALL | short_yes | [0.30, 0.70) | 1149 | 18336 | 541 | 70083510 | 568208 | -0.643 | 1.395 | -0.46 |
| C | exploration | ALL | short_yes | [0.30, 0.70) | 823 | 8391 | 332 | 14166700 | 189555 | 3.286 | 1.668 | 1.97 |
| C | confirmation | ALL | short_yes | [0.70, 0.90) | 1068 | 12942 | 693 | 26918690 | 225733 | -0.699 | 1.402 | -0.50 |
| C | exploration | ALL | short_yes | [0.70, 0.90) | 740 | 5644 | 471 | 5972714 | 68399 | 0.627 | 1.414 | 0.44 |
| C | confirmation | ALL | short_yes | [0.90, 1.00] | 958 | 11174 | 766 | 47034637 | 428479 | -0.078 | 0.650 | -0.12 |
| C | exploration | ALL | short_yes | [0.90, 1.00] | 669 | 4436 | 521 | 5022243 | 42805 | 1.272 | 0.813 | 1.56 |
| C | confirmation | Climate and Weather | long_yes | [0.00, 0.10) | 139 | 3586 | 102 | 735897 | 22320 | -0.714 | 0.456 | -1.56 |
| C | exploration | Climate and Weather | long_yes | [0.00, 0.10) | 137 | 1902 | 98 | 643585 | 10769 | 0.366 | 0.666 | 0.55 |
| C | confirmation | Climate and Weather | long_yes | [0.10, 0.30) | 140 | 3437 | 85 | 774296 | 33806 | -0.249 | 1.155 | -0.22 |
| C | exploration | Climate and Weather | long_yes | [0.10, 0.30) | 138 | 1948 | 88 | 572600 | 18684 | -2.122 | 1.068 | -1.99 |
| C | confirmation | Climate and Weather | long_yes | [0.30, 0.70) | 141 | 3202 | 86 | 671025 | 34614 | -3.398 | 1.335 | -2.54 |
| C | exploration | Climate and Weather | long_yes | [0.30, 0.70) | 140 | 1729 | 76 | 472284 | 16873 | -1.950 | 1.507 | -1.29 |
| C | confirmation | Climate and Weather | long_yes | [0.70, 0.90) | 136 | 1413 | 57 | 185528 | 8484 | -2.196 | 2.223 | -0.99 |
| C | exploration | Climate and Weather | long_yes | [0.70, 0.90) | 116 | 657 | 39 | 139740 | 4090 | 0.882 | 2.811 | 0.31 |
| C | confirmation | Climate and Weather | long_yes | [0.90, 1.00] | 128 | 996 | 28 | 168270 | 3629 | -3.129 | 4.292 | -0.73 |
| C | exploration | Climate and Weather | long_yes | [0.90, 1.00] | 109 | 491 | 18 | 129464 | 1814 | 0.610 | 1.109 | 0.55 |
| C | confirmation | Climate and Weather | short_yes | [0.00, 0.10) | 142 | 2982 | 27 | 1014084 | 18909 | 1.458 | 0.522 | 2.79 |
| C | exploration | Climate and Weather | short_yes | [0.00, 0.10) | 138 | 1729 | 26 | 1119699 | 9763 | 1.146 | 0.430 | 2.66 |
| C | confirmation | Climate and Weather | short_yes | [0.10, 0.30) | 138 | 3507 | 53 | 948533 | 36223 | 0.438 | 1.145 | 0.38 |
| C | exploration | Climate and Weather | short_yes | [0.10, 0.30) | 139 | 2174 | 51 | 779350 | 21712 | 1.541 | 1.068 | 1.44 |
| C | confirmation | Climate and Weather | short_yes | [0.30, 0.70) | 140 | 4070 | 66 | 1297809 | 62644 | 0.925 | 0.870 | 1.06 |
| C | exploration | Climate and Weather | short_yes | [0.30, 0.70) | 140 | 2167 | 55 | 934558 | 34050 | 4.951 | 1.389 | 3.56 |
| C | confirmation | Climate and Weather | short_yes | [0.70, 0.90) | 139 | 2309 | 82 | 464913 | 20518 | 1.838 | 2.144 | 0.86 |
| C | exploration | Climate and Weather | short_yes | [0.70, 0.90) | 127 | 962 | 81 | 260606 | 8252 | 0.914 | 2.207 | 0.41 |
| C | confirmation | Climate and Weather | short_yes | [0.90, 1.00] | 133 | 2166 | 102 | 354433 | 12273 | 1.003 | 1.152 | 0.87 |
| C | exploration | Climate and Weather | short_yes | [0.90, 1.00] | 114 | 711 | 92 | 195785 | 3180 | 2.145 | 1.767 | 1.21 |
| C | confirmation | Commodities | long_yes | [0.00, 0.10) | 96 | 829 | 77 | 1498714 | 14103 | 1.018 | 1.077 | 0.95 |
| C | exploration | Commodities | long_yes | [0.00, 0.10) | 37 | 65 | 32 | 34506 | 537 | -2.990 | 1.027 | -2.91 |
| C | confirmation | Commodities | long_yes | [0.10, 0.30) | 102 | 992 | 67 | 849488 | 13967 | 0.731 | 1.897 | 0.39 |
| C | exploration | Commodities | long_yes | [0.10, 0.30) | 48 | 87 | 32 | 54675 | 1124 | -7.074 | 4.548 | -1.56 |
| C | confirmation | Commodities | long_yes | [0.30, 0.70) | 108 | 1376 | 50 | 1672214 | 29328 | -0.890 | 1.847 | -0.48 |
| C | exploration | Commodities | long_yes | [0.30, 0.70) | 48 | 99 | 27 | 90202 | 2373 | -10.962 | 8.409 | -1.30 |
| C | confirmation | Commodities | long_yes | [0.70, 0.90) | 100 | 927 | 28 | 669595 | 10447 | -0.070 | 2.191 | -0.03 |
| C | exploration | Commodities | long_yes | [0.70, 0.90) | 37 | 60 | 15 | 83644 | 823 | 3.820 | 11.306 | 0.34 |
| C | confirmation | Commodities | long_yes | [0.90, 1.00] | 91 | 700 | 13 | 1209046 | 11204 | 1.133 | 0.552 | 2.05 |
| C | exploration | Commodities | long_yes | [0.90, 1.00] | 28 | 41 | 9 | 25257 | 256 | -2.590 | 3.835 | -0.68 |
| C | confirmation | Commodities | short_yes | [0.00, 0.10) | 102 | 757 | 16 | 1297090 | 10903 | 0.013 | 0.882 | 0.01 |
| C | exploration | Commodities | short_yes | [0.00, 0.10) | 41 | 63 | 4 | 63754 | 590 | 2.063 | 1.453 | 1.42 |
| C | confirmation | Commodities | short_yes | [0.10, 0.30) | 108 | 973 | 36 | 771355 | 10999 | -0.773 | 2.425 | -0.32 |
| C | exploration | Commodities | short_yes | [0.10, 0.30) | 47 | 86 | 7 | 82185 | 1640 | 6.403 | 4.921 | 1.30 |
| C | confirmation | Commodities | short_yes | [0.30, 0.70) | 107 | 1451 | 53 | 1950600 | 33304 | 0.082 | 2.065 | 0.04 |
| C | exploration | Commodities | short_yes | [0.30, 0.70) | 52 | 122 | 16 | 118979 | 3167 | 15.548 | 8.230 | 1.89 |
| C | confirmation | Commodities | short_yes | [0.70, 0.90) | 105 | 1097 | 69 | 996181 | 15372 | 5.025 | 2.146 | 2.34 |
| C | exploration | Commodities | short_yes | [0.70, 0.90) | 44 | 92 | 19 | 79091 | 1305 | 26.470 | 10.891 | 2.43 |
| C | confirmation | Commodities | short_yes | [0.90, 1.00] | 92 | 908 | 72 | 1452112 | 14899 | 0.189 | 0.698 | 0.27 |
| C | exploration | Commodities | short_yes | [0.90, 1.00] | 33 | 62 | 23 | 34731 | 418 | 5.306 | 5.527 | 0.96 |
| C | confirmation | Companies | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 1 | 1 | -5.000 | n/a | n/a |
| C | exploration | Companies | long_yes | [0.00, 0.10) | 2 | 3 | 2 | 3120 | 9 | -6.587 | 0.156 | -42.23 |
| C | exploration | Companies | long_yes | [0.10, 0.30) | 3 | 3 | 2 | 58275 | 151 | -16.155 | 0.209 | -77.15 |
| C | exploration | Companies | long_yes | [0.30, 0.70) | 2 | 2 | 1 | 41001 | 278 | -8.957 | 5.649 | -1.59 |
| C | exploration | Companies | long_yes | [0.70, 0.90) | 2 | 2 | 0 | 7116 | 77 | 4.849 | 1.786 | 2.71 |
| C | exploration | Companies | long_yes | [0.90, 1.00] | 1 | 1 | 0 | 1489 | 14 | 6.835 | n/a | n/a |
| C | confirmation | Companies | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 161 | 2 | 5.000 | n/a | n/a |
| C | exploration | Companies | short_yes | [0.00, 0.10) | 3 | 7 | 0 | 2839 | 16 | 3.918 | 0.650 | 6.03 |
| C | confirmation | Companies | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 1 | 1 | 16.000 | n/a | n/a |
| C | exploration | Companies | short_yes | [0.10, 0.30) | 3 | 3 | 1 | 41052 | 208 | 4.764 | 16.322 | 0.29 |
| C | exploration | Companies | short_yes | [0.30, 0.70) | 2 | 2 | 1 | 33804 | 287 | 0.080 | 1.342 | 0.06 |
| C | exploration | Companies | short_yes | [0.70, 0.90) | 2 | 2 | 2 | 21070 | 84 | -21.700 | 1.063 | -20.41 |
| C | exploration | Companies | short_yes | [0.90, 1.00] | 1 | 1 | 0 | 280 | 15 | 16.568 | n/a | n/a |
| C | confirmation | Crypto | long_yes | [0.00, 0.10) | 127 | 6380 | 88 | 45706752 | 413267 | 1.243 | 0.887 | 1.40 |
| C | exploration | Crypto | long_yes | [0.00, 0.10) | 124 | 2581 | 97 | 3710274 | 29349 | 0.548 | 1.026 | 0.53 |
| C | confirmation | Crypto | long_yes | [0.10, 0.30) | 128 | 7308 | 82 | 24677707 | 159541 | 0.394 | 1.589 | 0.25 |
| C | exploration | Crypto | long_yes | [0.10, 0.30) | 125 | 3184 | 83 | 4002412 | 38941 | -1.698 | 1.788 | -0.95 |
| C | confirmation | Crypto | long_yes | [0.30, 0.70) | 133 | 9884 | 68 | 59532842 | 383691 | 1.032 | 1.418 | 0.73 |
| C | exploration | Crypto | long_yes | [0.30, 0.70) | 129 | 4268 | 65 | 8675988 | 98593 | 0.904 | 2.114 | 0.43 |
| C | confirmation | Crypto | long_yes | [0.70, 0.90) | 128 | 6654 | 49 | 23885382 | 136179 | 1.159 | 1.654 | 0.70 |
| C | exploration | Crypto | long_yes | [0.70, 0.90) | 128 | 2736 | 37 | 3817847 | 34749 | 0.773 | 1.759 | 0.44 |
| C | confirmation | Crypto | long_yes | [0.90, 1.00] | 127 | 5646 | 30 | 43501325 | 406406 | 0.387 | 0.608 | 0.64 |
| C | exploration | Crypto | long_yes | [0.90, 1.00] | 123 | 2233 | 21 | 3657339 | 32354 | 0.691 | 0.844 | 0.82 |
| C | confirmation | Crypto | short_yes | [0.00, 0.10) | 129 | 6125 | 37 | 47531857 | 438794 | -0.753 | 0.967 | -0.78 |
| C | exploration | Crypto | short_yes | [0.00, 0.10) | 127 | 2583 | 17 | 4332368 | 35152 | 0.294 | 0.978 | 0.30 |
| C | confirmation | Crypto | short_yes | [0.10, 0.30) | 129 | 7104 | 57 | 25099747 | 144742 | -0.688 | 1.528 | -0.45 |
| C | exploration | Crypto | short_yes | [0.10, 0.30) | 129 | 3102 | 35 | 4677999 | 37444 | 1.674 | 2.247 | 0.75 |
| C | confirmation | Crypto | short_yes | [0.30, 0.70) | 132 | 10050 | 65 | 64079634 | 408767 | -0.805 | 1.527 | -0.53 |
| C | exploration | Crypto | short_yes | [0.30, 0.70) | 131 | 4464 | 62 | 10851852 | 107853 | 2.283 | 2.117 | 1.08 |
| C | confirmation | Crypto | short_yes | [0.70, 0.90) | 131 | 7395 | 79 | 24297223 | 166498 | -1.066 | 1.551 | -0.69 |
| C | exploration | Crypto | short_yes | [0.70, 0.90) | 127 | 3290 | 81 | 4561974 | 43565 | 0.811 | 1.787 | 0.45 |
| C | confirmation | Crypto | short_yes | [0.90, 1.00] | 128 | 6473 | 96 | 43975187 | 388394 | -0.122 | 0.695 | -0.18 |
| C | exploration | Crypto | short_yes | [0.90, 1.00] | 121 | 2693 | 83 | 3864503 | 31324 | 1.111 | 0.952 | 1.17 |
| C | confirmation | Economics | long_yes | [0.00, 0.10) | 111 | 215 | 101 | 105200 | 857 | -1.869 | 1.220 | -1.53 |
| C | exploration | Economics | long_yes | [0.00, 0.10) | 51 | 84 | 49 | 83130 | 379 | -3.289 | 0.554 | -5.94 |
| C | confirmation | Economics | long_yes | [0.10, 0.30) | 127 | 283 | 94 | 100520 | 1810 | -0.570 | 5.200 | -0.11 |
| C | exploration | Economics | long_yes | [0.10, 0.30) | 62 | 93 | 48 | 47303 | 711 | -2.184 | 5.003 | -0.44 |
| C | confirmation | Economics | long_yes | [0.30, 0.70) | 130 | 335 | 78 | 120554 | 3018 | -10.036 | 6.572 | -1.53 |
| C | exploration | Economics | long_yes | [0.30, 0.70) | 66 | 107 | 43 | 83858 | 1239 | -19.358 | 9.667 | -2.00 |
| C | confirmation | Economics | long_yes | [0.70, 0.90) | 118 | 242 | 35 | 138622 | 1424 | -0.248 | 9.937 | -0.02 |
| C | exploration | Economics | long_yes | [0.70, 0.90) | 61 | 89 | 19 | 38320 | 541 | -8.030 | 8.248 | -0.97 |
| C | confirmation | Economics | long_yes | [0.90, 1.00] | 106 | 170 | 16 | 83837 | 657 | -11.982 | 9.509 | -1.26 |
| C | exploration | Economics | long_yes | [0.90, 1.00] | 49 | 64 | 4 | 53854 | 216 | 1.829 | 2.216 | 0.83 |
| C | confirmation | Economics | short_yes | [0.00, 0.10) | 116 | 227 | 9 | 231863 | 1198 | 3.285 | 0.584 | 5.62 |
| C | exploration | Economics | short_yes | [0.00, 0.10) | 63 | 126 | 4 | 209155 | 670 | 3.623 | 0.493 | 7.35 |
| C | confirmation | Economics | short_yes | [0.10, 0.30) | 126 | 322 | 31 | 156714 | 2362 | 5.897 | 2.790 | 2.11 |
| C | exploration | Economics | short_yes | [0.10, 0.30) | 67 | 124 | 13 | 99575 | 1115 | 5.366 | 5.820 | 0.92 |
| C | confirmation | Economics | short_yes | [0.30, 0.70) | 130 | 372 | 56 | 214630 | 4378 | -10.030 | 5.739 | -1.75 |
| C | exploration | Economics | short_yes | [0.30, 0.70) | 71 | 134 | 27 | 99463 | 2091 | 16.231 | 5.064 | 3.21 |
| C | confirmation | Economics | short_yes | [0.70, 0.90) | 126 | 307 | 92 | 158273 | 2329 | -6.486 | 2.956 | -2.19 |
| C | exploration | Economics | short_yes | [0.70, 0.90) | 64 | 102 | 45 | 56427 | 594 | -8.209 | 4.115 | -1.99 |
| C | confirmation | Economics | short_yes | [0.90, 1.00] | 113 | 262 | 95 | 134052 | 1036 | -0.640 | 2.054 | -0.31 |
| C | exploration | Economics | short_yes | [0.90, 1.00] | 56 | 83 | 49 | 109681 | 339 | -3.812 | 1.148 | -3.32 |
| C | confirmation | Elections | long_yes | [0.00, 0.10) | 38 | 44 | 34 | 67313 | 362 | 15.395 | 11.233 | 1.37 |
| C | exploration | Elections | long_yes | [0.00, 0.10) | 6 | 9 | 5 | 16350 | 59 | -0.254 | 4.628 | -0.05 |
| C | confirmation | Elections | long_yes | [0.10, 0.30) | 39 | 52 | 29 | 34470 | 251 | 17.264 | 12.945 | 1.33 |
| C | exploration | Elections | long_yes | [0.10, 0.30) | 9 | 8 | 6 | 24957 | 72 | -2.650 | 11.076 | -0.24 |
| C | confirmation | Elections | long_yes | [0.30, 0.70) | 38 | 45 | 21 | 129975 | 503 | 5.992 | 17.727 | 0.34 |
| C | exploration | Elections | long_yes | [0.30, 0.70) | 7 | 7 | 4 | 12064 | 118 | 8.141 | 28.793 | 0.28 |
| C | confirmation | Elections | long_yes | [0.70, 0.90) | 28 | 34 | 7 | 44571 | 219 | -0.839 | 14.445 | -0.06 |
| C | exploration | Elections | long_yes | [0.70, 0.90) | 6 | 8 | 1 | 4535 | 74 | -25.831 | 22.549 | -1.15 |
| C | confirmation | Elections | long_yes | [0.90, 1.00] | 23 | 31 | 2 | 183872 | 514 | -11.518 | 16.102 | -0.72 |
| C | exploration | Elections | long_yes | [0.90, 1.00] | 5 | 5 | 0 | 541 | 15 | 6.255 | 1.834 | 3.41 |
| C | confirmation | Elections | short_yes | [0.00, 0.10) | 33 | 48 | 4 | 217001 | 668 | -18.496 | 11.136 | -1.66 |
| C | exploration | Elections | short_yes | [0.00, 0.10) | 10 | 13 | 2 | 48025 | 79 | 4.666 | 1.895 | 2.46 |
| C | confirmation | Elections | short_yes | [0.10, 0.30) | 37 | 51 | 15 | 95787 | 416 | -32.103 | 16.457 | -1.95 |
| C | exploration | Elections | short_yes | [0.10, 0.30) | 11 | 11 | 3 | 55493 | 133 | -30.700 | 31.518 | -0.97 |
| C | confirmation | Elections | short_yes | [0.30, 0.70) | 47 | 45 | 21 | 127332 | 681 | -17.011 | 11.624 | -1.46 |
| C | exploration | Elections | short_yes | [0.30, 0.70) | 8 | 10 | 3 | 8278 | 123 | -45.551 | 6.597 | -6.90 |
| C | confirmation | Elections | short_yes | [0.70, 0.90) | 32 | 40 | 23 | 83626 | 337 | 22.399 | 19.857 | 1.13 |
| C | exploration | Elections | short_yes | [0.70, 0.90) | 2 | 4 | 2 | 3008 | 66 | -3.710 | 5.464 | -0.68 |
| C | confirmation | Elections | short_yes | [0.90, 1.00] | 26 | 37 | 23 | 159171 | 686 | 12.570 | 16.802 | 0.75 |
| C | exploration | Elections | short_yes | [0.90, 1.00] | 5 | 7 | 5 | 606 | 10 | -5.198 | 0.792 | -6.56 |
| C | confirmation | Entertainment | long_yes | [0.00, 0.10) | 106 | 372 | 85 | 206048 | 2402 | -0.568 | 0.897 | -0.63 |
| C | exploration | Entertainment | long_yes | [0.00, 0.10) | 88 | 257 | 85 | 145086 | 1358 | -3.744 | 1.027 | -3.64 |
| C | confirmation | Entertainment | long_yes | [0.10, 0.30) | 107 | 355 | 76 | 226938 | 4257 | -5.290 | 3.081 | -1.72 |
| C | exploration | Entertainment | long_yes | [0.10, 0.30) | 89 | 244 | 66 | 189198 | 2342 | -6.861 | 3.003 | -2.28 |
| C | confirmation | Entertainment | long_yes | [0.30, 0.70) | 111 | 343 | 57 | 245792 | 5986 | -0.655 | 4.045 | -0.16 |
| C | exploration | Entertainment | long_yes | [0.30, 0.70) | 88 | 224 | 51 | 196449 | 2698 | 10.978 | 11.091 | 0.99 |
| C | confirmation | Entertainment | long_yes | [0.70, 0.90) | 105 | 276 | 32 | 176019 | 3055 | 5.433 | 2.852 | 1.90 |
| C | exploration | Entertainment | long_yes | [0.70, 0.90) | 93 | 191 | 26 | 90506 | 1287 | 2.689 | 4.837 | 0.56 |
| C | confirmation | Entertainment | long_yes | [0.90, 1.00] | 98 | 248 | 14 | 183676 | 1394 | 3.247 | 0.551 | 5.90 |
| C | exploration | Entertainment | long_yes | [0.90, 1.00] | 87 | 179 | 7 | 118455 | 739 | 0.791 | 3.058 | 0.26 |
| C | confirmation | Entertainment | short_yes | [0.00, 0.10) | 110 | 419 | 18 | 704816 | 3857 | 1.378 | 0.704 | 1.96 |
| C | exploration | Entertainment | short_yes | [0.00, 0.10) | 106 | 367 | 2 | 693793 | 2839 | 2.973 | 0.377 | 7.88 |
| C | confirmation | Entertainment | short_yes | [0.10, 0.30) | 119 | 417 | 32 | 363853 | 6411 | 6.486 | 2.474 | 2.62 |
| C | exploration | Entertainment | short_yes | [0.10, 0.30) | 101 | 310 | 18 | 309039 | 3623 | 10.693 | 2.195 | 4.87 |
| C | confirmation | Entertainment | short_yes | [0.30, 0.70) | 120 | 418 | 63 | 354441 | 7891 | 2.947 | 4.375 | 0.67 |
| C | exploration | Entertainment | short_yes | [0.30, 0.70) | 95 | 271 | 40 | 279591 | 3847 | -4.988 | 7.152 | -0.70 |
| C | confirmation | Entertainment | short_yes | [0.70, 0.90) | 116 | 348 | 71 | 190219 | 3033 | -2.390 | 3.836 | -0.62 |
| C | exploration | Entertainment | short_yes | [0.70, 0.90) | 95 | 240 | 60 | 120834 | 1576 | 0.410 | 4.651 | 0.09 |
| C | confirmation | Entertainment | short_yes | [0.90, 1.00] | 113 | 357 | 95 | 196328 | 1676 | -0.525 | 1.865 | -0.28 |
| C | exploration | Entertainment | short_yes | [0.90, 1.00] | 97 | 218 | 78 | 83188 | 840 | 1.426 | 3.965 | 0.36 |
| C | confirmation | Financials | long_yes | [0.00, 0.10) | 85 | 372 | 71 | 81995 | 3004 | -1.443 | 0.890 | -1.62 |
| C | exploration | Financials | long_yes | [0.00, 0.10) | 50 | 96 | 41 | 18741 | 266 | 9.187 | 11.308 | 0.81 |
| C | confirmation | Financials | long_yes | [0.10, 0.30) | 92 | 398 | 68 | 97227 | 2052 | -2.268 | 4.409 | -0.51 |
| C | exploration | Financials | long_yes | [0.10, 0.30) | 70 | 123 | 46 | 24530 | 469 | 20.402 | 15.796 | 1.29 |
| C | confirmation | Financials | long_yes | [0.30, 0.70) | 95 | 486 | 44 | 167157 | 2958 | 7.377 | 5.327 | 1.38 |
| C | exploration | Financials | long_yes | [0.30, 0.70) | 69 | 127 | 36 | 45207 | 722 | 20.238 | 14.586 | 1.39 |
| C | confirmation | Financials | long_yes | [0.70, 0.90) | 84 | 308 | 15 | 80425 | 1549 | 9.368 | 4.414 | 2.12 |
| C | exploration | Financials | long_yes | [0.70, 0.90) | 51 | 80 | 10 | 13346 | 290 | 7.022 | 6.404 | 1.10 |
| C | confirmation | Financials | long_yes | [0.90, 1.00] | 75 | 190 | 9 | 64990 | 565 | 2.431 | 1.171 | 2.08 |
| C | exploration | Financials | long_yes | [0.90, 1.00] | 36 | 51 | 5 | 10872 | 110 | 2.262 | 0.912 | 2.48 |
| C | confirmation | Financials | short_yes | [0.00, 0.10) | 85 | 269 | 9 | 126763 | 820 | 2.322 | 1.153 | 2.01 |
| C | exploration | Financials | short_yes | [0.00, 0.10) | 68 | 126 | 6 | 62512 | 487 | -3.061 | 4.836 | -0.63 |
| C | confirmation | Financials | short_yes | [0.10, 0.30) | 93 | 424 | 31 | 159994 | 1741 | 4.313 | 4.525 | 0.95 |
| C | exploration | Financials | short_yes | [0.10, 0.30) | 88 | 187 | 23 | 56440 | 898 | 10.704 | 3.241 | 3.30 |
| C | confirmation | Financials | short_yes | [0.30, 0.70) | 104 | 606 | 39 | 156890 | 3583 | 0.642 | 3.984 | 0.16 |
| C | exploration | Financials | short_yes | [0.30, 0.70) | 87 | 173 | 31 | 41598 | 1025 | 10.898 | 8.268 | 1.32 |
| C | confirmation | Financials | short_yes | [0.70, 0.90) | 96 | 432 | 67 | 85047 | 2063 | -3.688 | 3.478 | -1.06 |
| C | exploration | Financials | short_yes | [0.70, 0.90) | 58 | 101 | 36 | 33678 | 374 | -4.811 | 8.099 | -0.59 |
| C | confirmation | Financials | short_yes | [0.90, 1.00] | 78 | 307 | 63 | 63200 | 2305 | -0.884 | 1.409 | -0.63 |
| C | exploration | Financials | short_yes | [0.90, 1.00] | 49 | 75 | 36 | 9962 | 209 | 10.010 | 7.187 | 1.39 |
| C | exploration | Health | long_yes | [0.00, 0.10) | 2 | 2 | 2 | 348 | 6 | -5.638 | 0.353 | -15.96 |
| C | exploration | Health | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 10 | 1 | -10.000 | n/a | n/a |
| C | exploration | Health | long_yes | [0.30, 0.70) | 2 | 2 | 2 | 338 | 4 | -33.269 | 1.081 | -30.78 |
| C | exploration | Health | short_yes | [0.00, 0.10) | 2 | 3 | 0 | 622 | 17 | 4.116 | 0.078 | 52.94 |
| C | exploration | Health | short_yes | [0.10, 0.30) | 3 | 3 | 0 | 300 | 11 | 23.720 | 1.190 | 19.93 |
| C | exploration | Health | short_yes | [0.30, 0.70) | 1 | 1 | 0 | 10 | 1 | 31.000 | n/a | n/a |
| C | confirmation | Mentions | long_yes | [0.00, 0.10) | 129 | 432 | 105 | 336761 | 7751 | -1.188 | 0.745 | -1.59 |
| C | exploration | Mentions | long_yes | [0.00, 0.10) | 119 | 305 | 102 | 341655 | 5738 | -0.568 | 1.356 | -0.42 |
| C | confirmation | Mentions | long_yes | [0.10, 0.30) | 159 | 641 | 107 | 342524 | 13714 | -2.420 | 2.030 | -1.19 |
| C | exploration | Mentions | long_yes | [0.10, 0.30) | 137 | 537 | 97 | 391909 | 11127 | -3.844 | 3.573 | -1.08 |
| C | confirmation | Mentions | long_yes | [0.30, 0.70) | 179 | 814 | 104 | 638994 | 23886 | -7.527 | 2.223 | -3.39 |
| C | exploration | Mentions | long_yes | [0.30, 0.70) | 145 | 750 | 91 | 639242 | 20148 | -9.185 | 2.460 | -3.73 |
| C | confirmation | Mentions | long_yes | [0.70, 0.90) | 160 | 635 | 56 | 292777 | 7833 | 0.288 | 2.322 | 0.12 |
| C | exploration | Mentions | long_yes | [0.70, 0.90) | 142 | 593 | 38 | 306653 | 6980 | 0.753 | 3.599 | 0.21 |
| C | confirmation | Mentions | long_yes | [0.90, 1.00] | 139 | 363 | 16 | 224000 | 1940 | 3.193 | 0.847 | 3.77 |
| C | exploration | Mentions | long_yes | [0.90, 1.00] | 125 | 394 | 18 | 230493 | 2347 | -3.726 | 3.914 | -0.95 |
| C | confirmation | Mentions | short_yes | [0.00, 0.10) | 138 | 477 | 17 | 793376 | 7005 | 1.541 | 0.796 | 1.93 |
| C | exploration | Mentions | short_yes | [0.00, 0.10) | 123 | 370 | 21 | 892784 | 6388 | 1.747 | 0.614 | 2.85 |
| C | confirmation | Mentions | short_yes | [0.10, 0.30) | 172 | 821 | 50 | 1002584 | 22301 | 3.922 | 1.636 | 2.40 |
| C | exploration | Mentions | short_yes | [0.10, 0.30) | 142 | 706 | 50 | 927906 | 18764 | 3.643 | 2.482 | 1.47 |
| C | confirmation | Mentions | short_yes | [0.30, 0.70) | 181 | 981 | 85 | 1595495 | 42924 | 3.937 | 2.685 | 1.47 |
| C | exploration | Mentions | short_yes | [0.30, 0.70) | 146 | 901 | 58 | 1427549 | 33947 | 9.949 | 2.426 | 4.10 |
| C | confirmation | Mentions | short_yes | [0.70, 0.90) | 176 | 783 | 100 | 513794 | 14044 | 3.374 | 1.834 | 1.84 |
| C | exploration | Mentions | short_yes | [0.70, 0.90) | 143 | 752 | 88 | 652838 | 11063 | -0.631 | 1.997 | -0.32 |
| C | confirmation | Mentions | short_yes | [0.90, 1.00] | 149 | 481 | 116 | 484858 | 6244 | -1.326 | 0.624 | -2.13 |
| C | exploration | Mentions | short_yes | [0.90, 1.00] | 130 | 505 | 97 | 563612 | 5832 | 1.814 | 1.984 | 0.91 |
| C | confirmation | Politics | long_yes | [0.00, 0.10) | 98 | 212 | 92 | 602024 | 1943 | -3.501 | 1.349 | -2.59 |
| C | exploration | Politics | long_yes | [0.00, 0.10) | 60 | 144 | 53 | 207315 | 792 | -3.468 | 1.011 | -3.43 |
| C | confirmation | Politics | long_yes | [0.10, 0.30) | 123 | 247 | 90 | 361314 | 1919 | -12.162 | 1.989 | -6.12 |
| C | exploration | Politics | long_yes | [0.10, 0.30) | 69 | 121 | 50 | 242086 | 1151 | -5.769 | 8.252 | -0.70 |
| C | confirmation | Politics | long_yes | [0.30, 0.70) | 130 | 234 | 73 | 197338 | 2655 | -7.324 | 8.847 | -0.83 |
| C | exploration | Politics | long_yes | [0.30, 0.70) | 69 | 103 | 35 | 251072 | 2364 | 6.739 | 10.150 | 0.66 |
| C | confirmation | Politics | long_yes | [0.70, 0.90) | 86 | 122 | 25 | 85242 | 904 | 2.086 | 9.195 | 0.23 |
| C | exploration | Politics | long_yes | [0.70, 0.90) | 54 | 62 | 12 | 145466 | 1226 | 4.339 | 7.849 | 0.55 |
| C | confirmation | Politics | long_yes | [0.90, 1.00] | 54 | 76 | 9 | 171399 | 687 | 3.185 | 0.868 | 3.67 |
| C | exploration | Politics | long_yes | [0.90, 1.00] | 38 | 46 | 3 | 126001 | 589 | 5.547 | 0.765 | 7.25 |
| C | confirmation | Politics | short_yes | [0.00, 0.10) | 106 | 211 | 6 | 910679 | 2562 | 4.135 | 0.698 | 5.93 |
| C | exploration | Politics | short_yes | [0.00, 0.10) | 60 | 169 | 6 | 424963 | 1358 | 3.843 | 0.633 | 6.07 |
| C | confirmation | Politics | short_yes | [0.10, 0.30) | 125 | 244 | 33 | 534461 | 2727 | 10.101 | 3.311 | 3.05 |
| C | exploration | Politics | short_yes | [0.10, 0.30) | 68 | 143 | 20 | 268066 | 1852 | -7.654 | 10.370 | -0.74 |
| C | confirmation | Politics | short_yes | [0.30, 0.70) | 137 | 259 | 68 | 232418 | 3095 | 5.983 | 8.019 | 0.75 |
| C | exploration | Politics | short_yes | [0.30, 0.70) | 69 | 115 | 32 | 313814 | 2676 | 2.417 | 9.354 | 0.26 |
| C | confirmation | Politics | short_yes | [0.70, 0.90) | 101 | 148 | 80 | 83114 | 974 | -8.907 | 4.799 | -1.86 |
| C | exploration | Politics | short_yes | [0.70, 0.90) | 54 | 64 | 42 | 146727 | 1259 | -3.982 | 6.573 | -0.61 |
| C | confirmation | Politics | short_yes | [0.90, 1.00] | 84 | 105 | 70 | 175994 | 727 | -1.341 | 1.707 | -0.79 |
| C | exploration | Politics | short_yes | [0.90, 1.00] | 41 | 49 | 36 | 148568 | 535 | 4.748 | 8.770 | 0.54 |
| C | confirmation | Science and Technology | long_yes | [0.00, 0.10) | 39 | 67 | 37 | 38458 | 214 | -2.585 | 1.491 | -1.73 |
| C | exploration | Science and Technology | long_yes | [0.00, 0.10) | 23 | 42 | 20 | 43052 | 238 | -2.341 | 1.739 | -1.35 |
| C | confirmation | Science and Technology | long_yes | [0.10, 0.30) | 37 | 67 | 27 | 28881 | 385 | 0.608 | 9.752 | 0.06 |
| C | exploration | Science and Technology | long_yes | [0.10, 0.30) | 14 | 24 | 12 | 27079 | 247 | 5.297 | 17.805 | 0.30 |
| C | confirmation | Science and Technology | long_yes | [0.30, 0.70) | 47 | 69 | 28 | 60122 | 985 | -23.359 | 8.374 | -2.79 |
| C | exploration | Science and Technology | long_yes | [0.30, 0.70) | 17 | 24 | 10 | 32147 | 374 | 1.750 | 18.635 | 0.09 |
| C | confirmation | Science and Technology | long_yes | [0.70, 0.90) | 43 | 69 | 11 | 43201 | 578 | -1.034 | 6.124 | -0.17 |
| C | exploration | Science and Technology | long_yes | [0.70, 0.90) | 19 | 29 | 1 | 31596 | 222 | 18.254 | 2.287 | 7.98 |
| C | confirmation | Science and Technology | long_yes | [0.90, 1.00] | 41 | 60 | 5 | 33637 | 227 | 3.216 | 1.080 | 2.98 |
| C | exploration | Science and Technology | long_yes | [0.90, 1.00] | 20 | 27 | 0 | 21509 | 128 | 6.219 | 0.430 | 14.47 |
| C | confirmation | Science and Technology | short_yes | [0.00, 0.10) | 45 | 90 | 1 | 120632 | 415 | 2.704 | 1.471 | 1.84 |
| C | exploration | Science and Technology | short_yes | [0.00, 0.10) | 32 | 65 | 3 | 274090 | 558 | 1.482 | 1.191 | 1.24 |
| C | confirmation | Science and Technology | short_yes | [0.10, 0.30) | 49 | 82 | 10 | 59126 | 599 | 3.971 | 5.331 | 0.74 |
| C | exploration | Science and Technology | short_yes | [0.10, 0.30) | 22 | 39 | 6 | 54754 | 421 | 9.299 | 4.604 | 2.02 |
| C | confirmation | Science and Technology | short_yes | [0.30, 0.70) | 50 | 83 | 24 | 74149 | 934 | 8.989 | 11.642 | 0.77 |
| C | exploration | Science and Technology | short_yes | [0.30, 0.70) | 18 | 28 | 7 | 57185 | 483 | 0.743 | 13.432 | 0.06 |
| C | confirmation | Science and Technology | short_yes | [0.70, 0.90) | 45 | 82 | 30 | 46225 | 561 | 3.315 | 7.981 | 0.42 |
| C | exploration | Science and Technology | short_yes | [0.70, 0.90) | 21 | 32 | 13 | 36428 | 258 | -6.787 | 9.443 | -0.72 |
| C | confirmation | Science and Technology | short_yes | [0.90, 1.00] | 40 | 76 | 32 | 38992 | 233 | 5.143 | 6.222 | 0.83 |
| C | exploration | Science and Technology | short_yes | [0.90, 1.00] | 19 | 29 | 19 | 10264 | 98 | -3.749 | 1.148 | -3.27 |
| C | confirmation | Social | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 428 | 3 | -8.035 | n/a | n/a |
| C | exploration | Social | long_yes | [0.00, 0.10) | 4 | 3 | 4 | 726 | 7 | -2.642 | 0.649 | -4.07 |
| C | confirmation | Social | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 1 | 1 | -11.000 | n/a | n/a |
| C | exploration | Social | long_yes | [0.10, 0.30) | 2 | 2 | 2 | 133 | 8 | -13.173 | 1.909 | -6.90 |
| C | confirmation | Social | long_yes | [0.30, 0.70) | 1 | 1 | 0 | 305 | 10 | 60.141 | n/a | n/a |
| C | exploration | Social | long_yes | [0.30, 0.70) | 1 | 1 | 1 | 25 | 2 | -40.400 | n/a | n/a |
| C | exploration | Social | long_yes | [0.70, 0.90) | 2 | 2 | 0 | 301 | 9 | 19.246 | 0.807 | 23.84 |
| C | exploration | Social | short_yes | [0.00, 0.10) | 3 | 3 | 0 | 3681 | 25 | 2.656 | 0.319 | 8.33 |
| C | exploration | Social | short_yes | [0.10, 0.30) | 3 | 3 | 0 | 463 | 15 | 16.315 | 4.419 | 3.69 |
| C | confirmation | Social | short_yes | [0.30, 0.70) | 1 | 1 | 1 | 111 | 7 | -46.477 | n/a | n/a |
| C | exploration | Social | short_yes | [0.30, 0.70) | 2 | 2 | 0 | 17 | 4 | 40.588 | 1.522 | 26.66 |
| C | confirmation | Social | short_yes | [0.70, 0.90) | 1 | 1 | 0 | 73 | 4 | 83.096 | n/a | n/a |
| C | exploration | Social | short_yes | [0.70, 0.90) | 2 | 2 | 2 | 25 | 2 | -14.920 | 1.382 | -10.79 |
| C | confirmation | Social | short_yes | [0.90, 1.00] | 2 | 2 | 2 | 310 | 6 | -5.726 | 0.061 | -93.74 |
| C | exploration | Social | short_yes | [0.90, 1.00] | 3 | 3 | 3 | 1062 | 5 | -3.240 | 0.394 | -8.22 |
| C | exploration | Transportation | long_yes | [0.00, 0.10) | 1 | 1 | 1 | 6 | 1 | -7.000 | n/a | n/a |
| C | exploration | Transportation | short_yes | [0.00, 0.10) | 1 | 1 | 0 | 6 | 1 | 9.000 | n/a | n/a |
| C | exploration | Transportation | short_yes | [0.10, 0.30) | 1 | 1 | 0 | 84 | 6 | 14.476 | n/a | n/a |
| C | exploration | Transportation | short_yes | [0.30, 0.70) | 1 | 1 | 0 | 1 | 1 | 50.000 | n/a | n/a |
| C | exploration | Transportation | short_yes | [0.70, 0.90) | 1 | 1 | 0 | 8 | 1 | 74.000 | n/a | n/a |
| C | exploration | World | long_yes | [0.00, 0.10) | 1 | 2 | 1 | 26 | 2 | -2.231 | n/a | n/a |
| C | exploration | World | long_yes | [0.10, 0.30) | 1 | 1 | 1 | 35 | 2 | -15.086 | n/a | n/a |
| C | exploration | World | short_yes | [0.00, 0.10) | 1 | 6 | 0 | 3383 | 29 | 6.170 | n/a | n/a |
