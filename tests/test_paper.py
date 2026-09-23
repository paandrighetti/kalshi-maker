"""The forward simulator: queue positions, latency, crossing fills and requotes."""

import pytest

from kmaker.paper import (
    INF,
    MarketInfo,
    Simulator,
    TakerOrder,
    group_taker_orders,
    target_quote,
)
from kmaker.schema import parse_ranges

ONE_CENT = parse_ranges(None)
S = 1_000_000  # one second in microseconds


def info(category="Mentions", expiry=10**12 * S):
    return MarketInfo("M-1-A", "M-1", category, 0.0, ONE_CENT, expiry)


def sim(*pairs):
    """Simulator for (variant, side) pairs qualifying on every bucket of Mentions."""
    q = [
        {"variant": v, "category": "Mentions", "side": s, "bucket": b}
        for v, s in pairs
        for b in range(5)
    ]
    return Simulator(q)


def test_group_taker_orders():
    rows = [
        ("A", "1", 2.0, 0.40, True, 10, False),
        ("A", "2", 3.0, 0.41, True, 10, False),
        ("A", "3", 1.0, 0.39, False, 10, False),
        ("A", "4", 9.0, 0.50, True, 11, True),  # block trade, ignored
    ]
    orders = group_taker_orders(rows)
    assert len(orders) == 2
    buy = next(o for o in orders if o.taker_yes)
    assert buy.levels == [(0.40, 2.0), (0.41, 3.0)] and buy.qty == 5.0


def test_target_quotes():
    book = (0.40, 7.0, 0.45, 9.0)
    assert target_quote("PENNY", "short_yes", book, ONE_CENT) == (0.44, True, 0.0)
    assert target_quote("PENNY", "long_yes", book, ONE_CENT) == (0.41, True, 0.0)
    assert target_quote("JOIN", "short_yes", book, ONE_CENT) == (0.45, False, 9.0)
    assert target_quote("JOIN", "long_yes", book, ONE_CENT) == (0.40, False, 7.0)
    tight = (0.40, 7.0, 0.41, 9.0)  # one-tick spread: PENNY has to join
    assert target_quote("PENNY", "short_yes", tight, ONE_CENT) == (0.41, False, 9.0)
    assert target_quote("PENNY", "long_yes", tight, ONE_CENT) == (0.40, False, 7.0)


def test_penny_ask_filled_first_after_latency():
    s = sim(("PENNY", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), now_us=100 * S, live_delay_us=S)
    (o,) = s.live_orders("M-1-A")
    assert (o.price, o.queue_ahead, o.live_us) == (0.44, 0.0, 101 * S)
    early = TakerOrder("M-1-A", 100 * S + 500_000, True, [(0.45, 4.0)])
    assert s.on_taker_order(early) == []  # printed before the quote was live
    fills = s.on_taker_order(TakerOrder("M-1-A", 102 * S, True, [(0.45, 4.0)]))
    assert [(f.price, f.qty, f.via, f.queue_ahead) for f in fills] == [(0.44, 4.0, "tape", 0.0)]
    fills = s.on_taker_order(TakerOrder("M-1-A", 103 * S, True, [(0.45, 20.0)]))
    assert [f.qty for f in fills] == [6.0]  # the rest of the 10 contracts
    assert o.remaining == 0 and o.cancel_us == 103 * S


