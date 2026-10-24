# Discovery

The first phase of the method (`docs/method.md`), run on DayTrader 8.

| Question | Answer |
|---|---|
| Can we run the old slice locally? | Yes: `legacy/docker/Dockerfile`, see the README. Nothing that couldn't be reproduced |
| What does it do? | `one-pager.md` |
| How does it do it? | `architecture.md` |
| What data does it own? | `data-inventory.md` |
| Who are its users; their states, risks and journeys? | `users-states-journeys.md` |
| What are the requirements, and how is each tested? | `requirements.md`, `tests/characterisation/` |
| Does the old slice behave as the requirements say? | 61 characterisation test cases (plus one that checks the harness), passing against the legacy app and its fixtures image in CI |
| How does it perform? | `../../perf/baseline.md` (NFR-1) |
| Keep or fix the odd behaviour? | `keep-or-fix.md` |
| What did the agent get wrong? | `agent-errors.md` |

## First gate: status

**Passed except KF-7** (24 October 2026). Luke accepted every scope and keep-or-fix suggestion except KF-7, which is open: how long to keep orders (`keep-or-fix.md`).

- [x] Every functional requirement confirmed or corrected by a characterisation test, except ADMIN-4 (checked by hand: it destroys all data). Of the non-functional ones, NFR-1 has a measured baseline, NFR-3 is met by the set-up, and NFR-2 waits on KF-4 and KF-12.
- [x] Every one of the manual's 13 features traced to at least one tested requirement (`requirements.md`).
- [x] A JMeter baseline for NFR-1 on the legacy app (`perf/baseline.md`).
- [x] Luke: scope decisions S1–S6 (`requirements.md`), 24 October 2026.
- [x] Luke: keep-or-fix decisions KF-1 to KF-6 and KF-8 to KF-17, 24 October 2026.
- [ ] Luke: KF-7 (how long to keep orders).
- [ ] Luke: sign off the requirements once KF-7 is decided (ORDER-1 is high risk and has no agreed behaviour yet), so Planning starts after it. The dropped scope and its reason are in `requirements.md`.
