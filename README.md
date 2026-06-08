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
                      │  english-mxbai         │  mxbai-embed-large vectors
                      └───────────────────────┘

  Ollama (host, port 11434) — embeds search queries
  HF Dedicated Endpoint (optional) — embeds documents at index time
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

Semantic search is on by default (`SEMANTIC_ENABLED=true`). Set it to `false` if you want lexical-only and don't want to run Ollama. `OLLAMA_URL` defaults to `http://host.docker.internal:11434`, which works on Docker Desktop (Mac/Windows) — leave it unset locally.

To offload index-time embedding to a HuggingFace Dedicated Inference Endpoint (recommended for prod — orders of magnitude faster on a small GPU than Ollama on a CPU instance), also set `HUGGING_FACE_KEY` and `HF_DEDICATED_URL` in `.env`. The endpoint must run [TEI](https://github.com/huggingface/text-embeddings-inference) with `mixedbread-ai/mxbai-embed-large-v1`. Leaving either var unset falls back to embedding via Ollama at index time too.

### 2. Pull the model

```bash
ollama pull mxbai-embed-large
```

### 3. Start the stack

```bash
docker compose up --build
```

Flask is exposed on **port 5000**.

### 4. Build the indexes

```
http://localhost:5000/index?password=index123
```

This reads all hadiths from MySQL and builds **both** the lexical and semantic indexes by default — that's almost always what you want. Embedding ~48k English hadiths takes ~9 min via the HF Dedicated Endpoint (or considerably longer through Ollama if no remote endpoint is configured).

To build a subset, pass `targets=` (comma-separated):
```
http://localhost:5000/index?password=index123&targets=lexical          # lexical only
http://localhost:5000/index?password=index123&targets=mxbai            # one semantic model
http://localhost:5000/index?password=index123&targets=lexical,mxbai    # both (same as default)
```

To force a full rebuild instead of incremental:
```
http://localhost:5000/index?password=index123&rebuild=true
```

Check index status:
```
http://localhost:5000/index/status
```
Reports, per logical index (`lexical` + each semantic model): the live ES index
behind the alias, whether it supports incremental updates, total docs and an
English/Arabic breakdown, and any in-progress rebuild (a `{index}-{ns}` index
the alias hasn't swapped onto yet) with its climbing doc count. The top-level
`checkpoints` list shows embed-resume caches still on disk — present only while a
semantic build is running or was interrupted.

---

## Production deployment

Production uses `docker-compose.prod.yml` directly. Key differences from local:
- **No MySQL services** — connects to the existing external hadith DB and the searchdb (shadow-sampling metrics) via env vars
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

SEMANTIC_ENABLED=true

# searchdb (shadow sampling) — point at the externally-managed metrics DB
searchdb_host=<prod searchdb host>
searchdb_name=<db>
searchdb_username=<user>
searchdb_password=<password>
# 0 keeps shadow sampling off; raise to start sampling (see "Shadow sampling")
SEARCH_METRICS_SAMPLE_PERCENT=0
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

The prod stack is exposed on **port 7650**. Builds both lexical and semantic by default:

```
http://<server>:7650/index?password=<INDEXING_PASSWORD>
```

Add `&targets=lexical` or `&targets=mxbai` to build a subset.

Check index status:
```
http://<server>:7650/index/status
```

---

## Embedding model

| Key | Model | Query-time | Index-time | Dimensions |
|---|---|---|---|---|
| `mxbai` | mxbai-embed-large | Ollama (host) | HF Dedicated Endpoint (optional) → else Ollama | 1024 |
| `mxbai-xsmall` | mxbai-embed-xsmall | Ollama (host) | HF Dedicated Endpoint (optional) → else Ollama | 384 |

Queries are always embedded via **Ollama on the host machine** (not inside Docker) — the container reaches it at `http://host.docker.internal:11434` via ES 8.16's OpenAI-compatible inference endpoint. Index-time embedding is offloaded to a remote TEI endpoint when `HUGGING_FACE_KEY` + `HF_DEDICATED_URL` are set: the indexer fetches vectors over HTTP and ships them inline with the bulk payload (ES's `semantic_text` accepts pre-populated chunks and skips its own inference call). Vectors from TEI and Ollama for the same model are bit-compatible (cosine ≈ 0.9999), so queries can match docs embedded by either side.

Per-run tuning via env vars: `HF_DEDICATED_CONCURRENCY` (default 4), `HF_DEDICATED_BATCH_SIZE` (default 16, must keep `batch × max_input_length ≤ TEI's max_batch_tokens`), `HF_DEDICATED_RPM` (default -1, disabled).

### Adding a model

1. Add an entry to `EMBEDDING_MODELS` in `main.py` — copy the mxbai entry as a template (~10 lines).
2. Pull the model on the Ollama host: `ollama pull your-model-name`.
3. Hit `/index?password=...&targets=newkey` to build its index. (`/index` with no `targets=` will pick it up too, alongside lexical and the other semantic models.)
4. Add the alias name to `SEMANTIC_INDEXES` in `tests/batch_search.py`.
5. If it should be the default for `/search?mode=semantic` without a `&model=` param, point `DEFAULT_SEMANTIC_MODEL` at the new key.

`SEMANTIC_ENABLED` is a single global toggle — you don't add a per-model env var.

---

## Shadow sampling (semantic rollout)

To roll semantic search out safely, the service can **shadow-sample** live traffic:
on a random fraction of lexical-served `/search` queries it also runs the semantic
query in a background thread and records both sides — results and query timings —
to a `search_metrics` table in a separate **searchdb** (MySQL). The user always
gets the lexical response, unchanged and undelayed; the semantic run is fire-and-forget.

This produces an apples-to-apples dataset (same real queries, both engines) to
compare result quality and latency before flipping semantic on for everyone.

Enable it by setting the sample percent (0 = off, the default):

```env
SEARCH_METRICS_SAMPLE_PERCENT=5     # shadow 5% of lexical queries
```

Requires `SEMANTIC_ENABLED=true`, the default semantic model indexed, and a
reachable searchdb (`searchdb_host` / `searchdb_name` / `searchdb_username` /
`searchdb_password`). Optional knobs: `SEARCH_METRICS_WORKERS` (background pool
size, default 2) and `SEARCH_METRICS_MAX_INFLIGHT` (backlog cap before samples
are dropped under load, default 50).

`search_metrics` columns: `query`, `lexical_results` / `semantic_results` (full
ES response bodies as JSON), `lexical_query_time_ms` / `semantic_query_time_ms`,
`semantic_model_name`, and `routing_decision` (reserved for a future query router).

Locally, the `searchdb` service in `docker-compose.yml` provisions this DB and
creates the table from `searchdb/01-search_metrics.sql` on first start — no setup
needed beyond `docker compose up`. In prod, searchdb is an externally-managed DB
(like the hadith MySQL); just point the `searchdb_*` env vars at it.

---

## Search modes

| Mode | What it does |
|---|---|
| `lexical` | BM25 full-text search with collection boosts. Fast, exact keyword matching. Default. |
| `semantic` | Embedding similarity via HNSW approximate nearest-neighbor. Finds conceptually related hadiths even without keyword overlap. |

Mode is passed as a query parameter:
```
/english/search?q=prayer&mode=semantic
/english/search?q=prayer&mode=lexical
```

`mode=semantic` uses the model named in `DEFAULT_SEMANTIC_MODEL` (currently `mxbai`) when no `&model=` is supplied. Pass `&model=<key>` to pick a different enabled model.

---

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /<language>/search?q=...` | Main search endpoint (consumed by PHP website) |
| `GET /index?password=...` | Build/rebuild ES indexes from MySQL |
| `GET /index/status` | Per-index doc counts (English/Arabic), live index, and in-progress builds |

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
docker exec search-web-1 python3 /code/tests/batch_search.py
```

Outputs (`batch_results.csv`, `batch_report.md`) land in the repo root — the dev compose mounts `./:/code`, so files the script writes to `/code/` inside the container show up on the host immediately. No `docker cp` needed.

The script runs inside the container because ES is not exposed to the host — it's only reachable at `http://elasticsearch:9200` from within the Docker network.

Edit `QUERIES` in `tests/batch_search.py` to change which queries are tested.

**Note:** always use commas between query strings in the list. Python silently concatenates adjacent string literals without a comma, producing wrong queries with no error.

---

## Formatting

Format Python code with `uv format` before committing.
