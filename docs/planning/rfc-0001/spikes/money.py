"""Shared by both spikes: the home page's figures, from HOME-1N and HOME-2N. Decimal only."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def summary(balance: Decimal, open_balance: Decimal, rows: list[tuple]) -> dict:
    """HOME-1N: each row's value rounded for its row; the total is the exact sum of the unrounded
    values, rounded once. HOME-2N: the ratio to 10 places, then the percentage to 2."""
    values = [(s, q, q * price) for s, q, price in rows]
    holdings = [
        {"symbol": s, "quantity": q, "value": v.quantize(CENT, ROUND_HALF_UP)} for s, q, v in values
    ]
    market_value = sum((v for _, _, v in values), Decimal(0)).quantize(CENT, ROUND_HALF_UP)
    total = balance + market_value
    ratio = Decimal(1)
    if open_balance:
        ratio = (total / open_balance).quantize(Decimal("1e-10"), ROUND_HALF_UP)
    return {
        "balance": balance,
        "count": len(holdings),
        "market_value": market_value,
        "gain": total - open_balance,
        "gain_percent": ((ratio - 1) * 100).quantize(CENT, ROUND_HALF_UP),
        "holdings": holdings,
    }
