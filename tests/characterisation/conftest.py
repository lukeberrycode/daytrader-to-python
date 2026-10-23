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
