"""Characterisation tests: what the legacy DayTrader 8 does today, observed at its boundary.

Each test names the requirement it checks (docs/discovery/requirements.md). Where a test pins down
behaviour that looks wrong, the requirement links to its entry in docs/discovery/keep-or-fix.md.
Quote prices move at random after every trade, so tests read the price immediately before a trade
and check relationships, never fixed prices.
"""

import uuid
from decimal import Decimal

import httpx
import pytest

from .conftest import OPENING_BALANCE, PASSWORD

ORDER_FEE = Decimal("24.95")
CENT = Decimal("0.01")
SYMBOL = "s:7"


@pytest.mark.req("AUTH-1")
def test_registration_logs_the_new_user_in_with_the_opening_balance(client, new_user):
    assert client.cash_balance() == Decimal(OPENING_BALANCE)
    assert client.opening_balance() == Decimal(OPENING_BALANCE)


@pytest.mark.req("AUTH-2")
def test_registration_fails_when_the_passwords_differ(client):
    page = client.register(f"ct-{uuid.uuid4().hex[:12]}", "one", "1000", confirm="two")
    assert "passwords did not match" in page


@pytest.mark.req("AUTH-3")
def test_a_wrong_password_is_a_server_error(client, new_user):
    # Keep-or-fix KF-3: a failed login is an HTTP 500, not a message on the login page, and the
    # server log records both the password tried and the stored password (checked by hand; see
    # docs/discovery/agent-errors.md).
    client.logout()
    with pytest.raises(httpx.HTTPStatusError) as error:
        client.login(new_user, "wrong-password")
    assert error.value.response.status_code == 500


@pytest.mark.req("AUTH-4")
def test_registration_accepts_a_negative_opening_balance(client):
    # Keep-or-fix KF-2: no validation of the opening balance.
    client.register(f"ct-{uuid.uuid4().hex[:12]}", PASSWORD, "-500.00")
    assert client.cash_balance() == Decimal("-500.00")


@pytest.mark.req("QUOTE-1")
def test_quotes_api_returns_prices_with_two_decimal_places(client):
    quote = client.quote(SYMBOL)
    assert quote.symbol == SYMBOL
    assert quote.price == quote.price.quantize(CENT)
    # Keep-or-fix KF-4: money goes out as JSON numbers such as 52.00, not strings.
    assert '"price":' in client.raw_quotes_json(SYMBOL)


@pytest.mark.req("TRADE-1")
def test_buy_debits_quantity_times_price_plus_the_fee(client, new_user):
    before = client.cash_balance()
    price = client.quote(SYMBOL).price
    order = client.buy(SYMBOL, "3")
    assert (order.status, order.order_type, order.fee) == ("closed", "buy", ORDER_FEE)
    assert client.cash_balance() == before - (3 * price + ORDER_FEE)


@pytest.mark.req("TRADE-2")
def test_buy_creates_one_holding(client, new_user):
    client.buy(SYMBOL, "2")
    assert len(client.holding_ids()) == 1


@pytest.mark.req("TRADE-3")
def test_buy_is_allowed_beyond_the_cash_balance(client, new_user):
    # Keep-or-fix KF-1: no balance check, so the cash balance goes negative.
    price = client.quote(SYMBOL).price
    quantity = int(Decimal(OPENING_BALANCE) / price) + 100
    order = client.buy(SYMBOL, str(quantity))
    assert order.status == "closed"
    assert client.cash_balance() < 0


@pytest.mark.req("TRADE-4")
def test_sell_credits_quantity_times_price_minus_the_fee(client, new_user):
    client.buy(SYMBOL, "4")
    (holding_id,) = client.holding_ids()
    before = client.cash_balance()
    price = client.quote(SYMBOL).price
    order = client.sell(holding_id)
    assert (order.status, order.order_type) == ("closed", "sell")
    assert client.cash_balance() == before + (4 * price - ORDER_FEE)
    assert client.holding_ids() == []


@pytest.mark.req("TRADE-5")
def test_selling_a_holding_twice_fails_without_crediting_twice(client, new_user):
    # Keep-or-fix KF-5: the code tries to record a "cancelled" order, but that order fails bean
    # validation, so the user sees an HTTP 500. The transaction rolls back, so no money moves.
    client.buy(SYMBOL, "1")
    (holding_id,) = client.holding_ids()
    client.sell(holding_id)
    after_first_sale = client.cash_balance()
    with pytest.raises(httpx.HTTPStatusError) as error:
        client.sell(holding_id)
    assert error.value.response.status_code == 500
    assert client.cash_balance() == after_first_sale


@pytest.mark.req("PRICE-1")
def test_a_trade_moves_the_price_by_at_most_ten_percent(client, new_user):
    before = client.quote(SYMBOL).price
    client.buy(SYMBOL, "1")
    after = client.quote(SYMBOL).price
    # Penny stocks and prices over 400 follow other rules (PRICE-2, PRICE-3); s:7 is neither today.
    assume_normal = Decimal("0.01") < before <= Decimal("400")
    if not assume_normal:
        pytest.skip(f"{SYMBOL} is at {before}, outside the normal price range")
    assert after == after.quantize(CENT)
    factor_low = (before * Decimal("0.90")).quantize(CENT)
    factor_high = (before * Decimal("1.10")).quantize(CENT)
    assert factor_low <= after <= factor_high


@pytest.mark.req("ADMIN-1")
def test_the_admin_page_needs_no_login(client):
    # Keep-or-fix KF-6: web.xml declares security constraints, but the server enables no
    # application security, so /config (reset, rebuild the database) is open to anyone.
    page = client.admin_page()
    assert "Configuration" in page


@pytest.mark.req("ORDER-1")
def test_a_completed_order_is_shown_once_as_an_alert_then_deleted(client, new_user):
    # Keep-or-fix KF-7: with the default "long run" setting, showing the completed-order alert
    # deletes the order, so the account's order history is always empty.
    order = client.buy(SYMBOL, "1")
    first = client.account_page()
    assert "The following Order(s) have completed" in first
    assert str(order.order_id) in first
    assert client.total_orders() == 0
    assert "The following Order(s) have completed" not in client.account_page()
