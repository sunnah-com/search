# sunnah.com Search API

Flask + Elasticsearch search service for sunnah.com. Supports lexical (BM25) and semantic search.

---

## Architecture

```
Browser / PHP website
        │
        ▼
  Flask API (this repo)
        │
        ├── query router (_route_query)
        │       ├── any Arabic text  → cross_fields BM25 (all docs)    ─┐
        │       ├── "quoted query"   → cross_fields BM25 (en docs)      │
        │       ├── ends with number → cross_fields BM25 (en docs)      ├─ english-lexical
        │       ├── AND / OR / NOT   → cross_fields BM25 (en docs)      │
        │       └── everything else  → cross_fields BM25 (en docs)     ─┘
        │
        └── mode=semantic             → kNN       ── english-<model>
                                                      (semantic_text)
        └── Elasticsearch
                ├── english-lexical   — BM25 searches hadithText + arabicText
                └── english-<model>   — kNN searches semantic_text only

  Infinity server (host, port 7997) — embeds search queries
  HF Dedicated Endpoint (optional) — embeds documents at index time
```

BM25 paths all run against `english-lexical`. Semantic paths run against the index for the active model (e.g. `english-mxbai`, `english-embeddinggemma-qat-q4`). Both index types share the same text fields; the semantic index adds a `semantic_text` vector field.

Each index name in ES is an **alias** (e.g. `english-mxbai`) pointing to a timestamped backing index. Reindexing builds a new backing index and atomically swaps the alias — the live index keeps serving traffic during the rebuild.

---

## Local development setup

### Prerequisites

