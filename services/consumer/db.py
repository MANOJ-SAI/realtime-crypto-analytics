
import os, psycopg2
from psycopg2.extras import execute_values

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_DB = os.getenv("POSTGRES_DB", "crypto")
DB_USER = os.getenv("POSTGRES_USER", "crypto")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "crypto")

def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_DB, user=DB_USER, password=DB_PASS)

def init_schema():
    with get_conn() as conn, conn.cursor() as cur:
        with open("schema.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()

def upsert_prices(rows):
    sql = '''
    INSERT INTO prices
      (ts_epoch_ms, ts_iso, coin_id, symbol, name, vs_currency,
       current_price, market_cap, total_volume, high_24h, low_24h,
       pct_1h, pct_24h, pct_7d, image)
    VALUES %s
    ON CONFLICT (ts_epoch_ms, coin_id, vs_currency) DO UPDATE SET
      current_price = EXCLUDED.current_price,
      market_cap = EXCLUDED.market_cap,
      total_volume = EXCLUDED.total_volume,
      high_24h = EXCLUDED.high_24h,
      low_24h = EXCLUDED.low_24h,
      pct_1h = EXCLUDED.pct_1h,
      pct_24h = EXCLUDED.pct_24h,
      pct_7d = EXCLUDED.pct_7d,
      image = EXCLUDED.image;
    '''
    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, rows)
        conn.commit()
