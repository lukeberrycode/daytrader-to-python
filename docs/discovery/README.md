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

**Passed** (24 October 2026). Luke accepted every scope and keep-or-fix suggestion, chose option 1 for KF-7 (keep every order), and accepted Claude's recommendations on the AI review's points: the new slice's requirements are in `requirements.md`, with their own IDs and a planned test each. Planning can start.

- [x] Every functional requirement confirmed or corrected by a characterisation test, except ADMIN-4 (checked by hand: it destroys all data). Of the non-functional ones, NFR-1 has a measured baseline, NFR-3 is met by the set-up, and NFR-2 is required by the gate (MONEY-1N).
- [x] Every one of the manual's 13 features traced to at least one tested requirement (`requirements.md`).
- [x] A JMeter baseline for NFR-1 on the legacy app (`perf/baseline.md`).
- [x] Luke: scope decisions S1–S6 (`requirements.md`), 24 October 2026.
- [x] Luke: keep-or-fix decisions KF-1 to KF-6 and KF-8 to KF-17, 24 October 2026.
- [x] Luke: KF-7, keep every order (24 October 2026).
- [x] Luke: sign off the requirements, including the new slice's (`requirements.md`) and the dropped scope with its reason (24 October 2026).
