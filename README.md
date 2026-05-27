# sunnah.com Search API

Flask + Elasticsearch search service for sunnah.com. Supports lexical (BM25) and semantic search.

---

## Architecture

```
Browser / PHP website
        │
        ▼
  Flask API (this repo) ──► Elasticsearch
                                  │
                      ┌───────────┴───────────┐
                      │  english-lexical       │  BM25, no embeddings
                      │  english-mxbai         │  mxbai-embed-large via Ollama
                      └───────────────────────┘

  Ollama (runs on host, port 11434) — serves mxbai-embed-large
```

Each index name in ES is an **alias** (e.g. `english-mxbai`) pointing to a timestamped backing index. Reindexing builds a new backing index and atomically swaps the alias — the live index keeps serving traffic during the rebuild.

---

## Local development setup

### Prerequisites

- Docker + Docker Compose
- [Ollama](https://ollama.com) installed and running on your machine

### 1. Configure environment

```bash
cp .env.sample .env
```

Set `MXBAI_ENABLED=true` in `.env`. `OLLAMA_URL` defaults to `http://host.docker.internal:11434`, which works on Docker Desktop (Mac/Windows) — leave it unset locally.

### 2. Pull the model

```bash
ollama pull mxbai-embed-large
```

### 3. Start the stack

```bash
docker compose up --build
```

Flask is exposed on **port 5001**.

### 4. Build the indexes

```
http://localhost:5001/index?password=index123
```

This reads all hadiths from MySQL and builds both the lexical and mxbai indexes. Embedding ~48k English hadiths takes a few minutes.

To index only one at a time:
```
http://localhost:5001/index?password=index123&model=mxbai
http://localhost:5001/index?password=index123&model=lexical
```

To force a full rebuild instead of incremental:
```
http://localhost:5001/index?password=index123&rebuild=true
```

Check index status (doc counts):
```
http://localhost:5001/index/status
```

---

## Production deployment

Production uses `docker-compose.prod.yml` directly. Key differences from local:
- **No MySQL service** — connects to the existing external DB via env vars
- **uwsgi** instead of Flask dev server, exposed on **port 7650**
- **Persistent ES data** in a named Docker volume (`es-data`)
- **Explicit ES JVM memory limits** (`-Xms600m -Xmx1g`)

### 1. Configure environment

```bash
cp .env.sample .env
```

Fill in production values — at minimum:

```env
MYSQL_HOST=<prod db host>
MYSQL_USER=<user>
MYSQL_PASSWORD=<password>
MYSQL_DATABASE=hadithdb

ELASTIC_PASSWORD=<strong password>
INDEXING_PASSWORD=<strong password>

MXBAI_ENABLED=true
```

### 2. Ollama on Linux

Install [Ollama](https://ollama.com) on the host and pull the model before starting the stack:

```bash
ollama pull mxbai-embed-large
```

`host.docker.internal` only works on Docker Desktop (Mac/Windows), not on Linux. The prod compose file adds `host-gateway` so this hostname resolves correctly on Linux too — the default `OLLAMA_URL` works without any extra `.env` changes.

### 3. Start the stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 4. Build the indexes

The prod stack is exposed on **port 7650**:

```
http://<server>:7650/index?password=<INDEXING_PASSWORD>
```

To index only one at a time:
```
http://<server>:7650/index?password=<INDEXING_PASSWORD>&model=mxbai
http://<server>:7650/index?password=<INDEXING_PASSWORD>&model=lexical
```

Check index status:
```
http://<server>:7650/index/status
```

---

## Embedding model

| Key | Model | Served by | Dimensions |
|---|---|---|---|
| `mxbai` | mxbai-embed-large | Ollama (host) | 1024 |

mxbai runs via **Ollama on the host machine**, not inside Docker. The container reaches it at `http://host.docker.internal:11434`. Ollama exposes an OpenAI-compatible API, which ES 8.16's inference endpoint uses to embed queries and index documents.

### Adding a model

1. Add an entry to `EMBEDDING_MODELS` in `main.py` — copy the mxbai entry as a template (~8 lines).
2. Add `NEWMODEL_ENABLED=false` to `.env.sample`.
3. Pull the model: `ollama pull your-model-name`
4. Hit `/index?password=...&model=newmodel` to build its index.
5. Add the alias name to `SEMANTIC_INDEXES` in `tests/batch_search.py`.

---

## Search modes

| Mode | What it does |
|---|---|
| `lexical` | BM25 full-text search with collection boosts. Fast, exact keyword matching. Default. |
| `semantic` | Embedding similarity via HNSW approximate nearest-neighbor. Finds conceptually related hadiths even without keyword overlap. |

Mode is passed as a query parameter:
```
/english/search?q=prayer&mode=semantic&model=mxbai
/english/search?q=prayer&mode=lexical
```

---

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /<language>/search?q=...` | Main search endpoint (consumed by PHP website) |
| `GET /index?password=...` | Build/rebuild ES indexes from MySQL |
| `GET /index/status` | Doc counts for all indexes |

---

## Docker Compose files

| File | When to use |
|---|---|
| `docker-compose.yml` | Local development. `docker compose up --build`. |
| `docker-compose.prod.yml` | Production. Run with `-f docker-compose.prod.yml`. Uses uwsgi, persistent ES data volume, explicit JVM memory limits, no MySQL service. |

**Why Elasticsearch has a fixed IP** (`172.31.250.10`): at high request rates, Docker's embedded DNS resolver becomes a bottleneck and throws `EAI_AGAIN` errors. Hardcoding the IP in `/etc/hosts` via `extra_hosts` makes every lookup instant.

**Observability services** (`es-exporter`, `alloy`) ship ES metrics and logs to Grafana Cloud. They require Grafana Cloud credentials in `.env` — if you don't have them, these services will fail to connect but won't break the rest of the stack.

---

## Batch evaluation

`tests/batch_search.py` runs a fixed set of queries across lexical and semantic and produces a CSV and markdown report for side-by-side comparison.

```bash
# Copy script into container, run it, copy results back
docker cp tests/batch_search.py search-web-1:/code/batch_search.py && \
docker exec search-web-1 python3 /code/batch_search.py && \
docker cp search-web-1:/code/batch_results.csv tests/batch_results.csv && \
docker cp search-web-1:/code/batch_report.md tests/batch_report.md
```

The script runs inside the container because ES is not exposed to the host — it's only reachable at `http://elasticsearch:9200` from within the Docker network.

Edit `QUERIES` in `tests/batch_search.py` to change which queries are tested.

**Note:** always use commas between query strings in the list. Python silently concatenates adjacent string literals without a comma, producing wrong queries with no error.
