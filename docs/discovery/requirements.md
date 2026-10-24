# DayTrader 8: requirements (for the first gate)

Requirements start as a hypothesis drawn from the code. A characterisation test against the running legacy app confirms or corrects each one (`tests/characterisation/`, marked `@pytest.mark.req("<ID>")`).

**Status:** *Confirmed* = a passing characterisation test; *Corrected* = the test showed the code-reading was wrong, and the requirement now says what the app does; *By hand* = checked against the running app by hand, because an automated test would destroy the data other tests use; *Gate* = a requirement for the new slice that depends on a gate decision.

Behaviour that looks wrong is described as it is, with a link to `keep-or-fix.md`. The gate decides whether the new slice keeps it.

## Scope (decided at the gate, 24 October 2026)

Luke accepted every suggestion.

| # | Question | Decision (Claude's suggestion, accepted) |
|---|---|---|
| S1 | Which web interface does the new slice replace: JSP, JSF, or both? | One new web UI meeting the trader requirements; both old UIs have the same behaviour |
| S2 | Keep the three runtime modes and three order-processing modes? | No: they are alternative implementations for benchmarking. Keep the behaviour of the default (EJB3, synchronous) |
| S3 | Keep the benchmark primitives (`/servlet/Ping*`, `/ejb3/*`)? | No: they test Java EE features, not trading. Record them as dropped |
| S4 | Keep the REST quotes API and the market-summary WebSocket? | Yes: they're the public interface for client software |
| S5 | Keep the JMeter workload as the performance baseline? | Yes, as non-functional requirements (NFR-1) |
| S6 | Keep the scenario servlet (`/scenario`), a load driver that acts as random users? | Only if NFR-1 needs it; DayTrader's own JMeter scripts don't use it |

## Features in the manual, and their requirements

The 13 features counted in `docs/estimation.md` (F), from the app's documentation. Every feature has at least one requirement with a test.

| Feature | Requirements |
|---|---|
| Register | AUTH-1, AUTH-2, AUTH-4, AUTH-5 |
| Login | AUTH-3, AUTH-6, AUTH-7, AUTH-9 |
| Logout | AUTH-6, AUTH-12 |
| Home (with market summary) | HOME-1, HOME-2, HOME-3, MARKET-1, MARKET-2 |
| Account | AUTH-11, ORDER-1 |
| Account update | AUTH-8, AUTH-10 |
| Portfolio | PORT-1, TRADE-2 |
| Quotes | QUOTE-1 to QUOTE-4, PRICE-1 to PRICE-3 |
| Buy | TRADE-1 to TRADE-3, TRADE-6, TRADE-7 |
| Sell | TRADE-4, TRADE-5 |
| Change configuration | ADMIN-1, ADMIN-3 |
| Reset DayTrader | ADMIN-2, ADMIN-4 |
| Scenario servlet | SCEN-1 |

## Accounts and login (states T1–T3, T8, T9)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| AUTH-1 | Registering with matching passwords creates an account with the given opening balance as both cash and opening balance, and logs the user in | Medium | `TradeServletAction.doRegister` | `test_registration_logs_the_new_user_in_with_the_opening_balance` | Confirmed |
| AUTH-2 | Registration fails, with "passwords did not match", when the two passwords differ or are empty | Medium | same | `test_registration_fails_when_the_passwords_differ`, `…_when_the_password_is_empty` | Confirmed |
| AUTH-3 | A wrong password does not log in; the response is HTTP 500 (KF-3) | Medium | `AccountDataBean.login` | `test_a_wrong_password_is_a_server_error` | Corrected |
| AUTH-4 | Any opening balance is accepted, including negative (KF-2) | Medium | `doRegister` | `test_registration_accepts_a_negative_opening_balance` | Confirmed |
| AUTH-5 | Registering an existing user ID fails with "Registration operation failed" | Medium | `TradeSLSBBean.register` | `test_registering_an_existing_user_id_fails` | Confirmed |
| AUTH-6 | Login and logout are counted on the account; registration counts as the first login | Low | `AccountDataBean` | `test_login_and_logout_are_counted` | Confirmed |
| AUTH-7 | Pages other than welcome, login and register need a session; without one the welcome page shows "User Not Logged in". Tested for home, account, portfolio, quotes, buy, sell and profile update | Medium | `TradeAppServlet` | `test_pages_after_login_need_a_session` | Confirmed |
| AUTH-8 | A user can update password, name, address, card and email (all five checked); the new password works at the next login | Medium | `doAccountUpdate` | `test_profile_update_changes_the_profile_and_the_password` | Confirmed |
| AUTH-9 | An unknown user ID is an HTTP 500, like a wrong password (KF-3) | Medium | `TradeSLSBBean.login` | `test_an_unknown_user_id_is_a_server_error` | Confirmed |
| AUTH-10 | A profile update whose two passwords differ changes nothing | Medium | `doAccountUpdate` | `test_profile_update_with_unmatched_passwords_changes_nothing` | Confirmed |
| AUTH-11 | The account page's profile form contains the stored password and full card number (KF-3) | **High** | `account.jsp` | `test_the_account_page_shows_the_stored_password_and_card_number` | Confirmed |
| AUTH-12 | Logout ends the session | Medium | `doLogout` | `test_logout_ends_the_session` | Confirmed |

