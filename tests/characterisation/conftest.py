import os
import uuid
from collections.abc import Iterator

import pytest

from .legacy_client import LegacyClient

PASSWORD = "secret"
OPENING_BALANCE = "100000.00"


@pytest.fixture
def client() -> Iterator[LegacyClient]:
    c = LegacyClient()
    yield c
    c.close()


@pytest.fixture
def new_user(client: LegacyClient) -> str:
    """A newly registered user, logged in, so no test depends on another test's trades."""
    user_id = f"ct-{uuid.uuid4().hex[:12]}"
    client.register(user_id, PASSWORD, OPENING_BALANCE)
    return user_id


FIXTURES_URL = os.environ.get("FIXTURES_URL")


@pytest.fixture
def fixtures_client() -> Iterator[LegacyClient]:
    """A client for the "fixtures" image: the legacy app with test prices seeded."""
    if not FIXTURES_URL:
        pytest.skip("FIXTURES_URL not set: start the fixtures image (see the README)")
    c = LegacyClient(FIXTURES_URL)
    yield c
    c.close()
