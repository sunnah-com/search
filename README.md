# sunnah.com Search API

Flask + Elasticsearch search service for sunnah.com. Supports lexical (BM25), semantic, and hybrid search across the hadith corpus.

## What's in this branch

This branch extends the existing search service with **multi-model semantic search**: multiple embedding models can be indexed and queried independently, letting the team compare results before committing to one model in production.

### Key changes from main

- **Multi-model architecture** — each embedding model gets its own ES index. Models are enabled/disabled via env vars with no code changes required.
- **Dedicated lexical index** (`english-lexical`) — separated from the semantic indexes so it can be rebuilt quickly without re-embedding.
- **Testbed UI** — the API root (`/`) now serves a search interface for testing modes and models side-by-side without the PHP website.
- **`/api/models` endpoint** — returns which models are configured and whether their indexes are built; the testbed UI calls this on load.

Corresponding website changes (mode/model toggles in the production UI) are in the `semantic-search-ui-toggles` branch of the website repo.

---

## Architecture

```
Browser / PHP website
        │
        ▼
  Flask API (this repo) ──► Elasticsearch
        │                        │
        │              ┌─────────┴──────────┐
        │              │  english-lexical    │  BM25, no embeddings
        │              │  english-nomic      │  nomic-embed-text via Ollama
        │              │  english-mxbai      │  mxbai-embed-large via Ollama
        │              │  english-openai-*   │  text-embedding-3-small via OpenAI API
        │              │  multilingual-*     │  text-embedding-3-small, full corpus
        │              │  english-embedding… │  embeddinggemma-300m via TEI (optional)
        │              └────────────────────┘
        │
  Model servers (embedding inference)
        ├── Ollama (runs on host, port 11434) — nomic, mxbai
        ├── OpenAI API — openai-small-en / openai-small-multi
        └── tei-gemma Docker service — embeddinggemma (optional, see below)
```

Each model's index name in ES is an **alias** (e.g. `english-nomic`) that points to a timestamped backing index (e.g. `english-nomic-1779026769`). Reindexing builds a new backing index and atomically swaps the alias — the live index keeps serving traffic during the rebuild.

---

## Local setup

### Prerequisites

