# DayTrader 8: requirements (for the first gate)

Requirements start as a hypothesis drawn from the code. A characterisation test against the running legacy app confirms or corrects each one (`tests/characterisation/`, marked `@pytest.mark.req("<ID>")`).

**Status:** *Confirmed* = a passing characterisation test; *Corrected* = the test showed the code-reading was wrong, and the requirement now says what the app does; *By hand* = checked against the running app by hand, because an automated test would destroy the data other tests use; *Gate* = a requirement for the new slice that depends on a gate decision.

Behaviour that looks wrong is described as it is, with a link to `keep-or-fix.md`. The gate decides whether the new slice keeps it.

## Scope (decisions for the gate)

| # | Question | Claude's suggestion |
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
| AUTH-7 | Pages other than welcome, login and register need a session; without one the welcome page shows "User Not Logged in" | Medium | `TradeAppServlet` | `test_pages_after_login_need_a_session` | Confirmed |
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
| MARKET-2 | The top 5 gainers and losers are the stocks with the largest rise and fall from their opening price, in money, not percent. Total volume is sent as a binary float, e.g. 244711.84999999998 (seen by hand; KF-4) | Low | same | `test_top_gainers_and_losers_are_ranked_by_change_in_price` | Confirmed |

## Trading (states T5–T7): highest risk

| ID | Requirement | Risk | Source | Test | Status |
|---|---|---|---|---|---|
| TRADE-1 | A buy debits quantity × current price + 24.95 from cash, with the order closed immediately | **High** | `TradeSLSBBean.buy`, `TradeConfig.orderFee` | `test_buy_debits_quantity_times_price_plus_the_fee` | Confirmed |
| TRADE-2 | A completed buy creates one holding at the price quoted just before the buy | **High** | `completeOrder` | `test_buy_creates_one_holding`, `test_a_holding_records_the_price_before_the_buy` | Confirmed |
| TRADE-3 | A buy is not checked against the cash balance, which can go negative (KF-1) | **High** | `buy` | `test_buy_is_allowed_beyond_the_cash_balance` | Confirmed |
| TRADE-4 | A sell credits the holding's quantity × current price − 24.95 and removes the holding | **High** | `sell`, `completeOrder` | `test_sell_credits_quantity_times_price_minus_the_fee` | Confirmed |
| TRADE-5 | Selling a holding that's already sold moves no money; the user sees HTTP 500 (KF-5) | **High** | `sell` | `test_selling_a_holding_twice_fails_without_crediting_twice` | Corrected |
| TRADE-6 | Fractional and exponent quantities (0.1, 2.5, 1e3) are accepted; negative, zero, empty and non-numeric quantities are an HTTP 500 and move no money (KF-16) | **High** | `doBuy` | `test_fractional_and_exponent_quantities_are_accepted`, `test_an_invalid_quantity_is_a_server_error_and_moves_no_money` | Corrected (the outcome for invalid input was unknown) |
| TRADE-7 | A fractional trade uses the quantity as a binary double, and the new balance is truncated **toward zero** to 2 places. With a positive balance the trader pays up to a cent more and receives up to a cent less: 0.1 share at 10.00 costs 25.96, not 25.95. With a negative balance the same trade costs 25.95 (KF-12) | **High** | `buy`, `sell` (`new BigDecimal(double)`), `BALANCE DECIMAL(14,2)` | `test_a_fractional_trade_is_rounded_against_the_trader`, `test_a_fractional_sale_is_truncated_toward_zero_too`, `test_buying_a_tenth_of_a_share_at_10_00_costs_a_cent_extra`, `test_with_a_negative_balance_the_same_trade_costs_the_exact_amount` | Corrected (part 2's first version said "never less than the exact cost") |
| PRICE-1 | Each completed trade multiplies the stock's price by a random factor from 0.90 to 1.10 (2 decimal places), rounded half-up to 2 places; volume rises by the quantity | Medium | `updateQuotePriceVolume`, `getRandomPriceChangeFactor` | `test_a_trade_moves_the_price_by_at_most_ten_percent`, `test_a_trade_adds_its_quantity_to_the_volume` | Confirmed |
| PRICE-2 | A stock at exactly 0.01 is multiplied by 600 on its next trade | Medium | same | `test_a_penny_stock_is_multiplied_by_600_on_the_next_trade` (fixtures image) | Confirmed |
| PRICE-3 | A stock above 400 is halved on its next trade | Medium | same | `test_a_stock_above_400_is_halved_on_the_next_trade` (fixtures image) | Confirmed |
| ORDER-1 | After an order completes, the next page shows it once in an order alert; it's then deleted, so order history is always empty (KF-7) | **High** | `getClosedOrders`, `longRun` | `test_a_completed_order_is_shown_once_as_an_alert_then_deleted` | Confirmed |
| HOME-1 | The home page values holdings at purchase cost, not market value, so its "current gain" only reflects fees (KF-11) | **High** | `tradehome.jsp`, `FinancialUtils.computeHoldingsTotal` | `test_home_page_values_holdings_at_purchase_cost` | Corrected (the glossary says current value) |
| HOME-2 | Gain percentages are rounded to whole percent but shown with 2 decimal places (KF-10). The ratio is rounded half-up in the code; the tests can't produce a tie | Medium | `FinancialUtils.computeGainPercent` | `test_gain_percentages_are_rounded_to_whole_percent` | Corrected (the requirement said "rounded half-up, 2 decimal places") |
| HOME-3 | If any holding's purchase price × quantity has more than 2 decimal places, with the quantity taken as a binary double, the home page is an HTTP 500 (KF-13). That covers every holding of 0.1 shares, and 2.5 shares at an odd number of cents but not an even one (all three tested) | **High** | `computeHoldingsTotal` (`setScale` with no rounding mode) | `test_a_holding_worth_more_than_two_decimal_places_breaks_the_home_page` | Confirmed (predicted from the code) |
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
| NFR-2 | Money is exact decimal, rounded half-up to 2 places, never binary floating point | here | Gate: the legacy app doesn't do this for fractional quantities (TRADE-7), so NFR-2 depends on KF-4 and KF-12 |
| NFR-3 | Runs locally in containers from one command | here | Confirmed for the legacy app |

## Coverage

46 tests (54 test cases with parameters) confirm or correct 37 of the 38 functional requirements. ADMIN-4 is checked by hand. One more test checks the harness itself. Of the non-functional requirements, NFR-1 has a measured baseline, NFR-3 is met by the set-up, and NFR-2 waits on the gate.
