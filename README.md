
# Real-Time Crypto Analytics & Forecasting Platform (Kafka + CoinGecko + Postgres + Streamlit)

**Pipeline**: CoinGecko API → Kafka topic → Consumer → Postgres → Streamlit Dashboard

- Producer: pulls live crypto market data (top N by market cap)
- Consumer: upserts into Postgres
- Dashboard: KPIs, live charts, short-term forecast
- Kafka UI: inspect topics at http://localhost:8080


##  Project Overview

This project implements an **end-to-end real-time data streaming and analytics pipeline** for cryptocurrency markets using **Apache Kafka, PostgreSQL, Streamlit, and Machine Learning models (Prophet & LSTM)**.

The system continuously ingests live cryptocurrency price data, processes it through Kafka producers and consumers, stores it in a relational database, visualizes it via an interactive dashboard, and generates short-term price forecasts.

This project demonstrates a **modern event-driven architecture**, real-time analytics, and predictive modeling—similar to systems used in **fintech and trading platforms**.

---

##  System Architecture

- CoinGecko API
  ↓
- Kafka Producer (Python)
  ↓
- Kafka Topic (crypto.ticks)
  ↓
- Kafka Consumer (Python)
  ↓
- PostgreSQL (Time-series storage)
  ↓
- Streamlit Dashboard
  ↓
- Forecasting (Prophet & LSTM)


---

##  Key Features

- 🔄 Real-time cryptocurrency price streaming
- ⚡ Event-driven architecture using Apache Kafka
- 🗄️ Persistent time-series storage in PostgreSQL
- 📊 Interactive dashboards using Streamlit
- 📈 Multi-coin comparison & normalized performance views
- 🔮 Short-term forecasting using:
    - **Prophet** (statistical forecasting)
    - **LSTM** (deep learning)

- 🐳 Fully containerized using **Docker Compose**

---

##  Technologies Used

| Category | Tools |
|-------|------|
| Streaming | Apache Kafka (KRaft mode) |
| Backend | Python |
| Database | PostgreSQL |
| Dashboard | Streamlit |
| ML Models | Prophet, LSTM (TensorFlow/Keras) |
| Containerization | Docker & Docker Compose |
| API | CoinGecko Public API |

---


---

##  Setup & Installation

###  Prerequisites

- Docker
- Docker Compose
- Internet connection (for CoinGecko API)

---

###  Clone the Repository

```bash
git clone https://github.com/MANOJ-SAI/realtime-crypto-analytics.git
cd realtime-crypto-analytics
```
🔹 Environment Variables (.env)
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=crypto.ticks

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=crypto
POSTGRES_USER=crypto
POSTGRES_PASSWORD=crypto

STREAMLIT_PORT=8501
REFRESH_MS=30000
```

🔹 Start the Application

```bash
docker-compose up --build
```
🌐 Access the Application
- Streamlit Dashboard
  👉 http://localhost:8501

- Kafka UI (if enabled)
  👉 http://localhost:8080


## Dashboard Capabilities
- Live cryptocurrency price monitoring

- Per-coin metrics (price, 24h % change)

- Multi-coin comparison charts

- Indexed performance visualization

- Real-time database-backed updates

- Short-term price forecasting plots

## Forecasting Models
### Prophet
- Captures trends and seasonality

- Fast and interpretable

- Suitable for short-term forecasts

### LSTM
- Deep learning model for sequence data

- Learns non-linear price patterns

- Trained using historical cryptocurrency prices

## Evaluation Metrics
- Mean Absolute Percentage Error (MAPE)

- Root Mean Square Error (RMSE)

- Kafka pipeline latency and throughput

## Challenges Faced
- Kafka message size and heap memory issues

- Real-time API rate limits

- Forecasting noisy financial data

- Docker networking and service dependencies

All issues were resolved through Kafka tuning, heap optimization, and efficient data handling.

## Future Enhancements
- Kubernetes deployment

- Schema Registry integration

- Anomaly detection

- Hybrid forecasting models

- Support for multiple financial instruments

## Academic Relevance
This project is suitable for:

- Final Year / Capstone Projects

- Big Data Analytics

- Real-Time Systems

- Data Engineering

- Machine Learning Applications

## Author
**Koudodi Manoj Sai**
Software Engineer | Data & Platform Enthusiast

## License
This project is for **educational and academic purposes.**
