# DayTrader 8: requirements (draft for the first gate)

Requirements start as a hypothesis drawn from the code. A characterisation test against the running legacy app confirms or corrects each one (`tests/characterisation/`, marked `@pytest.mark.req("<ID>")`).

**Status:** *Confirmed* = a passing characterisation test; *Corrected* = the test showed the code-reading was wrong, and the requirement now says what the app does; *Hypothesis* = from the code, no test yet.

Behaviour that looks wrong is described as it is, with a link to `keep-or-fix.md`. The gate decides whether the new slice keeps it.

## Scope (decisions for the gate)

| # | Question | Claude's suggestion |
|---|---|---|
| S1 | Which web interface does the new slice replace: JSP, JSF, or both? | One new web UI meeting the trader requirements; both old UIs have the same behaviour |
| S2 | Keep the three runtime modes and three order-processing modes? | No: they are alternative implementations for benchmarking. Keep the behaviour of the default (EJB3, synchronous) |
| S3 | Keep the benchmark primitives (`/servlet/Ping*`, `/ejb3/*`)? | No: they test Java EE features, not trading. Record them as dropped |
| S4 | Keep the REST quotes API and the market-summary WebSocket? | Yes: they're the public interface for client software |
| S5 | Keep the JMeter workload as the performance baseline? | Yes, as non-functional requirements (NFR-1) |

## Accounts and login (states T1–T3, T8, T9)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| AUTH-1 | Registering with matching passwords creates an account with the given opening balance as both cash and opening balance, and logs the user in | Medium | `TradeServletAction.doRegister` | `test_registration_logs_the_new_user_in_with_the_opening_balance` | Confirmed |
| AUTH-2 | Registration fails, with "passwords did not match", when the two passwords differ or are empty | Medium | same | `test_registration_fails_when_the_passwords_differ` | Confirmed (empty: hypothesis) |
| AUTH-3 | A wrong password does not log in; the response is HTTP 500 (KF-3) | Medium | `AccountDataBean.login` | `test_a_wrong_password_is_a_server_error` | Corrected |
| AUTH-4 | Any opening balance is accepted, including negative (KF-2) | Medium | `doRegister` | `test_registration_accepts_a_negative_opening_balance` | Confirmed |
| AUTH-5 | Registering an existing user ID fails with "Registration operation failed" | Medium | `TradeSLSBBean.register` | – | Hypothesis |
| AUTH-6 | Login increments the login count and sets last login; logout increments the logout count | Low | `AccountDataBean` | – | Hypothesis |
| AUTH-7 | Pages other than welcome, login and register need a session; without one the welcome page shows "User Not Logged in" | Medium | `TradeAppServlet` | – | Hypothesis |
| AUTH-8 | A user can update password, name, address, card and email; the password change needs matching confirmation | Medium | `doAccountUpdate` | – | Hypothesis |

## Quotes and market (states T4, T10)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| QUOTE-1 | `GET /rest/quotes/{symbol}` returns a JSON list with symbol, company, price, open, low, high, change and volume; prices have 2 decimal places and are JSON numbers (KF-4) | Low | `QuoteResource` | `test_quotes_api_returns_prices_with_two_decimal_places` | Confirmed |
| QUOTE-2 | Several symbols separated by commas return several quotes; an unknown symbol returns `[null]` with HTTP 200 (KF-8) | Low | `QuoteResource` | – | Observed by hand |
| MARKET-1 | Market summary: TSIA (average price), opening TSIA, volume, top 5 gainers and losers | Low | `MarketSummarySingleton` | – | Hypothesis |

## Trading (states T5–T7): highest risk

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| TRADE-1 | A buy debits quantity × current price + 24.95 from cash, with the order closed immediately | **High** | `TradeSLSBBean.buy`, `TradeConfig.orderFee` | `test_buy_debits_quantity_times_price_plus_the_fee` | Confirmed |
| TRADE-2 | A completed buy creates one holding at the order's price | **High** | `completeOrder` | `test_buy_creates_one_holding` | Confirmed (price: hypothesis) |
| TRADE-3 | A buy is not checked against the cash balance, which can go negative (KF-1) | **High** | `buy` | `test_buy_is_allowed_beyond_the_cash_balance` | Confirmed |
| TRADE-4 | A sell credits the holding's quantity × current price − 24.95 and removes the holding | **High** | `sell`, `completeOrder` | `test_sell_credits_quantity_times_price_minus_the_fee` | Confirmed |
| TRADE-5 | Selling a holding that's already sold moves no money; the user sees HTTP 500 (KF-5) | **High** | `sell` | `test_selling_a_holding_twice_fails_without_crediting_twice` | Corrected |
| TRADE-6 | Quantities are decimal (stored as DOUBLE) and shown with one decimal place, e.g. "3.0"; non-numeric or negative quantities: behaviour unknown | **High** | `doBuy` | – | Hypothesis |
| PRICE-1 | Each completed trade multiplies the stock's price by a random factor from 0.90 to 1.10 (2 decimal places), rounded half-up to 2 decimal places; volume rises by the quantity | Medium | `updateQuotePriceVolume`, `getRandomPriceChangeFactor` | `test_a_trade_moves_the_price_by_at_most_ten_percent` | Confirmed (volume: hypothesis) |
| PRICE-2 | A stock at exactly 0.01 is multiplied by 600 instead | Medium | same | – | Hypothesis |
| PRICE-3 | A stock above 400 is halved instead | Medium | same | – | Hypothesis |
| ORDER-1 | After an order completes, the next page shows it once in an order alert; it's then deleted, so order history is always empty (KF-7) | **High** | `getClosedOrders`, `longRun` | `test_a_completed_order_is_shown_once_as_an_alert_then_deleted` | Confirmed |
| PORT-1 | Portfolio shows each holding with purchase price, current price, market value and gain, plus totals | Medium | `portfolio.jsp`, `FinancialUtils` | – | Hypothesis |
| ACCT-1 | Account page shows cash balance, opening balance, total gain and gain percentage (rounded half-up, 2 decimal places) | Medium | `FinancialUtils.computeGain*` | – | Hypothesis |

## Operator (states O1–O3)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| ADMIN-1 | `/config` is reachable without logging in (KF-6) | **High** | `server.xml` (no `appSecurity` feature), `web.xml` | `test_the_admin_page_needs_no_login` | Confirmed |
| ADMIN-2 | An operator can reset trade data and rebuild the database with N users and M quotes | High | `TradeConfigServlet` | – | Hypothesis |

## Non-functional

| ID | Requirement | Source | Status |
|---|---|---|---|
| NFR-1 | Throughput and response times under the JMeter workload `daytrader8.jmx` no worse than the legacy app on the same machine | `jmeter_files/` | Hypothesis: baseline not yet measured |
| NFR-2 | Money is exact decimal, rounded half-up to 2 places, never binary floating point | `FinancialUtils`, DDL | Hypothesis |
| NFR-3 | Runs locally in containers from one command | here | Confirmed for the legacy app |

## Coverage so far

13 characterisation tests confirm or correct 13 requirements. QUOTE-2 is confirmed by hand and NFR-3 by the set-up; 13 are still hypotheses. The high-risk trading rows come first in the next round of tests.
