-- Spike data: shaped like DayTrader's, sized like its shipped database (500 users, 1,000 quotes),
-- with 5 holdings per user. Money is NUMERIC(14,2); quantities NUMERIC(14,4) (TRADE-7N).
DROP TABLE IF EXISTS holding, account, quote;
CREATE TABLE quote (symbol text PRIMARY KEY, company text NOT NULL, price numeric(14,2) NOT NULL, open numeric(14,2) NOT NULL);
CREATE TABLE account (user_id text PRIMARY KEY, balance numeric(14,2) NOT NULL, open_balance numeric(14,2) NOT NULL);
CREATE TABLE holding (id serial PRIMARY KEY, user_id text NOT NULL REFERENCES account, symbol text NOT NULL REFERENCES quote,
                      quantity numeric(14,4) NOT NULL, purchase_price numeric(14,2) NOT NULL);
CREATE INDEX holding_user ON holding (user_id);
INSERT INTO quote SELECT 's:' || i, 'S' || i || ' Incorporated', round((random() * 200 + 1)::numeric, 2), round((random() * 200 + 1)::numeric, 2) FROM generate_series(0, 999) i;
INSERT INTO account SELECT 'uid:' || i, 100000.00, 100000.00 FROM generate_series(0, 499) i;
INSERT INTO holding (user_id, symbol, quantity, purchase_price)
  SELECT 'uid:' || u, 's:' || ((u * 7 + h * 131) % 1000), (h + 1) * 10, round((random() * 200 + 1)::numeric, 2)
  FROM generate_series(0, 499) u, generate_series(0, 4) h;
ANALYZE;
