# RFC-0001: the new slice's stack

**Status:** proposed, for Luke's decision at the gate "Is the destination stack approved?" (`docs/method.md`).
**Date:** 24 October 2026. **Author:** Claude Code, from the requirements Luke signed off at the first gate.

## The question

What should the new slice be built with, to meet the requirements in `docs/discovery/requirements.md`, including the N requirements the gate added?

Python is the destination (Luke's steer, recorded in the demo plan). This RFC chooses within Python and says what that choice costs.

## What the requirements ask of a stack

| Need | From |
|---|---|
| Server-rendered web pages with sessions, forms and login: one web UI replacing JSP and JSF | S1, AUTH-*, TRADE-*, HOME-*, PORT-1 |
| Hashed passwords, the same response to a wrong password and an unknown user ID (including timing), no secrets in logs, an operator login | AUTH-3N, AUTH-13N, AUTH-14N, ADMIN-1N |
| Exact decimal money in the database, in code and in JSON, written as numbers with 2 places | MONEY-1N, TRADE-7N, NFR-2 |
| A JSON REST API with the legacy field names | QUOTE-1, QUOTE-2N, S4 |
| A WebSocket for the market summary | MARKET-1, MARKET-2, S4 |
| Orders kept for good, in a table partitioned by month if it grows | ORDER-1N |
| Performance against the legacy baseline | NFR-1 |
| Runs locally in containers from one command | NFR-3 |

## Options considered

1. **Django 6.1**, with its ORM and migrations, Django templates, built-in auth and sessions, and Channels for the WebSocket; served by gunicorn.
2. **FastAPI 0.162**, with SQLAlchemy 2.1 (async) and Alembic, Jinja2 templates, and its native WebSocket support; served by uvicorn.
3. **Flask** (and similar micro-frameworks): considered and not spiked. It gives neither Django's built-in security and admin nor FastAPI's async and typed API, so it would need the most assembled by hand.

PostgreSQL is assumed for all three: `NUMERIC` maps exactly to Python's `Decimal`, and it supports declarative partitioning by month (ORDER-1N). DayTrader's Derby is embedded in the Java process and has no Python driver to speak of.

## Evidence

Spikes are in `rfc-0001/spikes/`, with their code and raw results. All ran on Luke's laptop (Intel Core i7-7600U, 4 logical CPUs) on 24 October 2026, with Python 3.14.8.

### 1. Throughput (NFR-1)

One page shaped like DayTrader's home page: read an account and its 5 holdings with their quotes from Postgres, compute the figures with `Decimal` (HOME-1N, HOME-2N), render HTML. Each framework was written the way it would normally be used: Django's ORM and templates on gunicorn; FastAPI's async SQLAlchemy and Jinja2 on `uvicorn[standard]`. The legacy app's own home page was measured the same way. Load: `oha`, 10 connections, 60 seconds after a 15-second warm-up, one server at a time.

Three runs at 8 server workers, all on the same code, on the evening of 24 October 2026 (`results/workers-8-run1` to `-run3`):

| Requests a second | Run 1 | Run 2 | Run 3 | Mean | p95 range |
|---|---|---|---|---|---|
| Legacy (Java EE on Open Liberty, embedded Derby) | 2,136 | 2,014 | 1,875 | 2,008 | 9–11 ms |
| Django | 760 | 674 | 690 | 708 | 19–25 ms |
| FastAPI | 619 | 477 | 582 | 559 | 27–41 ms |

- Both Python stacks reach about a third of the legacy app's throughput (Django 35%, FastAPI 28%), with p95 latency 2 to 4 times higher.
- **This understates the gap.** The legacy home page is 8,231 bytes; the spikes' pages are about 435 bytes, so the legacy app does far more rendering per request.
- Django was ahead of FastAPI in all three runs. FastAPI's async model gives no advantage here: each request makes two short database queries, so there's little waiting to overlap.
- **Noise:** runs earlier the same evening, while other work was using the machine, gave much lower figures for all three (legacy 1,208 to 1,654, Django 458 to 586; `results/workers-4`, `results/workers-8`). Those runs also predate two fixes from the AI review: a check that the legacy login worked, and the spike's rounding (HOME-1N). They're kept for the record, not used. Compare only figures from the same run.
- The legacy app's database runs inside its process, while Postgres is a separate container. A production deployment would have the same separation, so that difference stays.
- A first FastAPI run without `uvicorn[standard]` (its fast event loop and HTTP parser) managed 149 req/s. That set-up was unfair, and is excluded.

**Consequence: NFR-1 as written ("no worse than the legacy app on the same machine") is unlikely to be met by either Python stack, even with substantial optimisation.** That is a gate decision (below).

### 2. Money in JSON (MONEY-1N)

Can each option write `Decimal("25.90")` as the JSON number `25.90`? (`spikes/json_money.py`, `results/json_money.txt`)

| Option | Output | |
|---|---|---|
| Python's `json` | `TypeError` | Fails |
| Python's `json` with `default=float` | `25.9` | Fails: goes through a float |
| Django's JSON encoder | `"25.90"` | Fails: a string |
| Pydantic v2 (FastAPI's default) | `"25.90"` | Fails: a string |
| `simplejson` with `use_decimal=True` | `25.90` | Passes |

Neither framework does it out of the box, so the API writes JSON with `simplejson` either way. This doesn't separate the options.

`simplejson` writes a `Decimal` at whatever precision it has: `Decimal("25.9")` becomes `25.9`, and a 4-place quantity times a 2-place price has 6 places. So every amount is rounded to 2 places before encoding, in one function both the API and the WebSocket use (now part of MONEY-1N). The spike only tried values that already had 2 places; the AI review of this RFC pointed that out.

### 3. Security built in (AUTH-3N, AUTH-13N, AUTH-14N, ADMIN-1N)

- **Django:** login (`ModelBackend.authenticate`) calls `check_password_with_timing_attack_mitigation` whether or not the user exists, which is AUTH-3N's timing rule. An Argon2 password hasher is built in (AUTH-13N); it needs `argon2-cffi` installed and the hasher set first in `PASSWORD_HASHERS`. Sessions, CSRF protection, form validation and a permission system for the operator pages (ADMIN-1N) are built in.
- These are **hypotheses from reading Django 6.1.2's source**, not yet tested. The tests that will confirm them are already planned: AUTH-3N's timing test and AUTH-13N's stored-hash test (`requirements.md`).
- **FastAPI:** none of these is built in. Sessions, CSRF, password hashing, the timing rule and operator permissions would be assembled from separate libraries and our own code, and every line of it reviewed.

Most of the gate's fixes are security fixes (KF-3, KF-6). The less security code we write, the less there is to get wrong.

### 4. Other needs

| Need | Django | FastAPI |
|---|---|---|
| WebSocket (MARKET-1, MARKET-2) | Channels, an official Django project, under an ASGI server | Built in |
| Exact decimals in the database | `DecimalField` → `NUMERIC` → `Decimal` | `Numeric(asdecimal=True)` → `Decimal` |
| Partitioning by month (ORDER-1N) | A raw SQL migration | A raw SQL migration |
| Migrations | Built in | Alembic |
| Tests | pytest with pytest-django; the characterisation tests are black-box either way | pytest with httpx |

## Recommendation

**Option 1: Django 6.1 on Python 3.14, with PostgreSQL 17.**

- It meets the security requirements with built-in, widely reviewed code rather than code we'd write ourselves, and those requirements are most of what the gate changed.
- It was faster than FastAPI in all three spike runs. Async would add complexity with no measured benefit for this workload.
- Its admin and permission system covers the operator features (ADMIN-1N to ADMIN-3N, SEED-1N).
- Its weakness is the WebSocket, which needs Channels and an ASGI server alongside gunicorn. That's one small part of the app (MARKET-1, MARKET-2).

Upgrade to 6.2, the next long-term-support release, when it's out (expected in 2027).

The proposed architecture for this option is in `architecture.md`.

## Decisions for the gate

1. **The stack:** approve Django 6.1, Python 3.14 and PostgreSQL 17, or choose another option.
2. **NFR-1, which the evidence says needs revisiting.** Options:
   - **(a) Keep it as written.** Planning and Execution then include performance work (caching, query tuning, more workers), and the risk is that it still isn't met.
   - **(b) Restate it as service levels the trader would notice:** under DayTrader's own JMeter workload on the same machine, 0 errors and a p95 response time within a set limit (say 100 ms), with throughput measured and reported beside the legacy baseline rather than required to match it. *Claude's suggestion.* The legacy app's raw speed comes from a mature JVM and an in-process database, not from anything a trader asked for, and the measured gap belongs in the record, not hidden.
   - **(c) Change the destination** to something closer to the JVM's throughput (for example Kotlin or Java on a modern framework). That drops Python, Luke's steer, and the demo's reason for being.
