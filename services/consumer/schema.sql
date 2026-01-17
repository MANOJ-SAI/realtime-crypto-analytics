
CREATE TABLE IF NOT EXISTS prices (
  ts_epoch_ms BIGINT NOT NULL,
  ts_iso TEXT,
  coin_id TEXT NOT NULL,
  symbol TEXT,
  name TEXT,
  vs_currency TEXT NOT NULL,
  current_price DOUBLE PRECISION,
  market_cap DOUBLE PRECISION,
  total_volume DOUBLE PRECISION,
  high_24h DOUBLE PRECISION,
  low_24h DOUBLE PRECISION,
  pct_1h DOUBLE PRECISION,
  pct_24h DOUBLE PRECISION,
  pct_7d DOUBLE PRECISION,
  image TEXT,
  PRIMARY KEY (ts_epoch_ms, coin_id, vs_currency)
);

CREATE INDEX IF NOT EXISTS idx_prices_coin_ts ON prices (coin_id, ts_epoch_ms);
