# DayTrader to Python

Migration of DayTrader 8 (Java EE, in the `legacy/daytrader8` submodule) to Python, following `docs/method.md`. Current phase: Discovery (`docs/discovery/README.md` has the gate checklist).

## Rules

- **Requirements, not porting.** Never translate Java to Python line by line, method by method or class by class. Code in the new slice meets requirements in `docs/discovery/requirements.md`, and each requirement is traced to a test.
- **The legacy app is the test oracle.** A requirement drawn from the code is a hypothesis until a characterisation test against the running legacy app confirms it. If a test shows the code-reading was wrong, correct the requirement and add a row to `docs/discovery/agent-errors.md`.
- **Odd behaviour goes to `docs/discovery/keep-or-fix.md`**, never straight into the requirements. Decisions there are Luke's.
- **Gates are Luke's.** Nothing after a gate starts until he has approved it.
- **Money is `decimal.Decimal`**, rounded with `quantize(..., rounding=ROUND_HALF_UP)`. Never `float`, never the built-in `round()`.
- **Never modify `legacy/daytrader8`.** Changes to how it's built or run go in `legacy/docker/`.
- **Time every phase** in `docs/timings.md`.
- Work on a branch; one pull request per change. Luke merges.
- Write docs in British English, in plain, short sentences.

## Commands

- `uv run ruff check`, `uv run ruff format`.
- `uv run pytest tests/characterisation` needs the legacy app running (see the README); PRICE-2 and PRICE-3 also need the fixtures image (`FIXTURES_URL`).
- `perf/run-baseline.sh` runs the NFR-1 load baseline. Nothing else may use the legacy app while it runs.
