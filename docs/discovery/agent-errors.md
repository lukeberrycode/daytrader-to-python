# What the agent got wrong, and how the tests caught it

Discovery was AI-assisted (Claude Code, Opus 5.5): Claude read the Java and drafted the requirements, then wrote characterisation tests and ran them against the running legacy app. This note records where the code-reading was wrong. It's the evidence for the method's second principle: requirements drawn from code are a hypothesis until the running app confirms them.

| # | Claude's reading of the code | What the running app did | Caught by |
|---|---|---|---|
| 1 | Selling an already sold holding returns a "cancelled" order (the code creates one in `TradeSLSBBean.sell`) | HTTP 500: the cancelled order fails bean validation when saved, and the transaction rolls back | TRADE-5 test failed on first run |
| 2 | A wrong password returns the welcome page with an error (the servlet has a code path that does this) | HTTP 500: the exception from `AccountDataBean.login` is rethrown as a `ServletException` before that path | AUTH-3 test failed on first run |
| 3 | Not a mistake, but missed on first reading: completed orders are deleted when shown (`getClosedOrders` with `longRun`) | Order history always empty | Found while checking an unexplained "Total Orders: 0"; now ORDER-1 |
| 4 | (Found while investigating 2) The failed-login exception message includes the stored password | The server log contains `Incorrect password--><user>:<stored password>` | Server log read by hand; KF-3 |

Both failing tests were corrected to describe what the app does, and each difference went to `keep-or-fix.md` rather than straight into the requirements.
