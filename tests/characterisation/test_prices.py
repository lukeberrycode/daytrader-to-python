"""Price rules the shipped data never reaches, tested on the "fixtures" image.

legacy/docker/fixtures.sql seeds s:997 at 10.00, s:998 at 0.01 and s:999 at 400.01 before the app
starts.
Each test's trade changes the seeded price, so each rule can be tested once per container.
"""

import uuid
from decimal import Decimal

import pytest


def _user_id() -> str:
    return f"ct-{uuid.uuid4().hex[:12]}"


@pytest.mark.req("PRICE-2")
def test_a_penny_stock_is_multiplied_by_600_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "100000")
    assert c.quote("s:998").price == Decimal("0.01")
    c.buy("s:998", "1")
    assert c.quote("s:998").price == Decimal("6.00")


@pytest.mark.req("PRICE-3")
def test_a_stock_above_400_is_halved_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register(_user_id(), "pw", "100000")
    assert c.quote("s:999").price == Decimal("400.01")
    c.buy("s:999", "1")
    assert c.quote("s:999").price == Decimal("200.01")


@pytest.mark.req("TRADE-7")
def test_buying_a_tenth_of_a_share_at_10_00_costs_a_cent_extra(fixtures_client):
    # Exact decimals give 0.1 x 10.00 + 24.95 = 25.95, and so does half-up rounding. The app
    # charges 25.96: its 0.1 is a double (0.1000000000000000055...), so the cost is a hair over
    # 25.95, and the database truncates the new balance down to the cent below.
    c = fixtures_client
    c.register(_user_id(), "pw", "1000.00")
    assert c.quote("s:997").price == Decimal("10.00")
    c.buy("s:997", "0.1")
    assert c.cash_balance() == Decimal("974.04")
