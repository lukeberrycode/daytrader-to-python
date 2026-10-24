# DayTrader 8: data inventory

One embedded Derby database, `tradedb`, owned entirely by the app. No other system reads or writes it. Schema: `webapp/dbscripts/derby/Table.ddl` (DB2 and Oracle versions alongside).

| Table | Holds | Key | Money columns | Notes |
|---|---|---|---|---|
| `ACCOUNTPROFILEEJB` | User ID, password, full name, address, email, credit card | `USERID` | – | **Password and card number in plain text** (KF-3) |
| `ACCOUNTEJB` | Balance, opening balance, login and logout counts, created and last login | `ACCOUNTID` | `BALANCE`, `OPENBALANCE` DECIMAL(14,2) | One account per profile. Saving a balance with more than 2 decimal places truncates it (KF-12) |
| `QUOTEEJB` | Symbol, company, price, open, low, high, change, volume | `SYMBOL` | `PRICE`, `OPEN1`, `LOW`, `HIGH` DECIMAL(14,2) | `CHANGE1` and `VOLUME` are DOUBLE (KF-4). `LOW` and `HIGH` never change after seeding (KF-14) |
| `HOLDINGEJB` | Shares held: quantity, purchase price and date | `HOLDINGID` | `PURCHASEPRICE` DECIMAL(14,2) | `QUANTITY` is DOUBLE. A purchase date of 1970-01-01 marks a holding being sold |
| `ORDEREJB` | Orders: type, status, quantity, price, fee, open and completion dates | `ORDERID` | `PRICE`, `ORDERFEE` DECIMAL(14,2) | Status: open, processing, closed, completed, alertcompleted, cancelled. With the default "long run" setting, closed orders are **deleted** once shown in the order alert (KF-7) |
| `KEYGENEJB` | Next key per table | `KEYNAME` | – | Keys handed out in blocks of 1,000 |

## Volumes (prebuilt database)

- 500 users, `uid:0` to `uid:499`, all with password `xxx`, (`uid:1`, for example, opened with 275,090.00). Users created by the database rebuild get 1,000,000.
- 1,000 quotes, `s:0` to `s:999`, company names "S0 Incorporated" and so on.
- Some holdings and orders already exist (for example `uid:1` has holdings, and order IDs start at 3001).
- The image's `MAX_USERS=1000` and `MAX_QUOTES=500` settings don't match the database: they apply only when the database is rebuilt from `/config`.

## Money in code

`BigDecimal` throughout the service layer, rounded to 2 decimal places with half-up rounding (`FinancialUtils.SCALE`, `ROUND_HALF_UP`). Exceptions are listed in `keep-or-fix.md` (KF-4). The new slice uses Python's `decimal.Decimal` with `ROUND_HALF_UP` and Postgres `NUMERIC(14,2)`.

## Migration note

The data is synthetic and the database is rebuilt on demand, so the new slice can seed its own data rather than migrate Derby's. The data migration plan (Planning phase) should still show the schema mapping, because a real migration would need it.