def test_prints_below_the_ask_went_to_better_makers():
    s = sim(("JOIN", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    fills = s.on_taker_order(TakerOrder("M-1-A", 102 * S, True, [(0.44, 50.0)]))
    assert fills == []


def test_join_waits_for_the_queue_ahead():
    s = sim(("JOIN", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    (o,) = s.live_orders("M-1-A")
    assert o.queue_ahead == 9.0
    assert s.on_taker_order(TakerOrder("M-1-A", 102 * S, True, [(0.45, 5.0)])) == []
    assert o.queue_ahead == 4.0
    fills = s.on_taker_order(TakerOrder("M-1-A", 103 * S, True, [(0.45, 6.0)]))
    assert [(f.qty, f.queue_ahead) for f in fills] == [(2.0, 4.0)]
    # a sweep through the level fills the rest regardless of what printed at our price
    fills = s.on_taker_order(TakerOrder("M-1-A", 104 * S, True, [(0.46, 30.0)]))
    assert [f.qty for f in fills] == [8.0]


def test_long_yes_side_mirrors():
    s = sim(("JOIN", "long_yes"))
    s.on_book(info(), (0.40, 3.0, 0.45, 9.0), 100 * S, S)
    fills = s.on_taker_order(TakerOrder("M-1-A", 102 * S, False, [(0.40, 5.0), (0.39, 1.0)]))
    assert [(f.side, f.price, f.qty) for f in fills] == [("long_yes", 0.40, 3.0)]
    # taker buying YES never fills a bid
    assert s.on_taker_order(TakerOrder("M-1-A", 103 * S, True, [(0.45, 50.0)])) == []


def test_unchanged_target_keeps_queue_position_and_moved_target_requeues():
    s = sim(("JOIN", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    (o,) = s.live_orders("M-1-A")
    s.on_taker_order(TakerOrder("M-1-A", 102 * S, True, [(0.45, 5.0)]))
    s.on_book(info(), (0.40, 7.0, 0.45, 30.0), 110 * S, S)  # more size joined behind us
    (same,) = s.live_orders("M-1-A")
    assert same is o and same.queue_ahead == 4.0
    s.on_book(info(), (0.40, 7.0, 0.47, 12.0), 120 * S, S)  # the ask moved away
    (new,) = s.live_orders("M-1-A")
    assert new is not o and o.cancel_us == 121 * S  # a cancel waits the same second
    assert (new.price, new.queue_ahead, new.live_us) == (0.47, 12.0, 121 * S)


def test_canceled_quote_still_fills_trades_printed_before_the_cancel():
    s = sim(("PENNY", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    (o,) = s.live_orders("M-1-A")
    s.on_book(info(), (0.40, 7.0, 0.43, 9.0), 110 * S, S)  # someone improved; requote
    assert o.cancel_us == 111 * S
    fills = s.on_taker_order(TakerOrder("M-1-A", 105 * S, True, [(0.45, 3.0)]))
    assert [(f.oid, f.qty) for f in fills] == [(o.oid, 3.0)]
    # during the second after the book the old quote is still there: a taker at 0.44 hits it
    fills = s.on_taker_order(TakerOrder("M-1-A", 110 * S + 500_000, True, [(0.44, 3.0)]))
    assert [(f.oid, f.price, f.qty) for f in fills] == [(o.oid, 0.44, 3.0)]
    fills = s.on_taker_order(TakerOrder("M-1-A", 111 * S, True, [(0.43, 3.0)]))
    assert [(f.price, f.qty) for f in fills] == [(0.42, 3.0)]


def test_stale_quote_crossed_by_the_book_is_picked_off():
    s = sim(("PENNY", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    (o,) = s.live_orders("M-1-A")
    fills = s.on_book(info(), (0.50, 4.0, 0.55, 9.0), 130 * S, S)
    assert [(f.via, f.price, f.qty) for f in fills] == [("cross", 0.44, 4.0)]
    assert o.cancel_us == 131 * S
    (new,) = s.live_orders("M-1-A")
    assert new.price == 0.54


def test_eligibility_by_category_bucket_and_pooled_cells():
    s = Simulator([{"variant": "PENNY", "category": "Mentions", "side": "short_yes", "bucket": 0}])
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)  # target 0.44 is bucket 2
    assert s.live_orders("M-1-A") == []
    s.on_book(info(), (0.02, 7.0, 0.06, 9.0), 110 * S, S)  # target 0.05 is bucket 0
    assert [o.price for o in s.live_orders("M-1-A")] == [0.05]
    s.on_book(info("Politics"), (0.02, 7.0, 0.06, 9.0), 120 * S, S)
    assert s.live_orders("M-1-A") == []
    pooled = Simulator([{"variant": "JOIN", "category": "ALL", "side": "long_yes", "bucket": 2}])
    assert pooled.eligible("JOIN", "Politics", "long_yes", 0.5)
    assert not pooled.eligible("JOIN", "Politics", "short_yes", 0.5)


def test_one_sided_book_or_expiry_cancels_quotes():
    s = sim(("PENNY", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    s.on_book(info(), None, 110 * S, S)
    assert s.live_orders("M-1-A") == []
    s.on_book(info(expiry=150 * S), (0.40, 7.0, 0.45, 9.0), 160 * S, S)
    assert s.live_orders("M-1-A") == []


def test_prune_keeps_recent_cancels():
    s = sim(("PENNY", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    s.cancel_all("M-1-A", 110 * S)
    s.prune(105 * S)
    assert "M-1-A" in s.orders
    s.prune(111 * S)
    assert "M-1-A" not in s.orders


def test_variants_are_independent_worlds():
    s = sim(("PENNY", "short_yes"), ("JOIN", "short_yes"))
    s.on_book(info(), (0.40, 7.0, 0.45, 9.0), 100 * S, S)
    fills = s.on_taker_order(TakerOrder("M-1-A", 102 * S, True, [(0.45, 12.0)]))
    got = sorted((f.variant, f.price, f.qty) for f in fills)
    # PENNY at 0.44 takes 10; JOIN at 0.45 behind 9 gets the 3 that reach past its queue
    assert got == [("JOIN", 0.45, 3.0), ("PENNY", 0.44, 10.0)]


@pytest.mark.parametrize("side,taker_yes", [("short_yes", True), ("long_yes", False)])
def test_no_fill_after_cancel(side, taker_yes):
    s = sim(("JOIN", side))
    s.on_book(info(), (0.40, 0.0001, 0.45, 0.0001), 100 * S, S)
    s.cancel_all("M-1-A", 105 * S)
    level = 0.45 if taker_yes else 0.40
    assert s.on_taker_order(TakerOrder("M-1-A", 106 * S, taker_yes, [(level, 5.0)])) == []
    assert all(o.cancel_us != INF for o in s.orders["M-1-A"])
