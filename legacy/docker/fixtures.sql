-- Test fixtures for the "fixtures" image target (legacy/docker/Dockerfile). Data only: no code changes.
-- TRADE-7, negative balance: the same round price, on its own stock.
UPDATE QUOTEEJB SET PRICE = 10.00, OPEN1 = 10.00, CHANGE1 = 0 WHERE SYMBOL = 's:994';
-- HOME-3: 2.5 shares at an even and an odd number of cents.
UPDATE QUOTEEJB SET PRICE = 10.00, OPEN1 = 10.00, CHANGE1 = 0 WHERE SYMBOL = 's:995';
UPDATE QUOTEEJB SET PRICE = 10.01, OPEN1 = 10.01, CHANGE1 = 0 WHERE SYMBOL = 's:996';
-- TRADE-7: a round price, so a fractional trade's rounding shows exactly.
UPDATE QUOTEEJB SET PRICE = 10.00, OPEN1 = 10.00, CHANGE1 = 0 WHERE SYMBOL = 's:997';
-- PRICE-2: a stock at exactly 0.01 (the penny-stock rule).
UPDATE QUOTEEJB SET PRICE = 0.01, OPEN1 = 0.01, CHANGE1 = 0 WHERE SYMBOL = 's:998';
-- PRICE-3: a stock above 400 (the split rule).
UPDATE QUOTEEJB SET PRICE = 400.01, OPEN1 = 400.01 WHERE SYMBOL = 's:999';
