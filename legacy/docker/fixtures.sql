-- Test fixtures for the "fixtures" image target (legacy/docker/Dockerfile). Data only: no code changes.
-- PRICE-2: a stock at exactly 0.01 (the penny-stock rule).
UPDATE QUOTEEJB SET PRICE = 0.01, OPEN1 = 0.01, CHANGE1 = 0 WHERE SYMBOL = 's:998';
-- PRICE-3: a stock above 400 (the split rule).
UPDATE QUOTEEJB SET PRICE = 400.01, OPEN1 = 400.01 WHERE SYMBOL = 's:999';
