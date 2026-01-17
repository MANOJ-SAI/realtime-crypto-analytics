
import os, time, json, logging, requests
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

API_KEY = os.getenv("COINGECKO_API_KEY")
VS_CURRENCY = os.getenv("VS_CURRENCY", "usd")
TOP_N = int(os.getenv("TOP_N", "10"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "crypto.ticks")
PER_PAGE = int(os.getenv("PER_PAGE", "250"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "1"))

if not API_KEY:
    raise SystemExit("COINGECKO_API_KEY is required. Set it in .env")

session = requests.Session()
session.headers.update({"x-cg-demo-api-key": API_KEY})

def fetch_markets_page(page: int):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": min(PER_PAGE, 250),
        "page": page,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }
    r = session.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def fetch_markets_paginated():
    coins = []
    for page in range(1, MAX_PAGES + 1):
        batch = fetch_markets_page(page)
        if not batch:
            break
        coins.extend(batch)
        # optional: be nice to the API
        time.sleep(0.3)
    return coins

def make_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        retries=5,
        linger_ms=50,
        acks="all",
    )

def to_event(coin):
    return {
        "ts_iso": coin.get("last_updated"),
        "id": coin.get("id"),
        "symbol": coin.get("symbol"),
        "name": coin.get("name"),
        "vs_currency": VS_CURRENCY,
        "current_price": coin.get("current_price"),
        "market_cap": coin.get("market_cap"),
        "total_volume": coin.get("total_volume"),
        "high_24h": coin.get("high_24h"),
        "low_24h": coin.get("low_24h"),
        "price_change_percentage_1h_in_currency": coin.get("price_change_percentage_1h_in_currency"),
        "price_change_percentage_24h_in_currency": coin.get("price_change_percentage_24h_in_currency"),
        "price_change_percentage_7d_in_currency": coin.get("price_change_percentage_7d_in_currency"),
        "image": coin.get("image"),
    }

def main():
    producer = make_producer()
    logging.info("Producer ready. Topic=%s", KAFKA_TOPIC)
    while True:
        try:
            coins = fetch_markets_paginated()
            for coin in coins:
                event = to_event(coin)
                key = event["id"] or "coin"
                producer.send(KAFKA_TOPIC, key=key, value=event)
            producer.flush()
            logging.info("Published %d events", len(coins))
        except Exception as e:
            logging.exception("Error: %s", e)
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
