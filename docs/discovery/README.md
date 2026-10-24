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
| Does the old slice behave as the requirements say? | 51 characterisation test cases, passing against the legacy app and its fixtures image in CI |
| How does it perform? | `../../perf/baseline.md` (NFR-1) |
| Keep or fix the odd behaviour? | `keep-or-fix.md` |
| What did the agent get wrong? | `agent-errors.md` |

## First gate: status

**Ready for Luke** (24 October 2026). Discovery's work is done; the gate is his.

- [x] Every requirement confirmed or corrected by a characterisation test, except ADMIN-4 (checked by hand: it destroys all data) and NFR-2 (waits on KF-4 and KF-12).
- [x] Every one of the manual's 13 features traced to at least one tested requirement (`requirements.md`).
- [x] A JMeter baseline for NFR-1 on the legacy app (`perf/baseline.md`).
- [ ] Luke: scope decisions S1–S6 (`requirements.md`).
- [ ] Luke: keep-or-fix decisions KF-1 to KF-17.
- [ ] Luke: sign off the requirements, recording any dropped with the reason.
