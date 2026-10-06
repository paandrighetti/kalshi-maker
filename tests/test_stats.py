import numpy as np
import pandas as pd

from kmaker.stats import cluster_table, decide, leave_one_out, passes, wild_cluster_p


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


def test_wild_cluster_p_orders_evidence_and_is_reproducible():
    w = np.full(30, 10.0)
    strong = np.r_[np.full(27, 1.0), np.full(3, -1.0)]  # 27 of 30 clusters positive
    mixed = np.r_[np.full(15, 1.0), np.full(15, -1.0)] + np.linspace(0, 0.1, 30)
    p_strong = wild_cluster_p(strong, w, draws=9_999, seed=1)
    p_mixed = wild_cluster_p(mixed, w, draws=9_999, seed=1)
    assert p_strong < 0.001 < 0.1 < p_mixed < 0.9
    assert wild_cluster_p(strong, w, draws=9_999, seed=1) == p_strong
    # the p of a draw count B is a multiple of 1 / (B + 1)
    assert np.isclose(p_mixed * 10_000, round(p_mixed * 10_000))


def test_wild_cluster_p_on_the_day_12_join_clusters():
    # JOIN in the report of 6 October 2026 (cluster sums in USD and contracts, rounded): the value
    # Amendment 5 quotes; residuals not restricted to the null would give another p
    s = [
        7.2485,
        148.2063,
        149.8769,
        174.5114,
        -63.2282,
        -51.9986,
        -50.9017,
        78.8067,
        65.368,
        84.5604,
        -100.9904,
        18.2368,
        -63.4541,
        -5.9,
        8.9974,
        31.3993,
        23.8656,
        6.5,
        11.012,
        21.688,
        89.4452,
    ]
    w = [
        490.57,
        4487.98,
        4260.57,
        4052.27,
        4107.37,
        4356.15,
        4526.35,
        4736.49,
        4145.22,
        3910.36,
        3929.99,
        3743.9,
        165.85,
        20.0,
        1177.17,
        284.27,
        301.21,
        50.0,
        84.84,
        185.32,
        715.6,
    ]
    assert wild_cluster_p(s, w, draws=99_999, seed=20261006) == 0.05485


def test_wild_cluster_p_matches_full_enumeration():
    # six clusters: all 6^6 weight vectors are equally likely, so the exact p is a count
    import itertools

    from kmaker.stats import WEBB, _ratio_t

    s = np.array([3.0, -1.0, 2.0, 0.5, -0.5, 1.5])
    w = np.array([10.0, 12.0, 8.0, 9.0, 11.0, 10.0])
    t0 = float(_ratio_t(s, w))
    v = np.array(list(itertools.product(WEBB, repeat=6)))
    exact = float(np.mean(_ratio_t(v * s, w) >= t0))
    assert abs(wild_cluster_p(s, w, draws=99_999, seed=3) - exact) < 0.005


def test_wild_cluster_p_is_none_without_a_t():
    assert wild_cluster_p([1.0], [1.0], draws=99, seed=1) is None
    assert wild_cluster_p([1.0, 1.0], [1.0, 1.0], draws=99, seed=1) is None
    assert wild_cluster_p([0.0, 0.0, 0.0], [1.0, 1.0, 1.0], draws=99, seed=1) is None


def test_leave_one_out_by_hand():
    # cluster sums (2, 4), (-1, 2), (3, 6): without each, 2 / 8, 5 / 10 and 1 / 6 per contract
    lo, hi = leave_one_out([2.0, -1.0, 3.0], [4.0, 2.0, 6.0])
    assert np.isclose(lo, 100 / 6) and np.isclose(hi, 50.0)
    assert leave_one_out([1.0], [1.0]) is None


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
