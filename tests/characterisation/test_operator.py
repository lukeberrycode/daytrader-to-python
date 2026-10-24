"""Characterisation tests for the operator's features (states O1–O3) and the scenario servlet."""

import uuid

import httpx
import pytest

from .legacy_client import LegacyClient

DEFAULTS = {
    "EnableLongRun": "on",
    "DisplayOrderAlerts": "on",
    "EnablePublishQuotePriceChange": "on",
}


@pytest.fixture
def restore_config(client):
    fields, switches = client.config_fields(), client.config_switches()
    assert all(switches.values()), "the defaults have every switch on"
    yield
    client.admin(action="updateConfig", MaxQuotes=fields["MaxQuotes"], **DEFAULTS)
    assert client.config_fields() == fields
    assert client.config_switches() == switches


@pytest.mark.req("ADMIN-3")
def test_a_config_update_turns_off_every_setting_it_omits(client, restore_config):
    # Keep-or-fix KF-17: the form's checkboxes are read as "off" when absent, so changing one
    # setting from a script turns off long run, order alerts and the price streamer. With both
    # long run and alerts off, a new order is counted on the account page.
    client.admin(action="updateConfig", MaxQuotes=client.config_fields()["MaxQuotes"])
    assert client.config_switches() == {
        "EnablePublishQuotePriceChange": False,
        "DisplayOrderAlerts": False,
        "EnableLongRun": False,
    }
    user = LegacyClient()
    try:
        user.register(f"ct-{uuid.uuid4().hex[:12]}", "pw", "1000")
        user.buy("s:7", "1")
        user.account_page()
        assert user.total_orders() == 1
    finally:
        user.close()


@pytest.mark.req("ADMIN-2")
def test_reset_removes_ru_users_and_zeroes_seeded_login_counts(client):
    # The deleted user's orders and holdings can't be seen through the boundary once the user is
    # gone; that part of ADMIN-2 is from the code (TradeDirectDBUtils.resetTrade).
    removed = f"ru:{uuid.uuid4().hex[:8]}"
    kept = f"ct-{uuid.uuid4().hex[:12]}"
    for user_id in (removed, kept):
        other = LegacyClient()
        assert f"Welcome {user_id}," in other.register(user_id, "pw", "1000")
        other.close()
    client.login("uid:3", "xxx")
    assert client.login_counts()[0] >= 1
    client.logout()
    client.admin(action="resetTrade")
    with pytest.raises(httpx.HTTPStatusError):
        client.login(removed, "pw")
    assert f"Welcome {kept}," in client.login(kept, "pw")
    client.logout()
    client.login("uid:3", "xxx")
    assert client.login_counts() == (1, 0)


@pytest.mark.req("SCEN-1")
def test_the_scenario_servlet_fails_for_users_missing_from_the_database(client):
    # Keep-or-fix KF-9: the servlet picks users up to MAX_USERS (1000, from the image) but the
    # database has uid:0 to uid:499, so a large share of requests are HTTP 500. Each request has
    # no session, so each logs in as a new random user; about 4 in 10 fail.
    assert client.config_fields()["MaxUsers"] == "1000"
    client.login("uid:499", "xxx")
    client.logout()
    with pytest.raises(httpx.HTTPStatusError):
        client.login("uid:500", "xxx")  # the first user the database doesn't have
    statuses = [client.scenario() for _ in range(40)]
    assert 200 in statuses
    assert 500 in statuses


@pytest.mark.req("ORDER-1")
def test_the_order_alert_deletes_the_order_rather_than_hiding_it(client, restore_config):
    # Long run also turns off the account page's "show all orders" query, so "Total Orders: 0"
    # alone could mean hidden, not deleted. Separate the two: let the alert fire with long run on,
    # then turn long run off (alerts still on). The first order stays missing; a new one counts.
    user = LegacyClient()
    try:
        user.register(f"ct-{uuid.uuid4().hex[:12]}", "pw", "1000")
        user.buy("s:7", "1")
        assert "The following Order(s) have completed" in user.account_page()
        max_quotes = client.config_fields()["MaxQuotes"]
        client.admin(
            action="updateConfig",
            MaxQuotes=max_quotes,
            DisplayOrderAlerts="on",
            EnablePublishQuotePriceChange="on",
        )
        assert client.config_switches()["EnableLongRun"] is False
        assert user.total_orders() == 0  # deleted, not hidden
        user.buy("s:7", "1")
        user.account_page()
        assert user.total_orders() == 1  # the query works with long run off
    finally:
        user.close()