- Docker + Docker Compose
- [Infinity](https://github.com/michaelf34/infinity) installed and running on your machine

### 1. Configure environment

```bash
cp .env.sample .env
```

Semantic search is on by default (`SEMANTIC_ENABLED=true`). Set it to `false` if you want lexical-only and don't want to run the Infinity server. `INFINITY_URL` defaults to `http://host.docker.internal:7997`, which works on Docker Desktop (Mac/Windows) — leave it unset locally.

To offload index-time embedding to a HuggingFace Dedicated Inference Endpoint (recommended for prod — orders of magnitude faster on a small GPU than Infinity on a CPU instance), also set `HUGGING_FACE_KEY` and `HF_DEDICATED_URL` in `.env`. The endpoint must run [TEI](https://github.com/huggingface/text-embeddings-inference) with `mixedbread-ai/mxbai-embed-large-v1`. Leaving either var unset falls back to embedding via the Infinity server at index time too.

### 2. Serve the model

Pull whichever embedding model is configured in `EMBEDDING_MODELS` in `main.py`:

```bash
infinity_emb v2 --model-id mixedbread-ai/mxbai-embed-xsmall-v1 --port 7997
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

This reads all hadiths from MySQL and builds **both** the lexical and semantic indexes by default — that's almost always what you want. Embedding ~48k English hadiths takes ~9 min via the HF Dedicated Endpoint (or considerably longer through the Infinity server if no remote endpoint is configured).

To build a subset, pass `targets=` (comma-separated):
```
http://localhost:5000/index?password=index123&targets=lexical              # lexical only
http://localhost:5000/index?password=index123&targets=<model-key>          # one semantic model
http://localhost:5000/index?password=index123&targets=lexical,<model-key>  # both
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

### 2. Infinity server on Linux

Run an [Infinity](https://github.com/michaelf34/infinity) server on the host, serving the embedding model, before starting the stack:

```bash
infinity_emb v2 --model-id mixedbread-ai/mxbai-embed-xsmall-v1 --port 7997
```

`host.docker.internal` only works on Docker Desktop (Mac/Windows), not on Linux. The prod compose file adds `host-gateway` so this hostname resolves correctly on Linux too — the default `INFINITY_URL` works without any extra `.env` changes.

### 3. Start the stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 4. Build the indexes

The prod stack is exposed on **port 7650**. Builds both lexical and semantic by default:

```
http://<server>:7650/index?password=<INDEXING_PASSWORD>
```

Add `&targets=lexical` or `&targets=<model-key>` to build a subset.

Check index status:
```
http://<server>:7650/index/status
```

### Deploying the query router

The query router is a **pure code change** — no index rebuild or schema migration needed. The existing index serves all routes without modification.

**Recommended rollout steps:**

1. **Deploy with `ROUTER_LOG=true`** first. This emits one structured log line per request to the access log, letting you audit routing decisions on real traffic before committing:

   ```env
   ROUTER_LOG=true
   ```

   Watch for unexpected `route` values or `overridden: true` cases where user intent doesn't match what the router chose.

2. **Review a day of traffic.** Key things to check:
   - Arabic queries route to `lexical_arabic` and not falling through to standard BM25.
   - Quoted queries route to `lexical` (quotes force BM25; `query_string` handles phrase natively).
   - No legitimate English queries accidentally route to `lexical_arabic` — this happens if a query contains a stray Arabic character. Look for `overridden: true` on queries that look English.

3. **Correlate with shadow sampling** (if `SEARCH_METRICS_SAMPLE_PERCENT > 0`). The `routing_decision` column in `search_metrics` records the route taken alongside lexical and semantic result bodies for each sampled request — useful for comparing what each route returned on the same real queries.

4. **Turn off `ROUTER_LOG`** once routing looks correct. Structured logs are low-overhead but add access log noise on high-traffic servers.

5. **Rollback** is a single `docker compose` redeploy of the previous image. The index is untouched so rollback is instant.

---

## Embedding model

The active model(s) are declared in `EMBEDDING_MODELS` in `config.py`. Model selection is under active evaluation — see `tests/small_model_comparison.py` for the comparison script.

| Key | Model | Query-time | Index-time | Dimensions |
|---|---|---|---|---|
| `mxbai` | mxbai-embed-large | Infinity (host) | HF Dedicated Endpoint (optional) → else Infinity | 1024 |
| `mxbai-xsmall` | mxbai-embed-xsmall | Infinity (host) | HF Dedicated Endpoint (optional) → else Infinity | 384 |

Queries are always embedded via the **Infinity server on the host machine** (not inside Docker) — the container reaches it at `http://host.docker.internal:7997` via ES 8.16's OpenAI-compatible inference endpoint. Index-time embedding is offloaded to a remote TEI endpoint when `HUGGING_FACE_KEY` + `HF_DEDICATED_URL` are set: the indexer fetches vectors over HTTP and ships them inline with the bulk payload (ES's `semantic_text` accepts pre-populated chunks and skips its own inference call). Vectors from TEI and Infinity for the same model are bit-compatible (cosine ≈ 0.9999), so queries can match docs embedded by either side.

Per-run tuning via env vars: `HF_DEDICATED_CONCURRENCY` (default 4), `HF_DEDICATED_BATCH_SIZE` (default 16), `HF_DEDICATED_RPM` (default -1, disabled).

### Adding a model

1. Add an entry to `EMBEDDING_MODELS` in `main.py` — copy the mxbai entry as a template (~10 lines).
2. Serve the model on the Infinity host: `infinity_emb v2 --model-id your-model-name`.
3. Hit `/index?password=...&targets=newkey` to build its index. (`/index` with no `targets=` will pick it up too, alongside lexical and the other semantic models.)
4. Add the alias name to `SEMANTIC_INDEXES` in `tests/batch_search.py`.
5. If it should be the default for `/search?mode=semantic` without a `&model=` param, point `DEFAULT_SEMANTIC_MODEL` at the new key.

`SEMANTIC_ENABLED` is a single global toggle — there is no per-model on/off switch.

---

## Shadow sampling (semantic rollout)

On a random fraction of lexical-served `/search` queries the service also runs the
semantic query in a background thread and records both sides — results and query
timings — to a `search_metrics` table in a separate **searchdb** (MySQL). The user
always gets the lexical response, unchanged and undelayed; the semantic run is
fire-and-forget.

The `routing_decision` column records which query route was taken (`lexical`,
`lexical_arabic`, `lexical_reference`, `semantic`) so sampled results can be grouped
and compared by query type.

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
`semantic_model_name`, `routing_decision`.

Locally, the `searchdb` service in `docker-compose.yml` provisions this DB and
creates the table from `searchdb/01-search_metrics.sql` on first start — no setup
needed beyond `docker compose up`. In prod, searchdb is an externally-managed DB
(like the hadith MySQL); just point the `searchdb_*` env vars at it.

---

---


## Query routing

Every incoming query is classified by `_route_query()` before any ES call. Rules apply in strict priority order — earlier rules always win and override `?mode=`:

| Priority | Query shape | Route | `_meta.route` | Example |
|---|---|---|---|---|
| 1 | Any Arabic Unicode character present | `cross_fields` BM25, full corpus | `lexical_arabic` | `صلاة`, `aisha عائشة` |
| 2 | Wrapped in double quotes (≥3 chars) | `cross_fields` BM25, forced off semantic | `lexical` | `"angel of death"` |
| 3 | Ends with a number (`/(^|\s)\d+[a-z]?\s*$/`) | `cross_fields` BM25, forced off semantic | `lexical_reference` | `bukhari 1`, `abu dawud 200`, `42` |
| 4 | Contains `AND` / `OR` / `NOT` (uppercase) | `cross_fields` BM25, forced off semantic | `lexical` | `prayer AND night` |
| 5 | Everything else | Client `mode` (`?mode=lexical` or `?mode=semantic`) | `lexical` or `semantic` | `prayer at night` |

**Priority is absolute** — all four lexical rules override `?mode=semantic`.

**Number queries (rule 3):** Any query ending with a number — including bare numbers like `5` or `42` — is forced to lexical. Semantic returns 0/9 correct for collection+number queries in top 10; bare numbers have nothing meaningful to embed. `hadithNumber^2` + `collection^2` boosts surface the correct hadith at rank 1. Misspellings like `bukahri 1` still end with a number and stay on lexical.

**Boolean operators (rule 4):** Uppercase `AND`/`OR`/`NOT` are ES `query_string` operators. Semantic search embeds them as plain text and discards the boolean logic — keeping these on BM25 ensures the operators work as intended.

**Language scoping:** Phrase, lexical, and semantic routes on `/english/search` apply `{"exists": {"field": "hadithText"}}` to exclude Arabic-only docs. The Arabic route skips this filter — Arabic-only docs have `arabicText` but no `hadithText`, so the filter would exclude valid matches. (`lang` is stored but not indexed; exists on `hadithText` is the equivalent filter.)

**`_meta.route`** is present in every response and names the path taken. Facet aggregations (`gradeNorm`, `collection`) and the `isChainRef` exclusion filter are added by downstream branches (corpus-normalization and facets).

### Collection boosts

All routes — lexical (Arabic BM25, reference, standard BM25) and semantic — are wrapped in a `function_score` that adds a flat weight to docs from authoritative collections before the score is summed. When two results have nearly equal BM25 or cosine scores, the boost surfaces the more-authenticated collection.

| Weight | Collections |
|---|---|
| 3.5 | Bukhari, Muslim |
| 3.3 | Nawawi 40, Riyadussalihin |
| 2.5 | Mishkat, Malik, Ahmad, Tirmidhi |
| 2.0 | Ibn Majah, Darimi |
| 1.0 | All others (baseline) |

This lifts the most-authenticated hadiths above identical keyword matches in weaker collections. The boost is additive (`boost_mode: sum`) so a highly-relevant weak-collection hadith can still outrank a barely-relevant Bukhari hadith.

### Standard lexical — query_string fallback

Standard BM25 uses `query_string` first (supports `AND`, `OR`, `-`, field prefixes). If ES rejects the query syntax (unmatched quotes, stray parentheses, reserved operators in unexpected positions), the handler retries automatically with `simple_query_string`, which is lenient and treats the query as plain text. The fallback is logged server-side but not exposed in `_meta`.

### Router audit logging

Set `ROUTER_LOG=true` in `.env` to emit one structured log entry per request:

```json
{
  "message": "router_decision",
  "query": "صلاة الليل",
  "mode_requested": "semantic",
  "route": "lexical_arabic",
  "variant": "arabic",
  "overridden": true
}
```

`overridden: true` means a query rule (phrase, Arabic, number, or boolean) forced a lexical path when `?mode=semantic` was requested. Off by default.

For full ES query shapes, detection code, and known limitations see [`docs/query_router_design.md`](docs/query_router_design.md).

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

`mode=semantic` uses the model named in `DEFAULT_SEMANTIC_MODEL` when no `&model=` is supplied. Pass `&model=<key>` to pick a different enabled model.

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
