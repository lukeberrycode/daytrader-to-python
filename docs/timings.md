# Timings

The method measures every phase: an estimate before it starts, the actual time when it ends. The comparison is the evidence for what AI made faster.

How the estimates are made, and what they're compared with: `estimation.md`.

## Whole migration

| | Hours |
|---|---|
| Estimate without AI | Not yet estimated (`estimation.md`) |
| Actual: Luke's hands-on time, all phases | |
| Actual: agent time, all phases | |
| Actual: tokens and cost, all phases | |

## Per phase

Each phase is estimated before it starts. "Luke" is his hands-on time: reviewing, deciding at gates, correcting. Agent time and tokens come from the session or run logs.

**Tokens and cost.** Interactive Claude Code sessions run on Luke's subscription, so they cost nothing per token. For them, the table records tokens (output, and input read from cache) and an *API-equivalent* cost: what the same tokens would cost at Anthropic's published API prices. That makes subscription work comparable with API work; it isn't money spent. The AI review in GitHub Actions uses an API key, so its cost is real and is recorded in USD from each run's job summary. Prices used for Claude Opus 5.5, per million tokens: input $4.00, output $20.00, cache read $0.20, cache write $8.00 (1-hour cache, as Claude Code uses).

| Phase | Estimate without AI (h) | Started | Finished | Luke (h) | Agent (h) | Tokens / cost |
|---|---|---|---|---|---|---|
| **Discovery (parts 1 and 2)** | **119.3** (O 84.3, M 115.7, P 168.3; `estimation.md`) | | | | | |
| Discovery, part 1: set-up, running locally, first documents and tests | (in the phase estimate) | 23 Oct 2026 14:36 | 23 Oct 2026 14:43 (file times) | 0.76 (see note) | 0.12 | Subscription. Build: 42.8k output, 5.78M cache-read, 131k cache-write; API-equivalent $3.06. Follow-up (see note): 35.5k output, 6.96M cache-read, 91k cache-write; API-equivalent $2.83. **Total API-equivalent $5.89** |
| Discovery, part 2: remaining tests and the first gate | (in the phase estimate) | | | | | |
| Planning | | | | | | |
| Execution (per vertical slice) | | | | | | |
| Decommissioning and evaluation | | | | | | |

**Note on Discovery part 1, Luke's time.** Luke estimates his hands-on time at about half of the 91 minutes from 14:44, when the agent first asked him for an estimate, to 16:15: about 0.76 hours. Most of it went on deciding the estimation method (`estimation.md`). That's a one-off: it hadn't been done before and won't need doing again, so it overstates the review time a phase would normally need.

**Note on Discovery part 1, tokens.** The build is 14:36 to 14:44 (50 responses). The follow-up is 14:44 to 16:22 (37 responses): the licence, publishing the method, and defining the estimation method. As with Luke's time, most of the follow-up went on the estimation method, a one-off. Figures are from the Claude Code session log (`usage` on each response).
