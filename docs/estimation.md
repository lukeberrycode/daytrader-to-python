# Estimation

How the no-AI estimates in `timings.md` are made, so anyone can check them. The method matters as much as the figure it produces.

## What is estimated, and against what

- **Two estimates:** one per phase, made before that phase starts (except Discovery: see "Anchoring"); and one for the whole migration, made before Planning starts.
- **The counterfactual:** one experienced engineer, new to the DayTrader codebase, working without AI, to the same standard as this repository: the same Discovery documents, characterisation tests, keep-or-fix decisions, gates, RFC, data migration, cut-over and decommissioning. Without the last condition the comparison favours AI, because a typical no-AI migration would skip much of that.
- **What it's compared with:** Luke's hands-on hours with AI (reviews, gate decisions, corrections), with agent time and API cost alongside. Not agent time alone.
- **How it's reported:** estimated against measured, for one migration. Never as "X times faster" in general.

## Principles (Luke, 23 October 2026)

1. **Engineers' own estimates are notoriously inaccurate**, so estimates here come from a stated formula with published or stated inputs, not from anyone's judgement of the whole task.
2. **Estimates depend on understanding the task and the project intimately.** The agent understands DayTrader better than Luke does at this point, so it applies the formula and counts the inputs; Luke sets the formula and the per-feature times.
3. **Estimates are based on the user manual, not the size of the codebase.** The user manual is where the contract between the product and its user comes from: "if you do this, I will do that". Each function it describes is a high-level requirement.

## Discovery phase

### The method

Discovery has four parts, for an engineer working without AI:

1. **Read the user manual.** Each feature it describes is read once and becomes a high-level requirement. High-level discovery is then complete for that requirement. The one-pager (`discovery/one-pager.md`) is a précis of the manual.
2. **Play through each feature in the old slice**, as a user, several times, to pick up as much detail as possible.
3. **Find and read all the code** that implements the features, to check that understanding and pick up the edge cases. Assuming there is no dead code, every line has to be read. The code could be divided between the features, but it all adds up to the whole codebase, so this part is sized by the total lines of code and a reading rate, not per feature.
4. **Write up each feature:** the Discovery artefacts the counterfactual requires, per feature: its states, journeys and requirements, the characterisation tests that confirm them, and the keep-or-fix entries for anything odd.

The estimate is:

> **Discovery = L + F × (U + P + W)**

| Term | Meaning |
|---|---|
| L | Time for a person to read the whole codebase once |
| F | Number of identifiable features (or user stories) in the published user manual |
| U | Time for a person to read the part of the manual describing one feature |
| P | Time for a person to play through one feature in the old slice |
| W | Time for a person to write up one feature: requirements, characterisation tests and keep-or-fix entries |

Each term has an optimistic (O), most likely (M) and pessimistic (P) value. The three totals are combined with the PERT formula, (O + 4M + P) / 6.

### Inputs for DayTrader 8

**F = 13 features.** DayTrader's published manual is its bundled documentation (`legacy/daytrader8/src/main/webapp/docs/`):

- `rtCharacterisitics.html` lists 10 "high level user operations": Login, Logout, Register, Home (including the market summary), Account, Account Update, Portfolio, Quotes, Buy, Sell.
- `tradeFAQ.html` describes 3 operator features: changing the runtime configuration, Reset DayTrader, and the TradeScenario servlet that drives benchmark load.

Not counted: the web primitives, described in the manual as a suite of benchmark tests for application server features rather than functions of the trading app (scope decision S3). If the gate keeps them, each primitive becomes a feature and F rises.

**L: 28,522 lines.** Every non-blank line in `src/main` and `pom.xml`, in all languages: Java 16,779; JSP 4,663; XHTML 3,619; HTML 1,617; XML 1,061; SQL 430; CSS 296; properties 57. Blank lines take no reading time; comments do, so they're included. The documentation pages are excluded, because reading them is U.

**Reading rate for L.** The SmartBear study of code review at Cisco (2006) found reviewers are effective at up to 300 to 500 lines an hour, and miss more above that. That range gives O = 500 lines an hour, M = 400 (the midpoint), P = 300.

**U, P and W (Luke):**

| | O | M | P |
|---|---|---|---|
| U: read one feature in the manual | 1 min | 5 min | 8 min |
| P: play through one feature | 5 min | 20 min | 30 min |
| W: write up one feature | 2 h | 3 h | 5 h |

### Calculation

| | O | M | P |
|---|---|---|---|
| L = 28,522 lines ÷ rate | ÷ 500 = 57.0 h | ÷ 400 = 71.3 h | ÷ 300 = 95.1 h |
| F × (U + P) = 13 × | 6 min = 1.3 h | 25 min = 5.4 h | 38 min = 8.2 h |
| F × W = 13 × | 2 h = 26.0 h | 3 h = 39.0 h | 5 h = 65.0 h |
| **Total** | **84.3 h** | **115.7 h** | **168.3 h** |

