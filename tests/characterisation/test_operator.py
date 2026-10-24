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
    yield
    client.admin(action="updateConfig", **DEFAULTS)


@pytest.mark.req("ADMIN-3")
def test_a_config_update_turns_off_every_setting_it_omits(client, restore_config):
    # Keep-or-fix KF-17: the form's checkboxes are read as "off" when absent, so changing one
    # setting from a script turns off long run, order alerts and the price streamer. With long
    # run off, completed orders are kept (compare ORDER-1).
    client.admin(action="updateConfig", MaxQuotes="1000")
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
    removed = f"ru:{uuid.uuid4().hex[:8]}"
    kept = f"ct-{uuid.uuid4().hex[:12]}"
    for user_id in (removed, kept):
        other = LegacyClient()
        other.register(user_id, "pw", "1000")
        other.close()
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
    # database has uid:0 to uid:499, so a large share of requests are HTTP 500.
    statuses = [client.scenario() for _ in range(40)]
    assert 200 in statuses
    assert 500 in statuses
