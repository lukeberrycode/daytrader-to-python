# DayTrader 8: what it does

DayTrader is IBM's sample online stock-trading app, kept by the Open Liberty project as a Java EE 8 benchmark. Source: [OpenLiberty/sample.daytrader8](https://github.com/OpenLiberty/sample.daytrader8) (Apache-2.0), pinned in `legacy/daytrader8` at commit `f511802` (16 October 2025).

## For traders

A trader registers with an opening cash balance, logs in, looks up quotes, buys shares and sells holdings. Each trade costs a fixed fee of 24.95. The account page shows cash, opening balance, login counts and recent orders; the portfolio page shows holdings with their gain or loss; the market summary shows an index (TSIA), top gainers and losers and volume.

The market is simulated. Every completed trade moves that stock's price by a random factor between 0.90 and 1.10. A stock at 0.01 is multiplied by 600 (the "recovery miracle"), and one above 400 is halved (a "split").

## For operators

An unauthenticated configuration page (`/config`) sets the runtime mode, order processing mode and web interface, resets the trade data, and rebuilds the database. Settings return to defaults on restart.

## For benchmarking

About half the code is "primitives": ping servlets, JSPs, EJBs, CDI, WebSockets and JAX-RS endpoints that each exercise one Java EE feature for performance testing. They are not part of trading. JMeter scripts in `jmeter_files/` drive the trading workload.

## Not in it

No real money, no real market data, no external services. One embedded Derby database. Passwords and card numbers are stored in plain text, which is acceptable only because it's a benchmark (see `keep-or-fix.md`).