## Quotes and market (states T4, T10)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| QUOTE-1 | `GET /rest/quotes/{symbol}` returns a JSON list with symbol, company, price, open, low, high, change and volume; prices have 2 decimal places and are JSON numbers (KF-4) | Low | `QuoteResource` | `test_quotes_api_returns_prices_with_two_decimal_places` | Confirmed |
| QUOTE-2 | Several symbols (comma-separated, by GET or POST, both tested) return several quotes in order; an unknown symbol returns `null` in its place with HTTP 200 (KF-8) | Low | `QuoteResource` | `test_the_quotes_api_returns_null_for_an_unknown_symbol` | Confirmed |
| QUOTE-3 | The quotes page shows each symbol with its company, volume, price range, open, current price and change; the gain percentage follows HOME-2 | Low | `quote.jsp` | `test_the_quotes_page_shows_each_symbol_with_its_price` | Confirmed |
| QUOTE-4 | A quote's low and high stay at the opening price, however the price moves (KF-14) | Low | `updateQuotePriceVolume` | `test_low_and_high_never_move_from_the_opening_price` | Corrected (the glossary says the session's low and high) |
| MARKET-1 | The market index (TSIA) is the mean price of every stock, rounded to 2 places (half-up in the code; the test can't produce a tie to tell half-up from half-even). It's recalculated at most every 20 seconds (from the code, `marketSummaryInterval`) (KF-15) | Low | `MarketSummarySingleton` | `test_the_market_index_is_the_mean_price_of_every_stock` | Corrected (the glossary says the top 20 stocks) |
| MARKET-2 | The top 5 gainers and losers are the stocks with the largest rise and fall from their opening price, in money, not percent. Total volume is sent as a binary float, e.g. 244711.84999999998 (KF-4) | Low | same | `test_top_gainers_and_losers_are_ranked_by_change_in_price` | Confirmed (total volume: by hand) |

## Trading (states T5–T7): highest risk

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| TRADE-1 | A buy debits quantity × current price + 24.95 from cash, with the order closed immediately | **High** | `TradeSLSBBean.buy`, `TradeConfig.orderFee` | `test_buy_debits_quantity_times_price_plus_the_fee` | Confirmed |
| TRADE-2 | A completed buy creates one holding at the price quoted just before the buy | **High** | `completeOrder` | `test_buy_creates_one_holding`, `test_a_holding_records_the_price_before_the_buy` | Confirmed |
| TRADE-3 | A buy is not checked against the cash balance, which can go negative (KF-1) | **High** | `buy` | `test_buy_is_allowed_beyond_the_cash_balance` | Confirmed |
| TRADE-4 | A sell credits the holding's quantity × current price − 24.95 and removes the holding | **High** | `sell`, `completeOrder` | `test_sell_credits_quantity_times_price_minus_the_fee` | Confirmed |
| TRADE-5 | Selling a holding that's already sold moves no money; the user sees HTTP 500 (KF-5) | **High** | `sell` | `test_selling_a_holding_twice_fails_without_crediting_twice` | Corrected |
| TRADE-6 | Fractional and exponent quantities (0.1, 2.5, 1e3) are accepted; negative, zero, empty and non-numeric quantities are an HTTP 500 and move no money (KF-16) | **High** | `doBuy` | `test_fractional_and_exponent_quantities_are_accepted`, `test_an_invalid_quantity_is_a_server_error_and_moves_no_money` | Corrected (the outcome for invalid input was unknown) |
| TRADE-7 | A fractional trade uses the quantity as a binary double, and the new balance is truncated **toward zero** to 2 places. With a positive balance the trader pays up to a cent more and receives up to a cent less: 0.1 share at 10.00 costs 25.96, not 25.95. With a negative balance the same trade costs 25.95 (KF-12) | **High** | `buy`, `sell` (`new BigDecimal(double)`), `BALANCE DECIMAL(14,2)` | `test_a_fractional_purchase_is_truncated_toward_zero`, `test_a_fractional_sale_is_truncated_toward_zero_too`, `test_buying_a_tenth_of_a_share_at_10_00_costs_a_cent_extra`, `test_with_a_negative_balance_the_same_trade_costs_the_exact_amount` | Corrected (part 2's first version said "never less than the exact cost") |
| PRICE-1 | Each completed trade multiplies the stock's price by a random factor from 0.90 to 1.10 (2 decimal places), rounded half-up to 2 places; volume rises by the quantity | Medium | `updateQuotePriceVolume`, `getRandomPriceChangeFactor` | `test_a_trade_moves_the_price_by_at_most_ten_percent`, `test_a_trade_adds_its_quantity_to_the_volume` | Confirmed |
| PRICE-2 | A stock at exactly 0.01 is multiplied by 600 on its next trade | Medium | same | `test_a_penny_stock_is_multiplied_by_600_on_the_next_trade` (fixtures image) | Confirmed |
| PRICE-3 | A stock above 400 is halved on its next trade | Medium | same | `test_a_stock_above_400_is_halved_on_the_next_trade` (fixtures image) | Confirmed |
| ORDER-1 | After an order completes, the next page shows it once in an order alert; it's then deleted, so order history is always empty (KF-7). Deleted, not hidden: it stays missing after long run is turned off, while a new order is counted | **High** | `getClosedOrders`, `longRun` | `test_a_completed_order_is_shown_once_as_an_alert_then_deleted`, `test_the_order_alert_deletes_the_order_rather_than_hiding_it` | Confirmed |
| HOME-1 | The home page values holdings at purchase cost, not market value, so its "current gain" only reflects fees (KF-11) | **High** | `tradehome.jsp`, `FinancialUtils.computeHoldingsTotal` | `test_home_page_values_holdings_at_purchase_cost` | Corrected (the glossary says current value) |
| HOME-2 | Gain percentages are rounded to whole percent but shown with 2 decimal places (KF-10). The ratio is rounded half-up in the code; the tests can't produce a tie | Medium | `FinancialUtils.computeGainPercent` | `test_gain_percentages_are_rounded_to_whole_percent` | Corrected (the requirement said "rounded half-up, 2 decimal places") |
| HOME-3 | If any holding's purchase price × quantity has more than 2 decimal places, with the quantity taken as a binary double, the home page is an HTTP 500 (KF-13). That covers every holding of 0.1 shares, and 2.5 shares at an odd number of cents but not an even one (all three tested) | **High** | `computeHoldingsTotal` (`setScale` with no rounding mode) | `test_a_holding_worth_more_than_two_decimal_places_breaks_the_home_page`, `test_home_page_works_for_2_5_shares_at_an_even_number_of_cents`, `test_home_page_breaks_for_2_5_shares_at_an_odd_number_of_cents` (fixtures image) | Confirmed (predicted from the code) |
| PORT-1 | The portfolio values each holding at the current price: basis, market value, gain, and totals with a gain percentage (computed as HOME-2) | Medium | `portfolio.jsp`, `FinancialUtils` | `test_portfolio_values_each_holding_at_the_current_price` | Confirmed |

The account page has no gain figure. ACCT-1, which said it had, was wrong and is withdrawn (`agent-errors.md`); the gain is on the home page (HOME-1, HOME-2).

## Operator (states O1–O3)

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| ADMIN-1 | `/config` is reachable without logging in (KF-6) | **High** | `server.xml` (no `appSecurity` feature), `web.xml` | `test_the_admin_page_needs_no_login` | Confirmed |
| ADMIN-2 | Reset removes users whose IDs start `ru:`, and sets the seeded `uid:` users' login and logout counts to 0. It also deletes those users' orders and holdings: that part is from the code, because they can't be seen once the user is gone | High | `TradeDirectDBUtils.resetTrade` | `test_reset_removes_ru_users_and_zeroes_seeded_login_counts` | Confirmed (orders and holdings: from the code) |
| ADMIN-3 | A configuration update sets every checkbox setting it doesn't include to off: long run, order alerts and the price streamer, all checked (KF-17) | High | `TradeConfigServlet.doConfigUpdate` | `test_a_config_update_turns_off_every_setting_it_omits` | Confirmed |
| ADMIN-4 | Rebuilding the database replaces all data with MAX_USERS users and MAX_QUOTES quotes (1,000 and 500 in this image), taking about 40 seconds | High | `TradeDirectDBUtils.buildDB` | – | By hand, 24 October 2026 |
| SCEN-1 | The scenario servlet acts as a random user from `uid:0` to MAX_USERS − 1; with the shipped database, users from `uid:500` don't exist, so many requests are an HTTP 500 (KF-9) | Low | `TradeScenarioServlet` | `test_the_scenario_servlet_fails_for_users_missing_from_the_database` | Confirmed |

## Non-functional

| ID | Requirement | Source | Status |
|---|---|---|---|
| NFR-1 | Throughput and response times under the JMeter workload `daytrader8.jmx` no worse than the legacy app's baseline on the same machine | `jmeter_files/`, `perf/` | Baseline measured: `perf/baseline.md` |
| NFR-2 | Money is exact decimal, rounded half-up to 2 places, never binary floating point | here | Required: KF-4 and KF-12 fixed (Luke, 24 October 2026) |
| NFR-3 | Runs locally in containers from one command | here | Confirmed for the legacy app |

## Coverage

47 tests (61 test cases with parameters) confirm or correct 37 of the 38 functional requirements. ADMIN-4 is checked by hand. One more test checks the harness itself. Of the non-functional requirements, NFR-1 has a measured baseline, NFR-3 is met by the set-up, and NFR-2 is required by the gate.

## Requirements for the new slice (gate, 24 October 2026)

These are what Planning and Execution build and test against. Where the gate fixed a legacy behaviour, the new slice's requirement has its own ID ending in N, so a reversed behaviour never shares an ID with the legacy one. Every requirement not listed here applies to the new slice unchanged, with its characterisation test.

Each N requirement has a planned test. "Changed" means the characterisation test runs against the new slice with its expected result changed to this one; "new" means a test the legacy app can't have.

| ID | Requirement | From | Planned test |
|---|---|---|---|
| MONEY-1N | Money and quantities are exact decimals everywhere, never binary floating point. Money is rounded half-up to 2 places at the points the requirements name (TRADE-7N, HOME-1N, HOME-2N), never truncated. The JSON API keeps the legacy field names and writes money with exactly 2 decimal places, keeping trailing zeros (25.90, 52.00): every amount is rounded to 2 places before it's encoded, never left at whatever precision it has. Volumes and quantities are written as exact decimals, never through a float. `NaN` and `Infinity` are never written (inputs reject them: TRADE-6N, AUTH-4N) | KF-4, NFR-2 | New: every number in every JSON response parses as an exact decimal with the expected places. New: a unit test for each named rounding point with half-up ties (e.g. 0.005). New: a check in CI that money code never uses `float` |
| TRADE-7N | A quantity is a decimal above 0, at most 1,000,000, with at most 4 decimal places. Trade value = quantity × price, rounded half-up to 2 places; a buy debits value + fee, a sell credits value − fee. 0.1 share at 10.00 costs 25.95 | KF-12 | Changed: the TRADE-7 tests, including the seeded-price ones |
| TRADE-6N | A quantity outside TRADE-7N's rule, or that isn't a number (including `NaN` and `Infinity`), gets a message on the trade page; no money moves | KF-16 | Changed: the TRADE-6 tests, plus `NaN`, `Infinity`, too many places and too large |
| TRADE-3N | A buy costing more than the cash balance is rejected with a message; no money moves. A load-test setting, off by default, allows it if NFR-1 needs it | KF-1 | Changed: TRADE-3. New: with the load-test setting on, the same buy goes through |
| TRADE-5N | Selling a holding that's already sold gets a message; no money moves | KF-5 | Changed: TRADE-5 |
| AUTH-4N | An opening balance must be a number above 0, at most 999,999,999,999.99 (the legacy column's limit), with at most 2 decimal places; anything else gets a message | KF-2 | Changed: AUTH-4, plus `NaN`, `Infinity`, too many places and too large |
| AUTH-3N | A wrong password and an unknown user ID get the same message on the login page, never an HTTP 500. An unknown ID still runs a password-hash check, so response time doesn't reveal which IDs exist. Registration has to say when an ID is taken; whether to rate-limit login and registration is a Planning decision | KF-3 | Changed: AUTH-3, AUTH-9. New: unknown and known IDs take similar time |
| AUTH-13N | Passwords are stored hashed with a slow password hash (e.g. Argon2id). Seeded users are hashed from their seed passwords, so load-test scripts still log in | KF-3 | New: the stored value is a hash; seeded users log in |
| AUTH-14N | No secret is ever written to a log: passwords, session IDs and card numbers | KF-3 | New: failed logins, registrations and profile updates, then the logs searched for the values used |
| AUTH-11N | The account page never contains the password. Only the last 4 digits of a card are stored and shown | KF-3 | Changed: AUTH-11 (the page) and AUTH-8, whose test expects the full card number after an update. New: the stored card value, read from the database, has only the last 4 digits |
| ADMIN-1N | `/config` and every operator action need an operator login | KF-6 | Changed: ADMIN-1 |
| ADMIN-2N | Seeding marks every record it creates as seed data. The reset removes `ru:` users with their data (as ADMIN-2), and for the seeded users removes every order and holding not marked as seed data and restores their balances and login counts to the seeded values | KF-7 | Changed: ADMIN-2. New: after trading as a seeded user and resetting, that user's orders, holdings and balance equal the seed |
| ADMIN-3N | A configuration update changes only the settings it includes | KF-17 | Changed: ADMIN-3 |
| ORDER-1N | Every order is kept: trading, alerts and viewing never delete one. The only deletions are the operator's reset of test data (ADMIN-2, ADMIN-2N). The completion alert is shown once and marks the order as alerted. The account page shows the order history. The orders table is partitioned by month if it grows (the size that triggers it is a Planning decision) | KF-7 | Changed: both ORDER-1 tests |
| QUOTE-2N | A single unknown symbol is an HTTP 404; unknown symbols are left out of a list | KF-8 | Changed: QUOTE-2 |
| QUOTE-4N | A quote's low and high follow its price through the session | KF-14 | Changed: QUOTE-4 |
| SEED-1N | Users and quotes are seeded from one setting each, which the reset, the rebuild and any load driver read | KF-9 | Changed: SCEN-1 (if S6 keeps the scenario servlet), ADMIN-4 |
| HOME-1N | The home page values holdings at the current price. A holding's value is quantity × current price, rounded half-up to 2 places for its row. The total market value is the exact sum of the unrounded values, rounded half-up to 2 places once; the gain and HOME-2N's percentage use that rounded total | KF-11 | Changed: HOME-1. New: a holding whose value has more than 2 places (e.g. 0.3333 × 10.01) |
| HOME-2N | Gain percentages are (current ÷ opening − 1) × 100, with the division carried to 10 decimal places, then rounded half-up to 2 places. An opening value of 0 gives 0.00%. This applies on the home, portfolio and quotes pages (QUOTE-3) | KF-10 | Changed: HOME-2, PORT-1, QUOTE-3. New: a tie case and an opening value of 0 |
| HOME-3N | The home page works for every holding | KF-13 | Changed: HOME-3 |

Kept, with the documentation corrected: MARKET-1 (the index is the mean price of every stock, KF-15). The check is a review item, not a test: the new slice's user documentation describes the index as MARKET-1 does, and the four manual errors in `agent-errors.md` don't carry over.

Dropped, with the reason:

- **S1:** the second web interface. The JSP and JSF interfaces have the same behaviour, so the new slice has one web UI; NFR-1's script will need adapting to it.
- **S2 and S3:** the alternative runtime and order-processing modes and the benchmark primitives. They test Java EE features, not trading.
- **S6:** the scenario servlet, unless NFR-1 needs it. If it stays, SCEN-1's new-slice requirement (users seeded from one setting, KF-9) applies to it.
