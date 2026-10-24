"""Price rules the shipped data never reaches, tested on the "fixtures" image.

legacy/docker/fixtures.sql seeds s:998 at 0.01 and s:999 at 400.01 before the app starts.
Each test's trade changes the seeded price, so each rule can be tested once per container.
"""

from decimal import Decimal

import pytest


@pytest.mark.req("PRICE-2")
def test_a_penny_stock_is_multiplied_by_600_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register("ct-penny", "pw", "100000")
    assert c.quote("s:998").price == Decimal("0.01")
    c.buy("s:998", "1")
    assert c.quote("s:998").price == Decimal("6.00")


@pytest.mark.req("PRICE-3")
def test_a_stock_above_400_is_halved_on_the_next_trade(fixtures_client):
    c = fixtures_client
    c.register("ct-split", "pw", "100000")
    assert c.quote("s:999").price == Decimal("400.01")
    c.buy("s:999", "1")
    assert c.quote("s:999").price == Decimal("200.01")