**PERT estimate: (84.3 + 4 × 115.7 + 168.3) / 6 = 119.3 hours**, with a standard deviation of (168.3 − 84.3) / 6 = 14.0 hours. That's about 3.2 weeks at 37.5 hours a week.

## Later phases

Each later phase gets its own method, agreed before the phase starts and recorded here, in the same spirit: a stated formula with countable inputs.

## Whole migration

Not yet estimated. Function points are one candidate: they size the software by its user functions, consistent with principle 3.

### Function points (IFPUG)

Function point analysis sizes software by what it does for its users, not by its code (IFPUG Counting Practices Manual; ISO/IEC 20926). That suits a method built on "requirements, not code", and the size doesn't depend on Java being wordier than Python.

The count below is unadjusted, made by Claude from the code and the running app on 23 October 2026, not by a certified counter. It covers trading and operator functions only. The benchmark primitives are left out (scope decision S3). Standard IFPUG weights: data files 7/10/15 (low/average/high); inputs 3/4/6; outputs 4/5/7; enquiries 3/4/6.

| Type | Function | Complexity | FP |
|---|---|---|---|
| Data (ILF) | Account (account and profile: 2 record types) | Low | 7 |
| Data (ILF) | Quote | Low | 7 |
| Data (ILF) | Holding | Low | 7 |
| Data (ILF) | Order | Low | 7 |
| Input | Register | Low | 3 |
| Input | Log in | Low | 3 |
| Input | Log out | Low | 3 |
| Input | Buy (references account, quote, order, holding) | High | 6 |
| Input | Sell (same) | High | 6 |
| Input | Update profile | Low | 3 |
| Input | Change configuration | Low | 3 |
| Input | Reset trade data | Average | 4 |
| Input | Rebuild database | Average | 4 |
| Output | Home (cash, holdings total, gain, gain %) | High | 7 |
| Output | Portfolio (market values, gains, totals) | High | 7 |
| Output | Account (account, profile, recent orders) | Average | 5 |
| Output | Order confirmation and order alert (deletes orders, KF-7) | Average | 5 |
| Output | Market summary (TSIA, gainers, losers, volume) | Average | 5 |
| Output | Market summary WebSocket | Low | 4 |
| Output | Quote price change events (SSE, `/rest/broadcastevents`) | Low | 4 |
| Output | Runtime statistics | Low | 4 |
| Enquiry | Quotes page | Low | 3 |
| Enquiry | Quotes REST API (GET and POST share one process) | Low | 3 |
| Enquiry | View configuration | Low | 3 |
| **Total** | | | **113** |

The key-generation table and the in-memory settings aren't counted: users can't see them as data. Judgement calls on complexity move the total by roughly ±10, so treat the size as **100 to 125 function points**.

**Effort.** The ISBSG benchmarking paper (2024) gives the delivery rate for 344 Java projects (IFPUG or Nesma counts, after 2015, 300 to 3,000 function points). Its effort covers planning, requirements, design, build, test and implementation, which roughly matches this method's phases.

| ISBSG percentile | Hours per FP | × 113 FP | Weeks at 37.5 hours |
|---|---|---|---|
| 25th | 5.2 | 588 | 16 |
| Median | 6.7 | 757 | 20 |
| 75th | 8.2 | 927 | 25 |
| 90th | 9.9 | 1,119 | 30 |

ISBSG's productivity page also gives "around 8 hours per functional size unit" as typical for Java.

Limits, stated so the figure isn't over-read:

- DayTrader, at about 113 function points, is smaller than the 300 to 3,000 in that peer group.
- ISBSG publishes no comparable figure for Python; Java is used as the nearest.
- The figures are for development, not migration. A running reference app removes some requirements work, but characterisation tests, parity checks, data migration and cut-over add work. The estimate treats the two as roughly cancelling out, which is a judgement, not a measurement.

## Anchoring

The Discovery estimate was made after part 1 had been done with AI. The formula is mechanical, and its inputs are counted or taken from published figures, which limits how much that can bias it, but U, P and W were set afterwards. No independent estimator was available.

## Sources

- DayTrader 8 bundled documentation: `src/main/webapp/docs/rtCharacterisitics.html`, `tradeFAQ.html`.
- SmartBear, *Best Kept Secrets of Peer Code Review* (2006), Cisco study.
- IFPUG, Function Point Counting Practices Manual; ISO/IEC 20926:2009.
- ISBSG, [Benchmarking Application Development Projects/Teams](https://www.isbsg.org/wp-content/uploads/2024/05/Short-Paper-2024-01-Benchmarking-Application-Development-Teams.pdf) (short paper, 2024), Table 1.
- ISBSG, [Resources: Productivity](https://www.isbsg.org/resources-productivity/).
