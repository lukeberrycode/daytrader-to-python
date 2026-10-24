# DayTrader to Python

A worked example of migrating a legacy system to a new stack with AI assistance, by **requirements, not line-by-line porting**. The legacy system is [DayTrader 8](https://github.com/OpenLiberty/sample.daytrader8), IBM's Java EE 8 sample stock-trading app; the destination is Python (to be confirmed by an RFC in the Planning phase).

The method is in [`docs/method.md`](docs/method.md). In short:

- Requirements are drawn out of the old system (AI-assisted) and checked by **characterisation tests** run against the running old system. The same tests later run against the new one.
- Odd behaviour goes to a **keep-or-fix** log for a human decision, not straight into the requirements.
- People approve at each **gate**. Every phase is **timed** against an estimate.

## Progress

| Phase | Status |
|---|---|
| Discovery | Part 1 done: [`docs/discovery/`](docs/discovery/). First gate not yet passed |
| Planning | Not started |
| Execution | Not started |
| Evaluation | Not started |

## Running the legacy app

Needs Docker and [uv](https://docs.astral.sh/uv/) at the version set by `required-version` in `pyproject.toml` (`uv self update <version>`).

```sh
git clone --recurse-submodules https://github.com/lukeberrycode/daytrader-to-python.git
cd daytrader-to-python
docker build -t daytrader8-legacy -f legacy/docker/Dockerfile legacy
docker run -d --name legacy -p 127.0.0.1:9080:9080 daytrader8-legacy
scripts/wait-for-legacy.sh
```

Then open http://localhost:9080/daytrader (log in as `uid:0`, password `xxx`). The port is bound to `127.0.0.1` on purpose: the legacy app has an admin page with no login and stores passwords in plain text, so it shouldn't be reachable from other machines.

## Characterisation tests

```sh
uv sync
uv run pytest tests/characterisation
```

Each test is marked with the requirement it checks, e.g. `@pytest.mark.req("TRADE-1")`. The tests talk to the app only through `tests/characterisation/legacy_client.py`, so a second client with the same methods will run them against the new slice. Every pull request runs them in CI against a freshly built legacy app.

## AI review

Every pull request gets an automated review from Claude ([`.github/workflows/ai-review.yml`](.github/workflows/ai-review.yml)). It's review only: it can comment, but it can't push or approve. Its cost per run goes in the job summary. Every merge is reviewed and made by a person.

## Licences

Copyright 2026 Luke Berry. Licensed under the [Apache License 2.0](LICENSE), except the `legacy/daytrader8` submodule.

DayTrader 8 is © IBM, Apache-2.0, and sits unmodified in the `legacy/daytrader8` submodule.
