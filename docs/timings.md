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
| **Discovery (parts 1 and 2)** | **119.3** (O 84.3, M 115.7, P 168.3; `estimation.md`) | 23 Oct 2026 14:36 | Gate passed 24 Oct 2026 | **1.26** (0.76 in part 1, mostly the one-off estimation method; 0.50 in part 2: review and gate) | **1.03** | **API-equivalent $15.90** (subscription), plus **$4.45** real spend on AI review (below) |
| Discovery, part 1: set-up, running locally, first documents and tests | (in the phase estimate) | 23 Oct 2026 14:36 | 23 Oct 2026 14:43 (file times) | 0.76 (see note) | 0.12 | Subscription. Build: 42.8k output, 5.78M cache-read, 131k cache-write; API-equivalent $3.06. Follow-up (see note): 35.5k output, 6.96M cache-read, 91k cache-write; API-equivalent $2.83. **Total API-equivalent $5.89** |
| Discovery, part 2: remaining tests and the first gate | (in the phase estimate) | 24 Oct 2026 19:06 | 24 Oct 2026 20:00 (last push); gate passed 24 Oct 2026 | 0.50 (30 minutes: review and gate decisions, including KF-7) | 0.91 (includes a 5-minute load test and five rounds of AI review fixes) | Subscription. 104.1k output, 33.6M cache-read, 150k cache-write; API-equivalent $10.01 |
| Planning | **71.2** (O 50.75, M 71.5, P 90.5; `estimation.md`, made 24 Oct 2026 before the phase started) | | | | | |
| Planning: RFC-0001 (stack options, spikes, proposed architecture) | 37.5 of the phase estimate | 24 Oct 2026 22:34 | 24 Oct 2026 23:03 (agent); stack gate pending | _Luke's review and gate to add_ | 0.49 (about 10 minutes of it lost to a mistake in the spike's set-up) | Subscription. 24.2k output, 10.4M cache-read, 36k cache-write; API-equivalent $2.86 |
| Execution (per vertical slice) | | | | | | |
| Decommissioning and evaluation | | | | | | |

**Note on Discovery part 1, Luke's time.** Luke estimates his hands-on time at about half of the 91 minutes from 14:44, when the agent first asked him for an estimate, to 16:15: about 0.76 hours. Most of it went on deciding the estimation method (`estimation.md`). That's a one-off: it hadn't been done before and won't need doing again, so it overstates the review time a phase would normally need.

**Discovery is closed** (gate passed 24 October 2026): estimated at 119.3 hours without AI; it took 1.26 hours of Luke's time and 1.03 hours of agent time, at $15.90 of API-equivalent tokens plus real AI review spend on its pull requests (below). It is one phase of one migration, and part 1's hours were mostly a one-off, defining the estimation method.

**Note on Discovery part 2.** The agent's work ran from 19:05:50 to 20:00:35 (89 responses). The first 19 minutes produced 41 more characterisation tests, the fixtures image, the load baseline, and the Discovery documents brought up to the gate. The remaining 36 minutes answered five rounds of AI review on pull request #2, which corrected two requirements (TRADE-7, ORDER-1's evidence) and fixed a flaky test. The phase isn't finished until Luke has reviewed it and made the gate decisions; his time for that goes in the Luke column.

**Note on Discovery part 1, tokens.** The build is 14:36 to 14:44 (50 responses). The follow-up is 14:44 to 16:22 (37 responses): the licence, publishing the method, and defining the estimation method. As with Luke's time, most of the follow-up went on the estimation method, a one-off. Figures are from the Claude Code session log (`usage` on each response).

## AI review costs

Real API spend, from each run's job summary (`.github/workflows/ai-review.yml`).

| Pull request | Run | Cost (USD) | Note |
|---|---|---|---|
| #1 | 1 | 0.00 | Failed before calling the API: the action expected the Claude GitHub App. Fixed by using the workflow's own token |
| #1 | 2 | 0.23 | 2 findings (actions pinned by tag; uv version in four places), both fixed in the same pull request |
| #1 | 3 | 0.19 | No findings; listed two things it couldn't check from the job, both checked by hand |
| #2 | 1 | 0.78 | 7 findings, all fixed in the same pull request; marked failed for taking 29 turns against a cap of 20 (cap raised to 40) |
| #2 | 2 | 0.83 | 4 groups of findings: TRADE-7 overstated (balances truncate toward zero), requirements claiming more than their tests showed, test isolation, docs. All fixed |
| #2 | 3 | 0.74 | 6 findings, including a flaky SCEN-1 test that CI then failed on, and fixture errors that could pass silently. All fixed |
| #2 | 4 | 0.92 | 6 findings: two tests that couldn't fail (ADMIN-2, HOME-2), two requirements broader than their tests (AUTH-7, MARKET-2), two wording. All fixed |
| #2 | 5 | 0.76 | 1 finding (posted inline; the summary comment was blocked): ORDER-1's evidence couldn't tell deleted orders from hidden ones. A new test shows they're deleted. Marked failed after 4 permission denials |
| #2 | 6 | 0.00 | Failed before any model ran (0.6 seconds, no tokens); the log gives no reason. For Luke to check in the Anthropic Console (spend limit or credit balance) |

| #3 | 1 | 0.43 | 8 findings on the gate record, including a wrong claim about load-test orders (KF-7). Fixed, or settled by Luke with Claude's recommendations |
| #3 | 2 | 0.49 | Mostly the same points as run 1, already settled by the gate decisions; three gaps added (AUTH-8's test expects the full card number; no planned tests for the KF-1 setting or the KF-15 documentation) |
| #3 | 3 | 0.35 | 7 findings: ORDER-1N and ADMIN-2N contradicted each other, ADMIN-2N untestable, HOME-2N imprecise, missing planned tests, login timing, stale lines. All fixed |

Total real AI review spend: **$5.72** ($0.42 on #1, $4.03 on #2, $1.27 on #3).
