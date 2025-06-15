# 🧠 MASX_AI_NEWS_ETL

`MASX_AI_NEWS_ETL` is a modular, resilient daily news processing pipeline that ingests, summarizes, translates, and embeds global news articles using transformers, multilingual scraping, proxy rotation, and semantic enrichment. It supports both **local development** and **production orchestration** using **Apache Airflow**, **Kafka**, and **Redis**.

> This service feeds MASX AI’s doctrine-driven geopolitical forecasting engine by preparing clean, multilingual summaries from global sources like GDELT.

---

## 🚀 Features

- 🌐 **Multilingual News Ingestion** — via `feedparser`, `newspaper3k`
- 🧽 **Content Extraction Engine** — `BeautifulSoup` primary + `crawl4ai` fallback
- 🧠 **Summarization** — BART-based summarizer (`facebook/bart-large-cnn`)
- 🌍 **Translation** — Auto-detect language + translate using `deep-translator`
- 🧭 **Embedding-Ready** — Processed summaries for vector storage
- 🔁 **Proxy Rotation via Redis** — Dynamic IP rotation with periodic validation
- 🪂 **Kafka Integration** — Sends final summaries to downstream systems
- ⏱ **Airflow DAGs** — Orchestrates `update_proxypool`, `extract_news`, and more
- 📡 **ENV-based Control** — Separate config for dev and prod environments

---

## 🧱 Architecture

```text
+---------------------------+
|   Airflow DAG (daily)    |
+------------+-------------+
             ↓
┌────────────┼────────────────────────────┐
│ update_proxypool                       │
│   └── Validate proxies, cache in Redis │
└────────────┬────────────────────────────┘
             ↓
┌────────────┼────────────────────────────┐
│ extract_news                            │
│   └── Fetch & parse RSS feeds           │
│   └── BeautifulSoup or crawl4ai fallback│
│   └── Translate → Summarize → Embed     │
│   └── Publish to Kafka topic            │
└────────────┴────────────────────────────┘
```

---

## ⚙️ Stack Overview

| Layer         | Technology                         |
|---------------|-------------------------------------|
| Language      | Python 3.11                         |
| Extraction    | BeautifulSoup, crawl4ai             |
| Summarization | HuggingFace Transformers (BART)     |
| Translation   | Deep Translator, langdetect         |
| Scheduling    | Apache Airflow                      |
| Messaging     | Kafka (prod only)                   |
| Caching       | Redis                               |
| Proxy Source  | free-proxy-list.net                 |

---
##  MASX_AI_NEWS_ETL - Ongoing Implementation

Airflow runs DAG → pushes summary to Kafka →
  ├─ Consumer A: stores to vector DB  ----yes 
  ├─ Consumer B: tags with doctrines  ----??? 
  ├─ Consumer C: pushes to UI  ---- yes 
  └─ Consumer D: triggers AutoGen feedback ---????

---

##  MASX_AI_NEWS_ETL - Folder Structure

```




MASX_AI_NEWS_ETL/
├── dags/                          # Airflow DAGs
│   └── news_etl_dag.py
├── etl/                           # Core ETL logic
│   ├── extract.py                 # Handles feedparser + crawl4ai fallback
│   ├── summarize.py              # BART model loading + summarization
│   ├── translate.py              # Multilingual translation
│   ├── proxy_manager.py          # Proxy validation + Redis cache
│   ├── kafka_publisher.py        # Sends JSON to Kafka
│   ├── redis_connector.py        # Auto-start and Redis config loader
│   └── utils.py                  # Cleaning, langdetect, etc.
├── config/
│   ├── __init__.py
│   └── settings.py               # Loads from .env and sets ENV vars
├── models/
│   └── summarizer.py             # Loads tokenizer + BART model (once)
├── tests/
│   └── test_etl_pipeline.py
├── .env                          # Environment variables (excluded via .gitignore)
├── .gitignore
├── README.md
├── requirements.txt
├── Pipfile
├── Dockerfile
└── main.py                       # Entry point for manual runs

```
---

## 📦 Example Output

```json
{
  "article_id": "dw-eu-summit-20250613",
  "source": "DW",
  "language": "ar",
  "translated_summary": "The EU summit discussed rising China tensions...",
  "embedding": [0.42, -0.13, 0.77, ...]
}
```

---

## 🛠️ Setup Instructions

### 🧪 Local Dev (Redis Auto-launch)

```bash
pipenv install
pipenv shell
python main.py
```

Redis will auto-launch via Docker if not running:
```bash
docker run -d -p 6379:6379 --name masx-summarizer-redis --rm redis
```

---

### 🏭 Production (Airflow + Kafka)

#### 1. Airflow DAG (`etl_dag.py`)
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

update_proxypool_task = PythonOperator(
    task_id='update_proxypool',
    python_callable=update_proxypool,
    provide_context=True,
    dag=dag
)

extract_news_task = PythonOperator(
    task_id='extract_news',
    python_callable=extract_news,
    provide_context=True,
    dag=dag
)
```

#### 2. Kafka Publisher
Summaries are published to Kafka for downstream agents:
```python
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
producer.send("masx_summaries", value=json.dumps(summary).encode("utf-8"))
```

---

## 📁 ENV File Example

```env
APP_ENV=prod
REDIS_HOST_PROD=redis
REDIS_PORT_PROD=6379
REDIS_KEY=proxies-1
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=masx_summaries
```

---

## 🔐 Security

- `.env` file excluded via `.gitignore`
- Uses proxy headers for safe scraping
- Avoids persistent identifiers or PII

---

## 🧠 Roadmap

- [x] Airflow DAG support
- [x] Kafka integration
- [x] Redis auto-start and fallback
- [ ] Vector DB embedding and similarity clustering
- [ ] Doctrine alignment and threat tagging

---

## 🙌 Author

Developed by [Ateet Bahamani](https://ateetai.vercel.app)  
Part of the [MASX AI](https://masxai.com) project — a multi-agent AI system for global strategic forecasting.

---

## 🪪 License

MIT License
