"""Shared by both spikes: the home page's figures, from HOME-1N and HOME-2N. Decimal only."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def summary(balance: Decimal, open_balance: Decimal, rows: list[tuple]) -> dict:
    holdings = [
        {"symbol": s, "quantity": q, "value": (q * price).quantize(CENT, ROUND_HALF_UP)}
        for s, q, price in rows
    ]
    market_value = sum((h["value"] for h in holdings), Decimal("0.00"))
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
