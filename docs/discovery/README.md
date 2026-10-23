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
| Does the old slice behave as the requirements say? | 13 characterisation tests, passing against the legacy app in CI |
| Keep or fix the odd behaviour? | `keep-or-fix.md` |
| What did the agent get wrong? | `agent-errors.md` |

## First gate: status

**Not yet passed.** Before it:

- [ ] Characterisation tests for the remaining high- and medium-risk hypotheses (TRADE-6, PORT-1, ACCT-1, AUTH-5 to AUTH-8, PRICE-2, PRICE-3, ADMIN-2), each traced to its requirement.
- [ ] A JMeter baseline for NFR-1 on the legacy app.
- [ ] Luke: scope decisions S1–S5 (`requirements.md`).
- [ ] Luke: keep-or-fix decisions KF-1 to KF-9.
- [ ] Luke: sign off the requirements, recording any dropped with the reason.
