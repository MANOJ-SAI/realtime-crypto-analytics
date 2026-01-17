
# Real-Time Crypto Analytics (Kafka + CoinGecko + Postgres + Streamlit)

**Pipeline**: CoinGecko API → Kafka topic → Consumer → Postgres → Streamlit Dashboard

- Producer: pulls live crypto market data (top N by market cap)
- Consumer: upserts into Postgres
- Dashboard: KPIs, live charts, short-term forecast
- Kafka UI: inspect topics at http://localhost:8080

## Quickstart
```bash
cp .env.example .env
# put your COINGECKO_API_KEY in .env
docker compose up -d --build
```
Open:
- Kafka UI → http://localhost:8080
- Streamlit → http://localhost:8501

## Customize
Edit `.env`:
- `TOP_N=10` — top coins
- `POLL_INTERVAL_SECONDS=30`
- `VS_CURRENCY=usd`
- Postgres creds
