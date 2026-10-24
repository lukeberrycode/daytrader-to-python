"""Characterisation tests: what the legacy DayTrader 8 does today, observed at its boundary.

Each test names the requirement it checks (docs/discovery/requirements.md). Where a test pins down
behaviour that looks wrong, the requirement links to its entry in docs/discovery/keep-or-fix.md.
Quote prices move at random after every trade, so tests read the price immediately before a trade
and check relationships, never fixed prices.
"""

import uuid
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

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


@pytest.mark.req("TRADE-2")
def test_a_holding_records_the_price_before_the_buy(client, new_user):
    price = client.quote(SYMBOL).price
    client.buy(SYMBOL, "2")
    (row,) = client.portfolio().rows
    assert (row.symbol, row.quantity, row.purchase_price) == (SYMBOL, Decimal("2.0"), price)


@pytest.mark.req("TRADE-6")
@pytest.mark.parametrize("quantity", ["-5", "0", "abc", ""])
def test_an_invalid_quantity_is_a_server_error_and_moves_no_money(client, new_user, quantity):
    # Keep-or-fix KF-16: no message on the page, just an HTTP 500.
    before = client.cash_balance()
    with pytest.raises(httpx.HTTPStatusError) as error:
        client.buy(SYMBOL, quantity)
    assert error.value.response.status_code == 500
    assert client.cash_balance() == before
    assert client.holding_ids() == []


@pytest.mark.req("TRADE-6")
@pytest.mark.parametrize("quantity", ["0.1", "2.5", "1e3"])
def test_fractional_and_exponent_quantities_are_accepted(client, new_user, quantity):
    order = client.buy(SYMBOL, quantity)
    assert order.status == "closed"
    assert order.quantity == Decimal(quantity)


@pytest.mark.req("TRADE-7")
@pytest.mark.parametrize("quantity", ["0.1", "0.3", "0.7", "0.15"])
def test_a_fractional_trade_is_rounded_against_the_trader(client, new_user, quantity):
    # Keep-or-fix KF-12: the quantity is a Java double, so 0.1 is really
    # 0.1000000000000000055..., and the database truncates the new balance to 2 places.
    # The trader pays up to a cent more than half-up rounding would charge.
    before = client.cash_balance()
    price = client.quote(SYMBOL).price
    client.buy(SYMBOL, quantity)
    # float() here models the legacy app's Java double on purpose; it is the behaviour under test.
    # CLAUDE.md's no-float rule is for the new slice. A seeded-price test pins this down exactly
    # (test_prices.py).
    exact = Decimal(float(quantity)) * price + ORDER_FEE  # what Java's new BigDecimal(double) does
    assert client.cash_balance() == (before - exact).quantize(CENT, rounding=ROUND_DOWN)


@pytest.mark.req("TRADE-7")
def test_a_fractional_sale_is_truncated_toward_zero_too(client, new_user):
    client.buy(SYMBOL, "0.3")
    (holding_id,) = client.holding_ids()
    before = client.cash_balance()
    price = client.quote(SYMBOL).price
    client.sell(holding_id)
    exact = before + Decimal(float("0.3")) * price - ORDER_FEE  # float() models Java's double
    assert client.cash_balance() == exact.quantize(CENT, rounding=ROUND_DOWN)


@pytest.mark.req("HOME-1")
def test_home_page_values_holdings_at_purchase_cost(client, new_user):
    # Keep-or-fix KF-11: "total of holdings" is the purchase cost, not the market value the
    # glossary describes, so "current gain" only ever reflects fees.
    client.buy(SYMBOL, "2")
    client.buy("s:8", "3")
    summary = client.home_summary()
    basis = sum(row.basis for row in client.portfolio().rows)
    assert summary.holdings == 2
    assert summary.holdings_total == basis
    assert summary.cash_and_holdings == summary.cash + basis
    assert summary.gain == summary.cash_and_holdings - summary.opening_balance
    assert summary.gain == -2 * ORDER_FEE


@pytest.mark.req("HOME-2")
def test_gain_percentages_are_rounded_to_whole_percent(client, new_user):
    # Keep-or-fix KF-10: the ratio is rounded to 2 decimal places before multiplying by 100,
    # so -0.05% shows as +0.00%.
    client.buy(SYMBOL, "1")
    client.buy("s:8", "1")
    summary = client.home_summary()
    ratio = (summary.cash_and_holdings / summary.opening_balance).quantize(CENT, ROUND_HALF_UP)
    assert summary.gain_percent == (ratio - 1) * 100
    assert summary.gain_percent == summary.gain_percent.to_integral_value()


@pytest.mark.req("HOME-3")
def test_a_holding_worth_more_than_two_decimal_places_breaks_the_home_page(client, new_user):
    # Keep-or-fix KF-13: price x quantity is set to 2 places with no rounding mode, which throws.
    # The quantity is a double, so 0.1 has dozens of decimal places and this fails at any price.
    client.buy(SYMBOL, "0.1")
    assert client.status(action="home") == 500
    assert client.status(action="portfolio") == 200


@pytest.mark.req("PORT-1")
def test_portfolio_values_each_holding_at_the_current_price(client, new_user):
    client.buy(SYMBOL, "2")
    client.buy("s:8", "3")
    portfolio = client.portfolio()
    for row in portfolio.rows:
        assert row.current_price == client.quote(row.symbol).price
        assert row.basis == row.quantity * row.purchase_price
        assert row.market_value == row.quantity * row.current_price
        assert row.gain == row.market_value - row.basis
    assert portfolio.total_basis == sum(r.basis for r in portfolio.rows)
    assert portfolio.total_market_value == sum(r.market_value for r in portfolio.rows)
    assert portfolio.total_gain == portfolio.total_market_value - portfolio.total_basis
    ratio = (portfolio.total_market_value / portfolio.total_basis).quantize(CENT, ROUND_HALF_UP)
    assert portfolio.total_gain_percent == (ratio - 1) * 100


@pytest.mark.req("PRICE-1")
def test_a_trade_adds_its_quantity_to_the_volume(client, new_user):
    before = client.quote(SYMBOL).volume
    client.buy(SYMBOL, "3")
    assert client.quote(SYMBOL).volume == before + 3
