# What the agent got wrong, and how the tests caught it

Discovery was AI-assisted (Claude Code, Opus 5.5): Claude read the Java and drafted the requirements, then wrote characterisation tests and ran them against the running legacy app. This note records where the code-reading was wrong. It's the evidence for the method's second principle: requirements drawn from code are a hypothesis until the running app confirms them.

| # | Claude's reading of the code | What the running app did | Caught by |
|---|---|---|---|
| 1 | Selling an already sold holding returns a "cancelled" order (the code creates one in `TradeSLSBBean.sell`) | HTTP 500: the cancelled order fails bean validation when saved, and the transaction rolls back | TRADE-5 test failed on first run |
| 2 | A wrong password returns the welcome page with an error (the servlet has a code path that does this) | HTTP 500: the exception from `AccountDataBean.login` is rethrown as a `ServletException` before that path | AUTH-3 test failed on first run |
| 3 | Not a mistake, but missed on first reading: completed orders are deleted when shown (`getClosedOrders` with `longRun`) | Order history always empty | Found while checking an unexplained "Total Orders: 0"; now ORDER-1 |
| 4 | (Found while investigating 2) The failed-login exception message includes the stored password | The server log contains `Incorrect password--><user>:<stored password>` | Server log read by hand; KF-3 |

Both failing tests were corrected to describe what the app does, and each difference went to `keep-or-fix.md` rather than straight into the requirements.

## Part 2 (24 October 2026)

| # | Claude's reading | What the running app did | Caught by |
|---|---|---|---|
| 5 | The account page shows the total gain and gain percentage (ACCT-1) | It shows neither; the gain is on the home page | Reading the page while writing PORT-1 and HOME-1; ACCT-1 withdrawn |
| 6 | Gain percentages are rounded half-up to 2 decimal places | Rounded to whole percent, shown with 2 decimal places (KF-10) | A loss of $49.90 showing as "+0.00%" on the home page |
| 7 | Not a misreading, but missed in part 1: the home page values holdings at purchase cost | Its "current gain" only ever reflects fees (KF-11) | Comparing the home page with the portfolio page |
| 9 | Fractional trades are "rounded against the trader" (part 2's first version of TRADE-7) | Truncated toward zero: with a negative balance the rounding favours the trader | The AI review of the pull request questioned it; a test on the fixtures image confirmed it |
| 8 | A harness assumption: a successful login returns a page saying "Ready to Trade" (the code sets that status) | The home page doesn't show the status; three tests failed on first run | Tests failed; they now check for "Welcome <user>," |

Two predictions from the code were confirmed by tests written to check them: the home page breaks on a holding worth more than 2 decimal places (KF-13), and fractional trades lose a cent to the trader (KF-12).

The manual (the app's bundled documentation) was wrong in four places, which matters for the estimation method, because it treats the manual as the contract: TSIA is not "the top 20 stocks" (KF-15), "total of holdings" is not current value (KF-11), the "price range" is not the session's low and high (KF-14), and "long run" does more than disable a query (KF-7). In each case the running app, not the manual, is the oracle.
