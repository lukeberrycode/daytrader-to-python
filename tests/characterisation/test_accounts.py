"""Characterisation tests for accounts, login and profiles (states T1–T3, T8, T9)."""

import uuid

import httpx
import pytest

from .conftest import PASSWORD
from .legacy_client import LegacyClient


def _user_id() -> str:
    return f"ct-{uuid.uuid4().hex[:12]}"


@pytest.mark.req("AUTH-2")
def test_registration_fails_when_the_password_is_empty(client):
    page = client.register(_user_id(), "", "1000")
    assert "passwords did not match" in page


@pytest.mark.req("AUTH-5")
def test_registering_an_existing_user_id_fails(client, new_user):
    client.logout()
    page = client.register(new_user, PASSWORD, "1000")
    assert "Registration operation failed" in page


@pytest.mark.req("AUTH-6")
def test_login_and_logout_are_counted(client, new_user):
    assert client.login_counts() == (1, 0)  # registration logs the user in
    client.logout()
    client.login(new_user, PASSWORD)
    assert client.login_counts() == (2, 1)


@pytest.mark.req("AUTH-7")
def test_pages_after_login_need_a_session(client):
    page = client.home()
    assert "User Not Logged in" in page


@pytest.mark.req("AUTH-9")
def test_an_unknown_user_id_is_a_server_error(client):
    # Keep-or-fix KF-3: like a wrong password, an unknown user is an HTTP 500.
    with pytest.raises(httpx.HTTPStatusError) as error:
        client.login(_user_id(), PASSWORD)
    assert error.value.response.status_code == 500


@pytest.mark.req("AUTH-8")
def test_profile_update_changes_the_profile_and_the_password(client, new_user):
    client.update_profile("new-secret", "new-secret", "Changed Name", "changed@example.com")
    fields = client.profile_fields()
    assert fields["fullname"] == "Changed Name"
    assert fields["email"] == "changed@example.com"
    assert fields["address"] == "2 Test Street"
    assert fields["creditcard"] == "1111-1111-1111-1111"
    client.logout()
    assert f"Welcome {new_user}," in client.login(new_user, "new-secret")


@pytest.mark.req("AUTH-10")
def test_profile_update_with_unmatched_passwords_changes_nothing(client, new_user):
    client.update_profile("one", "two", "Changed Name", "changed@example.com")
    assert client.profile_fields()["fullname"] == "Test User"
    client.logout()
    assert f"Welcome {new_user}," in client.login(new_user, PASSWORD)


@pytest.mark.req("AUTH-11")
def test_the_account_page_shows_the_stored_password_and_card_number(client, new_user):
    # Keep-or-fix KF-3: the profile form is filled with the plain-text password and full card
    # number, so both are in the page's HTML.
    fields = client.profile_fields()
    assert fields["password"] == PASSWORD
    assert fields["creditcard"] == "0000-0000-0000-0000"


def test_a_second_client_has_no_session():
    # Guards the harness: each LegacyClient has its own cookies.
    other = LegacyClient()
    try:
        assert "User Not Logged in" in other.home()
    finally:
        other.close()


@pytest.mark.req("AUTH-12")
def test_logout_ends_the_session(client, new_user):
    client.logout()
    assert "User Not Logged in" in client.home()
