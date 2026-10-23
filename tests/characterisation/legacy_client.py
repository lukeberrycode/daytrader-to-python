"""Drives the legacy DayTrader 8 through its boundary: the JSP web app and the REST quotes API.

The tests use only the methods here, never the HTML, so the same tests can run against the new slice
through a second client with the same methods. Money is always returned as Decimal.
"""

import html
import os
import re
from dataclasses import dataclass
from decimal import Decimal

import httpx

BASE_URL = os.environ.get("LEGACY_URL", "http://localhost:9080/daytrader")


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: Decimal
    open: Decimal
    change: Decimal


@dataclass(frozen=True)
class Order:
    order_id: int
    status: str
    fee: Decimal
    order_type: str
    symbol: str
    quantity: Decimal


def _text(page: str) -> str:
    """The page as plain text with single spaces, for matching labels and values."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))


class LegacyClient:
    def __init__(self) -> None:
        self._http = httpx.Client(base_url=BASE_URL, timeout=30, follow_redirects=True)

    def close(self) -> None:
        self._http.close()

    def _app(self, **params: str) -> str:
        response = self._http.get("/app", params=params)
        response.raise_for_status()
        return _text(response.text)

    # Quotes are public: the REST API needs no login.
    def quote(self, symbol: str) -> Quote:
        response = self._http.get(f"/rest/quotes/{symbol}")
        response.raise_for_status()
        # parse_float keeps the JSON numbers exact instead of turning them into floats.
        (data,) = response.json(parse_float=Decimal, parse_int=Decimal)
        return Quote(data["symbol"], data["price"], data["open"], data["change"])

    def raw_quotes_json(self, symbols: str) -> str:
        response = self._http.get(f"/rest/quotes/{symbols}")
        response.raise_for_status()
        return response.text

    def admin_page(self) -> str:
        response = self._http.get("/config")
        response.raise_for_status()
        return _text(response.text)

    def register(
        self, user_id: str, password: str, opening_balance: str, confirm: str | None = None
    ) -> str:
        return self._app(
            action="register",
            **{
                "user id": user_id,
                "passwd": password,
                "confirm passwd": password if confirm is None else confirm,
                "Full Name": "Test User",
                "Credit Card Number": "0000-0000-0000-0000",
                "money": opening_balance,
                "email": "test@example.com",
                "snail mail": "1 Test Street",
            },
        )

    def login(self, user_id: str, password: str) -> str:
        return self._app(action="login", uid=user_id, passwd=password)

    def logout(self) -> str:
        return self._app(action="logout")

    def home(self) -> str:
        return self._app(action="home")

    def account_page(self) -> str:
        return self._app(action="account")

    def total_orders(self) -> int:
        return int(re.search(r"Total Orders: (\d+)", self.account_page()).group(1))

    def cash_balance(self) -> Decimal:
        page = self._app(action="account")
        return Decimal(re.search(r"cash balance: (-?[\d.]+)", page).group(1))

    def opening_balance(self) -> Decimal:
        page = self._app(action="account")
        return Decimal(re.search(r"opening balance: (-?[\d.]+)", page).group(1))

    def holding_ids(self) -> list[int]:
        response = self._http.get("/app", params={"action": "portfolio"})
        response.raise_for_status()
        return sorted({int(h) for h in re.findall(r"holdingID=(\d+)", response.text)})

    def buy(self, symbol: str, quantity: str) -> Order:
        return self._order(self._app(action="buy", symbol=symbol, quantity=quantity))

    def sell(self, holding_id: int) -> Order:
        return self._order(self._app(action="sell", holdingID=str(holding_id)))

    @staticmethod
    def _order(page: str) -> Order:
        # The order page's details row: id, status, created, completed, fee, type, symbol, quantity.
        match = re.search(
            r"order ID order status creation date completion date txn fee type symbol quantity "
            r"(\d+) (\w+) \S+ \S+ (?:\S+ \S+ )?(-?[\d.]+) (\w+) (\S+) (-?[\d.]+)",
            page,
        )
        if match is None:
            raise AssertionError(f"No order details on the page: {page[:500]}")
        order_id, status, fee, order_type, symbol, quantity = match.groups()
        return Order(int(order_id), status, Decimal(fee), order_type, symbol, Decimal(quantity))
