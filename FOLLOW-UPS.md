# Follow-ups

Points found on 2026-11-02 during a review of this repository (at `30d0e161`) for the `lukeberrycode-help` notes. Each one says what was found, why it matters, and what to do. Delete an entry once it's dealt with, and this file once it's empty.

## 1. Upgrade websockets from 17.3 to 17.4 (security fix)

**Found:** `uv.lock` locks `websockets` at `17.3`. This is true on `main` and on every branch on GitHub as of 2026-11-02 (`planning/rfc-stack`, `fix/kf-18-reset-deletes-orders`, `docs/gate-1`, `discovery/part-2`). `pyproject.toml` asks for `"websockets>=17.3"` in the `dev` dependency group.

**Why it matters:** websockets 17.4, released on 30 October 2026, "fixes a security issue". `recv()` now rejects fragmented messages split into more than 4,096 frames. Earlier versions didn't enforce such a limit, so a server could make a client run out of memory (denial of service). The changelog says all implementations were affected, the threading client used here included; `recv_streaming()` isn't affected. The limit can be changed with the `WEBSOCKETS_MAX_FRAGMENTS` environment variable.

- Changelog: https://websockets.readthedocs.io/en/stable/project/changelog.html (section 17.4, "Security fix")

**Risk here: low.** The only user is `LegacyClient.market_summary()` in `tests/characterisation/legacy_client.py`, which opens `ws://localhost:9080/daytrader/marketsummary` on the local legacy app, sends `{"action": "updateMarketSummary"}` and reads one reply with `recv(timeout=10)`. It never talks to an untrusted server. It's still worth taking, because it's a one-line lock change and keeps the dependency current before the new slice's work starts.

**What to do:**

1. On a branch from `main`: `uv lock --upgrade-package websockets`. Because `pyproject.toml` already says `>=17.3`, only `uv.lock` changes.
2. Check the diff touches only the `websockets` entries in `uv.lock`.
3. Run the characterisation tests against the legacy app, at least `tests/characterisation/test_quotes.py` (MARKET-1 and MARKET-2 use the WebSocket).
4. Optionally raise the floor in `pyproject.toml` to `"websockets>=17.4"`, so a fresh lock can never pick a vulnerable version.
5. Merge, and rebase or merge `main` into any open branches (PR #4, PR #5) so they pick it up.

**Background:** the `lukeberrycode-help` note `python-websockets/what-is-python-websockets.md` explains the library and how this repository uses it.
