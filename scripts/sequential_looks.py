"""False successes of the forward rule when the edge is zero (Amendment 4).

Daily results are independent standard normal draws, and t on day n is their cumulative sum
divided by the square root of n. Prints the share of 200,000 paths that reach the threshold
under each schedule of looks; seed 7 gives the figures quoted in PREREGISTRATION.md.
"""

import numpy as np

rng = np.random.default_rng(7)
t = np.cumsum(rng.standard_normal((200_000, 180), dtype=np.float32), axis=1)
t /= np.sqrt(np.arange(1, 181))


def share(days: list[int], threshold: float) -> float:
    return float((t[:, [d - 1 for d in days]] >= threshold).any(axis=1).mean())


print(f"one look on day 60, t >= 2:               {share([60], 2.0):.3f}")
print(f"every day from day 20 to 60, t >= 2:      {share(list(range(20, 61)), 2.0):.3f}")
print(f"every day from day 20 to 180, t >= 2:     {share(list(range(20, 181)), 2.0):.3f}")
print(f"days 20 and 60, t >= 2.28 (Amendment 4):  {share([20, 60], 2.28):.3f}")
