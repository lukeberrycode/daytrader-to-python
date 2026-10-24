"""Drives the legacy DayTrader 8 through its boundary: the JSP web app and the REST quotes API.

The tests use only the methods here, never the HTML, so the same tests can run against the new slice
through a second client with the same methods. Money is always returned as Decimal.
"""

import html
import json
import os
import re
from dataclasses import dataclass
from decimal import Decimal

import httpx
from websockets.sync.client import connect

BASE_URL = os.environ.get("LEGACY_URL", "http://localhost:9080/daytrader")
MONEY = r"(-?[\d.]+)"


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: Decimal
    open: Decimal
    change: Decimal
    low: Decimal
    high: Decimal
    volume: Decimal


@dataclass(frozen=True)
class HomeSummary:
    cash: Decimal
    holdings: int
    holdings_total: Decimal
    cash_and_holdings: Decimal
    opening_balance: Decimal
    gain: Decimal
    gain_percent: Decimal


@dataclass(frozen=True)
class PortfolioRow:
    holding_id: int
    symbol: str
    quantity: Decimal
    purchase_price: Decimal
    current_price: Decimal
    basis: Decimal
    market_value: Decimal
    gain: Decimal


@dataclass(frozen=True)
class Portfolio:
    rows: list[PortfolioRow]
    total_basis: Decimal
    total_market_value: Decimal
    total_gain: Decimal
    total_gain_percent: Decimal


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
    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url
        self._http = httpx.Client(base_url=base_url, timeout=30, follow_redirects=True)

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
        return _quote(data)

    def quotes(self, symbols: list[str]) -> list[Quote | None]:
        """Several quotes in one request; None where the API returns null."""
        response = self._http.post("/rest/quotes", data={"symbols": ",".join(symbols)})
        response.raise_for_status()
        return [
            _quote(d) if d else None for d in response.json(parse_float=Decimal, parse_int=Decimal)
        ]

    def quotes_page(self, symbols: str) -> str:
        return self._app(action="quotes", symbols=symbols)

    def market_summary(self) -> dict:
        """The market summary, which the app sends only over its WebSocket."""
        url = self.base_url.replace("http", "ws", 1) + "/marketsummary"
        with connect(url, open_timeout=10) as socket:
            socket.send(json.dumps({"action": "updateMarketSummary"}))
            return json.loads(socket.recv(timeout=10), parse_float=Decimal, parse_int=Decimal)

    def raw_quotes_json(self, symbols: str) -> str:
        response = self._http.get(f"/rest/quotes/{symbols}")
        response.raise_for_status()
        return response.text

    def admin_page(self) -> str:
        response = self._http.get("/config")
        response.raise_for_status()
        return _text(response.text)

    def admin(self, **params: str) -> str:
        response = self._http.get("/config", params=params)
        response.raise_for_status()
        return _text(response.text)

    def scenario(self) -> int:
        """One request to the scenario servlet, with no session, so it logs in as a new random
        user each time (it keeps its user in the session). Returns the HTTP status."""
        return httpx.get(f"{self.base_url}/scenario", timeout=30).status_code

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

    def status(self, **params: str) -> int:
        """The HTTP status of an app request, for behaviour that ends in an error page."""
        return self._http.get("/app", params=params).status_code

    def update_profile(self, password: str, confirm: str, full_name: str, email: str) -> str:
        return self._app(
            action="update_profile",
            password=password,
            cpassword=confirm,
            fullname=full_name,
            address="2 Test Street",
            creditcard="1111-1111-1111-1111",
            email=email,
        )

    def profile_fields(self) -> dict[str, str]:
        """The values in the account page's profile form."""
        response = self._http.get("/app", params={"action": "account"})
        response.raise_for_status()
        return _form_fields(response.text)

    def config_switches(self) -> dict[str, bool]:
        """The configuration page's checkboxes: name -> checked."""
        response = self._http.get("/config")
        response.raise_for_status()
        tags = re.findall(r"<INPUT[^>]*>", response.text, flags=re.I | re.S)
        return {
            re.search(r'name="([^"]+)"', t, re.I).group(1): bool(re.search(r"\bchecked\b", t, re.I))
            for t in tags
            if re.search(r'type="checkbox"', t, re.I)
        }

    def raw_quotes_get(self, symbols: str) -> list:
        response = self._http.get(f"/rest/quotes/{symbols}")
        response.raise_for_status()
        return response.json(parse_float=Decimal, parse_int=Decimal)

    def config_fields(self) -> dict[str, str]:
        """The values in the configuration page's form."""
        response = self._http.get("/config")
        response.raise_for_status()
        return _form_fields(response.text)

    def login_counts(self) -> tuple[int, int]:
        page = self.account_page()
        logins = int(re.search(r"total logins: (\d+)", page).group(1))
        logouts = int(re.search(r"total logouts: (\d+)", page).group(1))
        return logins, logouts

    def home_summary(self) -> HomeSummary:
        page = self.home()
        match = re.search(
            rf"opening balance: \$ {MONEY} (\d+) \$ {MONEY} \$ {MONEY} \$ {MONEY} "
            rf"current gain/\(loss\): \$ {MONEY} \( ([+-]?[\d.]+)% \)",
            page,
        )
        if match is None:
            raise AssertionError(f"No account summary on the home page: {page[:500]}")
        cash, count, total, both, opening, gain, percent = match.groups()
        return HomeSummary(
            Decimal(cash),
            int(count),
            Decimal(total),
            Decimal(both),
            Decimal(opening),
            Decimal(gain),
            Decimal(percent),
        )

    def portfolio(self) -> Portfolio:
        page = self._app(action="portfolio")
        rows = [
            PortfolioRow(int(h), sym, *(Decimal(v) for v in values))
            for h, sym, *values in re.findall(
                r"(\d+) \w{3} \w{3} \d+ [\d:]+ \w+ \d{4} (s:\d+) "
                rf"{MONEY} {MONEY} {MONEY} {MONEY} {MONEY} {MONEY} sell",
                page,
            )
        ]
        total = re.search(rf"Total \$ {MONEY} \$ {MONEY} \$ {MONEY} \( ([+-]?[\d.]+)% \)", page)
        if total is None:
            raise AssertionError(f"No totals row on the portfolio page: {page[:500]}")
        return Portfolio(rows, *(Decimal(v) for v in total.groups()))

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


def _form_fields(page: str) -> dict[str, str]:
    fields = {}
    for tag in re.findall(r"<INPUT[^>]*>", page, flags=re.I | re.S):
        name = re.search(r'name="([^"]+)"', tag, flags=re.I)
        value = re.search(r'value="([^"]*)"', tag, flags=re.I)
        if name:
            fields[name.group(1)] = html.unescape(value.group(1)) if value else ""
    return fields


def _quote(data: dict) -> Quote:
    return Quote(
        data["symbol"],
        data["price"],
        data["open"],
        data["change"],
        data["low"],
        data["high"],
        data["volume"],
    )
