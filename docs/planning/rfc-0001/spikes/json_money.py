"""RFC-0001 spike: can each option write Decimal("25.90") to JSON as the number 25.90 (MONEY-1N)?"""

import json
from decimal import Decimal

VALUE = {"price": Decimal("25.90"), "volume": Decimal("244711.85")}
WANT = '{"price": 25.90, "volume": 244711.85}'


def attempt(name, fn):
    try:
        out = fn()
    except Exception as e:  # noqa: BLE001 - reporting each option's failure is the point
        out = f"error: {type(e).__name__}: {e}"
    ok = out.replace(" ", "") == WANT.replace(" ", "")
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {out}")


attempt("stdlib json", lambda: json.dumps(VALUE))
attempt("stdlib json, default=float", lambda: json.dumps(VALUE, default=float))

import simplejson  # noqa: E402

attempt("simplejson, use_decimal", lambda: simplejson.dumps(VALUE, use_decimal=True))

from django.core.serializers.json import DjangoJSONEncoder  # noqa: E402

attempt("Django JsonResponse encoder", lambda: json.dumps(VALUE, cls=DjangoJSONEncoder))

from pydantic import BaseModel  # noqa: E402


class Money(BaseModel):
    price: Decimal
    volume: Decimal


attempt("Pydantic v2 (FastAPI's default)", lambda: Money(**VALUE).model_dump_json())
attempt(
    "Pydantic v2, mode=python then stdlib json",
    lambda: json.dumps(Money(**VALUE).model_dump(mode="python"), default=float),
)
