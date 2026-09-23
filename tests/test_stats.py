import numpy as np
import pandas as pd

from kmaker.stats import cluster_table, decide, passes


def test_cluster_table_matches_hand_computation():
    # clusters c1 (two rows, two events), c2, c3 with sums (2, 4), (-1, 2), (3, 6)
    df = pd.DataFrame(
        {
            "k": ["a"] * 4,
            "cluster": ["c1", "c1", "c2", "c3"],
            "event": ["e1", "e2", "e3", "e3"],
            "s": [1.0, 1.0, -1.0, 3.0],
            "w": [2.0, 2.0, 2.0, 6.0],
            "n": [1, 1, 1, 1],
        }
    )
    t = cluster_table(df, ["k"]).iloc[0]
    S = np.array([2.0, -1.0, 3.0])
    W = np.array([4.0, 2.0, 6.0])
    m = S.sum() / W.sum()
    var = 3 / 2 * ((S - m * W) ** 2).sum() / W.sum() ** 2
    assert t["clusters"] == 3 and t["events"] == 3 and t["losing"] == 1
    assert t["contracts"] == 12 and t["rows"] == 4
    assert np.isclose(t["mean_c"], 100 * m)
    assert np.isclose(t["se_c"], 100 * np.sqrt(var))
    assert np.isclose(t["t"], m / np.sqrt(var))


def test_degenerate_variance_has_no_t():
    one = pd.DataFrame(
        {"k": ["a"], "cluster": ["c"], "event": ["e"], "s": [1.0], "w": [1.0], "n": [1]}
    )
    assert np.isnan(cluster_table(one, ["k"]).iloc[0]["t"])
    # identical cluster means: zero residual variance must not produce an infinite t
    same = pd.DataFrame(
        {
            "k": ["a", "a"],
            "cluster": ["c1", "c2"],
            "event": ["e1", "e2"],
            "s": [1.0, 1.0],
            "w": [1.0, 1.0],
            "n": [1, 1],
        }
    )
    assert np.isnan(cluster_table(same, ["k"]).iloc[0]["t"])


def _cell(stat, sample, mean=1.0, t=3.0, **kw):
    base = {
        "stat": stat,
        "sample": sample,
        "category": "Mentions",
        "side": "short_yes",
        "bucket": 0,
        "clusters": 40,
        "events": 150,
        "losing": 12,
        "contracts": 1000.0,
        "rows": 10,
        "mean_c": mean,
        "se_c": 1.0,
        "t": t,
    }
    return {**base, **kw}


def test_passes_floors():
    assert passes(pd.Series(_cell("B", "exploration")))
    for field, value in (
        ("clusters", 29),
        ("events", 99),
        ("losing", 9),
        ("contracts", 499.0),
        ("mean_c", -0.1),
        ("t", 1.99),
        ("t", float("nan")),
    ):
        assert not passes(pd.Series(_cell("B", "exploration", **{field: value}))), field


def test_decide_requires_both_samples():
    cells = pd.DataFrame(
        [
            _cell("B", "exploration", t=2.5),
            _cell("B", "confirmation", t=2.1),
            _cell("C", "exploration", t=2.5),
            _cell("C", "confirmation", t=1.9),
            _cell("B", "all", t=9.0, category="Politics"),  # pooled sample never decides
        ]
    )
    q, tested = decide(cells)
    assert tested == 2
    assert [(x["variant"], x["category"]) for x in q] == [("PENNY", "Mentions")]


def test_decide_missing_sample_does_not_qualify():
    q, tested = decide(pd.DataFrame([_cell("B", "exploration")]))
    assert q == [] and tested == 1
