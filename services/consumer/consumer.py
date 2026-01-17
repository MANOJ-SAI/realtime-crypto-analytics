
import os, json, time, logging
from kafka import KafkaConsumer
from dateutil import parser as dateparser
from db import init_schema, upsert_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "crypto.ticks")

def parse_ts_ms(ts_iso):
    if not ts_iso:
        return int(time.time() * 1000)
    try:
        dt = dateparser.parse(ts_iso)
        return int(dt.timestamp() * 1000)
    except Exception:
        return int(time.time() * 1000)

def main():
    init_schema()
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    logging.info("Consumer listening on %s", KAFKA_TOPIC)
    batch, last = [], time.time()
    while True:
        pack = consumer.poll(timeout_ms=1000)
        for _, msgs in pack.items():
            for msg in msgs:
                v = msg.value
                ts_ms = parse_ts_ms(v.get("ts_iso"))
                row = (
                    ts_ms, v.get("ts_iso"), v.get("id"), v.get("symbol"), v.get("name"),
                    v.get("vs_currency"), v.get("current_price"), v.get("market_cap"),
                    v.get("total_volume"), v.get("high_24h"), v.get("low_24h"),
                    v.get("price_change_percentage_1h_in_currency"),
                    v.get("price_change_percentage_24h_in_currency"),
                    v.get("price_change_percentage_7d_in_currency"),
                    v.get("image")
                )
                batch.append(row)
        if batch and (len(batch) >= 200 or time.time() - last > 5):
            try:
                upsert_prices(batch)
                logging.info("Upserted %d rows", len(batch))
            except Exception as e:
                logging.exception("DB upsert failed: %s", e)
            batch, last = [], time.time()

if __name__ == "__main__":
    main()
