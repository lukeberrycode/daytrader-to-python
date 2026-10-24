"""Characterisation tests for quotes and the market summary (states T4, T10)."""

import time
from decimal import ROUND_HALF_UP, Decimal

import pytest

CENT = Decimal("0.01")
ALL_SYMBOLS = [f"s:{i}" for i in range(1000)]


@pytest.mark.req("QUOTE-2")
def test_the_quotes_api_returns_null_for_an_unknown_symbol(client):
    quotes = client.quotes(["s:1", "no-such-symbol", "s:2"])  # POST
    assert [q.symbol if q else None for q in quotes] == ["s:1", None, "s:2"]
    by_get = client.raw_quotes_get("s:1,no-such-symbol,s:2")
    assert [q["symbol"] if q else None for q in by_get] == ["s:1", None, "s:2"]


@pytest.mark.req("QUOTE-3")
def test_the_quotes_page_shows_each_symbol_with_its_price(client, new_user):
    page = client.quotes_page("s:1,s:2")
    for q in client.quotes(["s:1", "s:2"]):
        # symbol, company, volume, low - high, open, $ current price, change (gain %)
        company = f"S{q.symbol[2:]} Incorporated"
        row = f"{q.symbol} {company} {q.volume:.1f} {q.low} - {q.high} {q.open} $ {q.price} "
        assert row in page
        assert f"$ {q.price} {q.change} (" in page


@pytest.mark.req("QUOTE-4")
def test_low_and_high_never_move_from_the_opening_price(client, new_user):
    # Keep-or-fix KF-14: trades change the price but never the low or high, so the
    # "price range" is always the opening price, contrary to the glossary.
    for _ in range(3):  # a trade can leave the price unchanged (a factor of 1.00)
        client.buy("s:40", "1")
    moved = [q for q in client.quotes(ALL_SYMBOLS) if q and q.price != q.open]
    assert moved, "no stock has moved since opening"
    assert all(q.low == q.open == q.high for q in moved)


@pytest.mark.req("MARKET-1")
def test_the_market_index_is_the_mean_price_of_every_stock(client):
    # Keep-or-fix KF-15: the glossary says TSIA is an index of the top 20 stocks.
    # The summary is recalculated at most every 20 seconds, so wait for it to catch up.
    deadline = time.monotonic() + 30
    while True:
        prices = [q.price for q in client.quotes(ALL_SYMBOLS) if q]
        mean = (sum(prices) / len(prices)).quantize(CENT, rounding=ROUND_HALF_UP)
        summary = client.market_summary()
        if summary["tsia"] == mean or time.monotonic() > deadline:
            break
        time.sleep(3)
    assert summary["tsia"] == mean


@pytest.mark.req("MARKET-2")
def test_top_gainers_and_losers_are_ranked_by_change_in_price(client):
    summary = client.market_summary()
    gainers = [summary[f"gainer{i}_change"] for i in range(1, 6)]
    losers = [summary[f"loser{i}_change"] for i in range(1, 6)]
    assert gainers == sorted(gainers, reverse=True)
    assert losers == sorted(losers)
    assert min(gainers) >= max(losers)
    assert all(summary[f"gainer{i}_price"].startswith("$") for i in range(1, 6))
