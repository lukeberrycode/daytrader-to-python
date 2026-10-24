"""Price rules the shipped data never reaches, tested on the "fixtures" image.

legacy/docker/fixtures.sql seeds a few prices before the app starts (s:994 to s:999).
Each test's trade changes the seeded price, so each rule can be tested once per container.
"""

import os
import uuid
from decimal import Decimal

import pytest


def _user_id() -> str:
    return f"ct-{uuid.uuid4().hex[:12]}"


def _seeded(c, symbol: str, price: str) -> None:
    """Skip on a fixtures container whose seeded price has been traded. In CI (FIXTURES_STRICT),
    the container is always fresh, so a wrong price means the seeding failed: fail instead."""
    actual = c.quote(symbol).price
    if actual != Decimal(price):
        message = f"{symbol} is at {actual}, not its seeded {price}"
        if os.environ.get("FIXTURES_STRICT"):
            pytest.fail(f"{message}: the fixtures image wasn't seeded")
        pytest.skip(f"{message}: start a fresh fixtures container")


@pytest.mark.req("PRICE-2")
def test_a_penny_stock_is_multiplied_by_600_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "100000")
    _seeded(c, "s:998", "0.01")
    c.buy("s:998", "1")
    assert c.quote("s:998").price == Decimal("6.00")


@pytest.mark.req("PRICE-3")
def test_a_stock_above_400_is_halved_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "100000")
    _seeded(c, "s:999", "400.01")
    c.buy("s:999", "1")
    assert c.quote("s:999").price == Decimal("200.01")


@pytest.mark.req("TRADE-7")
def test_buying_a_tenth_of_a_share_at_10_00_costs_a_cent_extra(fixtures_client):
    # Exact decimals give 0.1 x 10.00 + 24.95 = 25.95, and so does half-up rounding. The app
    # charges 25.96: its 0.1 is a double (0.1000000000000000055...), so the cost is a hair over
    # 25.95, and the database truncates the new balance down to the cent below.
    c = fixtures_client
    c.register(_user_id(), "pw", "1000.00")
    _seeded(c, "s:997", "10.00")
    c.buy("s:997", "0.1")
    assert c.cash_balance() == Decimal("974.04")


@pytest.mark.req("TRADE-7")
def test_with_a_negative_balance_the_same_trade_costs_the_exact_amount(fixtures_client):
    # The balance is truncated toward zero, so below zero the rounding favours the trader.
    c = fixtures_client
    c.register(_user_id(), "pw", "-500.00")
    _seeded(c, "s:994", "10.00")
    c.buy("s:994", "0.1")
    assert c.cash_balance() == Decimal("-525.95")


@pytest.mark.req("HOME-3")
def test_home_page_works_for_2_5_shares_at_an_even_number_of_cents(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "1000.00")
    _seeded(c, "s:995", "10.00")
    c.buy("s:995", "2.5")  # 25.000: two decimal places are enough
    assert c.status(action="home") == 200


@pytest.mark.req("HOME-3")
def test_home_page_breaks_for_2_5_shares_at_an_odd_number_of_cents(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "1000.00")
    _seeded(c, "s:996", "10.01")
    c.buy("s:996", "2.5")  # 25.025: three decimal places
    assert c.status(action="home") == 500