- Docker + Docker Compose
- For Ollama-backed models (nomic, mxbai): [Ollama](https://ollama.com) installed and running on your machine

### 1. Configure environment

```bash
cp .env.sample .env
```

Edit `.env` and enable the models you want to test:

```env
NOMIC_ENABLED=true
MXBAI_ENABLED=true
OPENAI_ENABLED=false   # requires OPENAI_API_KEY
EMBEDDINGGEMMA_ENABLED=false  # requires --profile embeddinggemma, see below
```

If using Ollama and it's not at the default address, set:
```env
OLLAMA_URL=http://host.docker.internal:11434
```

### 2. Pull Ollama models (if enabled)

```bash
ollama pull nomic-embed-text
ollama pull mxbai-embed-large
```

### 3. Start the stack

```bash
docker compose up --build
```

The override file (`docker-compose.override.yml`) is applied automatically and exposes Flask on port 5001.

For the embeddinggemma model only:
```bash
docker compose --profile embeddinggemma up --build
```
This starts the `tei-gemma` service which downloads `google/embeddinggemma-300m` from HuggingFace on first run (~600 MB, cached in a Docker volume).

### 4. Build the indexes

Open in a browser or curl:

```
http://localhost:5001/index?password=index123
```

This reads all hadiths from MySQL and builds ES indexes for every enabled model plus the lexical index. It takes a while — embedding ~48k English hadiths per model is the slow part.

To rebuild only one model's index:
```
http://localhost:5001/index?password=index123&model=nomic
http://localhost:5001/index?password=index123&model=lexical
```

To force a full rebuild instead of incremental:
```
http://localhost:5001/index?password=index123&rebuild=true
```

Check index status (doc counts per index):
```
http://localhost:5001/index/status
```

---

## Embedding models

| Key | Model | Served by | Dimensions | Notes |
|---|---|---|---|---|
| `openai-small-en` | text-embedding-3-small | OpenAI API | 1536 | English corpus only |
| `openai-small-multi` | text-embedding-3-small | OpenAI API | 1536 | Full Arabic+English corpus |
| `nomic` | nomic-embed-text | Ollama (host) | 768 | English-only |
| `mxbai` | mxbai-embed-large | Ollama (host) | 1024 | English-only |
| `embeddinggemma` | embeddinggemma-300m | tei-gemma (Docker) | 256 | Optional, needs `--profile embeddinggemma` |

**Nomic and mxbai run via Ollama on your host machine**, not inside Docker. The container reaches them at `http://host.docker.internal:11434` — a Docker hostname that resolves to your Mac's IP from inside any container. Ollama exposes an OpenAI-compatible API, which is what ES 8.16's inference endpoint uses.

**embeddinggemma runs in a Docker container** (`tei-gemma`) using HuggingFace's Text Embeddings Inference server. It's gated behind a Docker Compose profile so it doesn't start unless you need it.

### Adding a new model

1. Add an entry to `EMBEDDING_MODELS` in `main.py` — copy the shape of any existing entry. For an Ollama model it's ~8 lines.
2. Add `NEWMODEL_ENABLED=false` to `.env.sample` (and set to `true` in your local `.env`).
3. Pull the model in Ollama: `ollama pull your-model-name`
4. Hit `/index?password=index123&model=newmodel` to build its index.
5. Update `SEMANTIC_INDEXES` in `batch_search.py` to include it (use the alias name, e.g. `"english-newmodel"`).

### Disabling a model

Set `MODELNAME_ENABLED=false` in `.env`. The model is completely ignored at runtime — no index queries, no inference calls.

---

## Search modes

| Mode | What it does |
|---|---|
| `lexical` | BM25 full-text search with collection boosts. Fast, exact keyword matching. |
| `semantic` | Embedding similarity via HNSW approximate nearest-neighbor. Finds conceptually related hadiths even without keyword overlap. |
| `hybrid` | Both legs run in parallel (msearch), results fused with Reciprocal Rank Fusion (RRF). |

The active mode and model are passed as query parameters:
```
/english/search?q=prayer&mode=semantic&model=nomic
/english/search?q=prayer&mode=hybrid&model=mxbai
/english/search?q=prayer&mode=lexical
```

---

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Testbed UI — search interface for comparing modes and models |
| `GET /api/models` | JSON: configured models + whether each index exists in ES |
| `GET /<language>/search?q=...` | Main search endpoint (consumed by PHP website) |
| `GET /index?password=...` | Build/rebuild ES indexes from MySQL |
| `GET /index/status` | Doc counts for all indexes |

---

## Docker Compose files

| File | When to use |
|---|---|
| `docker-compose.yml` | Base definition. Do not run directly. |
| `docker-compose.override.yml` | Applied automatically on `docker compose up`. Exposes Flask on port 5001 (override from default 5000 to avoid conflicts). |
| `docker-compose.prod.yml` | Production. Run with `-f docker-compose.prod.yml`. Uses uwsgi, persistent ES data volume, explicit JVM memory limits, no MySQL service. |

**Why Elasticsearch has a fixed IP** (`172.31.250.10`): at high request rates, Docker's embedded DNS resolver becomes a bottleneck and throws `EAI_AGAIN` errors. Hardcoding the IP in `/etc/hosts` via `extra_hosts` makes every lookup instant.

**Observability services** (`es-exporter`, `alloy`) are included in the base compose file. They ship ES metrics and logs to Grafana Cloud. They require Grafana Cloud credentials in `.env` — if you don't have them, these services will fail to connect but won't break the rest of the stack.

---

## Batch evaluation

`batch_search.py` runs a fixed set of queries across all enabled models and produces a CSV and a markdown report for side-by-side comparison.

```bash
# Copy script into container, run it, copy results back
docker cp search/batch_search.py search-web-1:/code/batch_search.py && \
docker exec search-web-1 python3 /code/batch_search.py && \
docker cp search-web-1:/code/batch_results.csv search/batch_results.csv && \
docker cp search-web-1:/code/batch_report.md search/batch_report.md
```

The script must run inside the container because ES is not exposed to the host — it's only reachable at `http://elasticsearch:9200` from within the Docker network.

Edit `QUERIES` in `batch_search.py` to change which queries are tested. Edit `SEMANTIC_INDEXES` to add or remove models from the comparison.

**Note:** always use commas between query strings in the list. Python silently concatenates adjacent string literals without a comma, producing wrong queries with no error.
