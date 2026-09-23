from kmaker.schema import (
    bucket_label,
    bucket_of,
    maker_fee,
    maker_fee_rate,
    normalize_market,
    normalize_trade,
    parse_ranges,
    series_of,
    tick_at,
    top_of_book,
    ts_us,
)

EDGES = (0.0, 0.10, 0.30, 0.70, 0.90)


def test_trade_new_fields_and_direction():
    t = {
        "count_fp": "12.75",
        "created_time": "2026-09-21T23:24:25.627326Z",
        "is_block_trade": False,
        "no_price_dollars": "0.5600",
        "taker_book_side": "bid",
        "taker_outcome_side": "yes",
        "taker_side": "yes",
        "ticker": "KXATP-26SEP21VILJUS-VIL",
        "trade_id": "abc",
        "yes_price_dollars": "0.4400",
    }
    row = normalize_trade(t)
    assert row == ("KXATP-26SEP21VILJUS-VIL", "abc", 12.75, 0.44, True, row[5], False)
    assert row[5] == ts_us("2026-09-21T23:24:25.627326Z")
    assert row[5] % 1_000_000 == 627326


def test_trade_legacy_fields():
    t = {
        "ticker": "X-1",
        "trade_id": "t",
        "count": 3,
        "yes_price": 7,
        "taker_side": "no",
        "created_time": "2025-12-01T00:00:01Z",
    }
    assert normalize_trade(t) == (
        "X-1",
        "t",
        3.0,
        0.07,
        False,
        ts_us("2025-12-01T00:00:01Z"),
        False,
    )


def test_trade_rejects_unknown_side():
    assert normalize_trade({"ticker": "X", "taker_outcome_side": "", "count_fp": "1"}) is None


def test_ts_us_without_fraction():
    assert ts_us("1970-01-01T00:00:01Z") == 1_000_000
    assert ts_us(None) is None


def test_series_of():
    assert series_of("KXBTC15M-26SEP211930-30") == "KXBTC15M"
    assert series_of("KXHIGHNY") == "KXHIGHNY"


def test_market_normalization_and_mve():
    m = {
        "ticker": "KXA-1-B",
        "event_ticker": "KXA-1",
        "status": "finalized",
        "result": "Yes",
        "close_time": "2026-01-01T00:00:00Z",
        "settlement_ts": "2026-01-01T01:00:00Z",
        "price_ranges": [{"start": "0", "end": "1", "step": "0.01"}],
    }
    n = normalize_market(m)
    assert n["series"] == "KXA" and n["result"] == "yes" and not n["mve"]
    assert n["settlement_us"] - n["close_us"] == 3600 * 1_000_000
    assert normalize_market({"ticker": "KXMVEX-1-A", "event_ticker": "KXMVEX-1"})["mve"]
    assert normalize_market({"ticker": "Q-1", "mve_collection_ticker": "C"})["mve"]


def test_ticks_on_tapered_grid():
    r = parse_ranges(
        '[{"start":"0","end":"0.1","step":"0.001"},{"start":"0.1","end":"0.9","step":"0.01"},'
        '{"start":"0.9","end":"1","step":"0.001"}]'
    )
    assert tick_at(r, 0.05) == 0.001
    assert tick_at(r, 0.10) == 0.01
    assert tick_at(r, 0.95) == 0.001
    assert tick_at(r, 1.0) == 0.001
    assert tick_at(parse_ranges(None), 0.5) == 0.01


def test_top_of_book_requires_two_sides():
    m = {
        "yes_bid_dollars": "0.40",
        "yes_bid_size_fp": "10",
        "yes_ask_dollars": "0.43",
        "yes_ask_size_fp": "5",
    }
    assert top_of_book(m) == (0.40, 10.0, 0.43, 5.0)
    assert top_of_book({**m, "yes_bid_dollars": "0.0000"}) is None
    assert top_of_book({**m, "yes_ask_dollars": "1.0000"}) is None
    assert top_of_book({**m, "yes_ask_size_fp": "0"}) is None


def test_maker_fee_rounds_up_to_the_cent():
    # 0.0175 x 10 x 0.5 x 0.5 = 0.04375 -> 0.05
    assert maker_fee(0.0175, 10, 0.5) == 0.05
    # 0.0175 x 100 x 0.99 x 0.01 = 0.017325 -> 0.02
    assert maker_fee(0.0175, 100, 0.99) == 0.02
    assert maker_fee(0.0, 10, 0.5) == 0.0
    assert maker_fee_rate("quadratic_with_maker_fees", 1, 0.0175) == 0.0175
    assert maker_fee_rate("quadratic_with_maker_fees", 0.5, 0.0175) == 0.00875
    assert maker_fee_rate("quadratic", 1, 0.0175) == 0.0


def test_buckets():
    assert [bucket_of(p, EDGES) for p in (0.01, 0.0999, 0.10, 0.5, 0.8999, 0.9, 0.99)] == [
        0,
        0,
        1,
        2,
        3,
        4,
        4,
    ]
    assert bucket_label(0, EDGES) == "[0.00, 0.10)"
    assert bucket_label(4, EDGES) == "[0.90, 1.00]"
