"""Configuration and the semantic-model catalog.

Pure configuration and data — no Elasticsearch client, no Flask, no logging.
Everything here is read from the environment at import time so the rest of the
app can import ready-to-use constants. The semantic on/off switch is
SEMANTIC_ENABLED; the model catalog is EMBEDDING_MODELS.
"""

import os
from enum import Enum

from dotenv import load_dotenv

# Load before any os.environ reads below — config is imported first by every
# entrypoint, so this also populates env for main.py and embedding.py.
load_dotenv(".env.local")


def _is_truthy(value):
    return (value or "").lower() in ("1", "true", "yes")


def _int_env(name, default):
    """Parse an int env var, falling back to `default` on missing/garbage."""
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# Pure lexical index — no embeddings, fast to rebuild.
LEXICAL_INDEX = "english-lexical"

# Each model gets its own ES index so you can index and switch independently.
# The semantic field is always called "semantic_text" inside each model's index.
SEMANTIC_FIELD = "semantic_text"

# Clip the incoming query before it hits either search path. Semantic needs it
# because the embedding server doesn't truncate, so over-long input overflows the model's
# context window (400) or burns CPU and stalls the serial embed queue; lexical
# benefits too, since huge query_strings are pure ES load with no real intent
# behind them. Real queries are a phrase or two; 1000 chars only clips garbage.
# Env-tunable — tighten if context-length 400s reappear (e.g. dense scripts).
QUERY_MAX_CHARS = _int_env("QUERY_MAX_CHARS", 1000)

# Infinity embedding server (michaelf34/infinity) — OpenAI-compatible /v1/embeddings.
# Serves query-time embedding for every semantic model; replaced the CPU-bound Ollama
# backend that previously handled the non-xsmall models.
_INFINITY_URL = os.environ.get("INFINITY_URL", "http://host.docker.internal:7997")
_HUGGING_FACE_KEY = os.environ.get("HUGGING_FACE_KEY")
# Each remote model needs its own HF Inference Endpoint (one endpoint serves one
# model), so the URL is per-model. The HF key is shared across them.
_HF_DEDICATED_URL = os.environ.get(
    "HF_DEDICATED_URL"
)  # mxbai endpoint, e.g. https://<id>.endpoints.huggingface.cloud
_HF_DEDICATED_URL_EMBEDDINGGEMMA_QAT = os.environ.get(
    "HF_DEDICATED_URL_EMBEDDINGGEMMA_QAT"
)  # embeddinggemma QAT endpoint (serves the embeddinggemma-qat-q4 model)
_HF_DEDICATED_URL_MXBAI_XSMALL = os.environ.get(
    "HF_DEDICATED_URL_MXBAI_XSMALL"
)  # mxbai-embed-xsmall endpoint


def _build_remote_inference(url, model_id):
    """Index-time embedding via a HuggingFace Inference Endpoint running TEI.

    The endpoint exposes an OpenAI-compatible /v1/embeddings route that returns
    L2-normalized vectors directly. Returns None (→ fall back to ES inference
    via the local Infinity server at index time) when the HF key or this model's
    URL is missing.
    """
    if not (_HUGGING_FACE_KEY and url):
        return None
    return {
        "url": f"{url.rstrip('/')}/v1/embeddings",
        "api_key": _HUGGING_FACE_KEY,
        "model_id": model_id,  # TEI ignores model field, but OpenAI shape requires it
    }


SEMANTIC_ENABLED = _is_truthy(os.environ.get("SEMANTIC_ENABLED"))

# EmbeddingGemma is trained with asymmetric task prompts: documents are embedded
# with a "title/text" prefix and queries with a "task: search result" prefix.
# Embedding raw text without them measurably degrades retrieval, so we prepend
# them at both index and query time. The query/document split is the whole point
# of asymmetric retrieval — it pulls a query's vector toward its answer's document
# vector rather than toward other queries. Models that don't use this scheme
# (e.g. mxbai) simply carry no "prompts" key and are embedded verbatim.
# Ref: https://huggingface.co/google/embeddinggemma-300m  ("Prompt instructions")
_EMBEDDINGGEMMA_PROMPTS = {
    "query": "task: search result | query: ",
    "document": "title: none | text: ",
}

# Catalog of semantic models. Pure data — no env coupling. Add an entry here
# to register another model; the on/off switch lives on SEMANTIC_ENABLED above.
EMBEDDING_MODELS = {
    "embeddinggemma-q8": {
        "label": "embeddinggemma-q8",
        "index": "english-embeddinggemma-q8",
        "inference_id": "embeddinggemma-q8",
        "multilingual": False,
        "dims": 256,  # google/embeddinggemma-300m (QAT int4); same 768-d output as q8
        "prompts": _EMBEDDINGGEMMA_PROMPTS,
        # ES inference endpoint — bound to the local Infinity server (query-time embedding).
        # Infinity exposes an OpenAI-compatible API; ES 8.16 has no native infinity service.
        "service": "openai",
        "service_settings": {
            "api_key": "infinity",  # Infinity doesn't require auth; ES requires a non-empty value
            "url": f"{_INFINITY_URL}/v1/embeddings",
            # HF repo Infinity loads (transformers weights); the QAT-q4 checkpoint
            # dequantized so it isn't GGUF-only like the Ollama tag was.
            "model_id": "embeddinggemma-q8",
            "similarity": "cosine",
        },
     },
    "mxbai": {
        "label": "mxbai-embed-large",
        "index": "english-mxbai",
        "inference_id": "mxbai-embed-large",
        "multilingual": False,
        "dims": 1024,  # mxbai-embed-large(-v1); used for inline chunks
        # ES inference endpoint — bound to the local Infinity server (query-time embedding).
        # Infinity exposes an OpenAI-compatible API; ES 8.16 has no native infinity service.
        "service": "openai",
        "service_settings": {
            "api_key": "infinity",  # Infinity doesn't require auth; ES requires a non-empty value
            "url": f"{_INFINITY_URL}/v1/embeddings",
            "model_id": "mixedbread-ai/mxbai-embed-large-v1",
            "similarity": "cosine",
        },
        # Optional remote inference for index time only. When set, the indexer
        # pre-computes vectors via the HF Dedicated Endpoint and ships them
        # inline in the bulk payload (semantic_text accepts pre-populated chunks
        # and skips its own inference call). Query time always goes through the
        # ES inference endpoint above (local Infinity server).
        "remote_inference": _build_remote_inference(_HF_DEDICATED_URL, "mxbai"),
    },
    "mxbai-xsmall": {
        "label": "mxbai-embed-xsmall",
        "index": "english-mxbai-xsmall",
        "inference_id": "mxbai-embed-xsmall",
        "multilingual": False,
        "dims": 384,  # mixedbread-ai/mxbai-embed-xsmall-v1; used for inline chunks
        # ES inference endpoint — bound to the local Infinity server (query-time embedding).
        # Infinity exposes an OpenAI-compatible API; ES 8.16 has no native infinity service.
        "service": "openai",
        "service_settings": {
            "api_key": "infinity",  # Infinity doesn't require auth; ES requires a non-empty value
            "url": f"{_INFINITY_URL}/v1/embeddings",
            "model_id": "mixedbread-ai/mxbai-embed-xsmall-v1",
            "similarity": "cosine",
        },
        # Optional remote inference for index time only — see note on mxbai above.
        # "remote_inference": _build_remote_inference(
        #     _HF_DEDICATED_URL_MXBAI_XSMALL, "mxbai-xsmall"
        # ),
    },
}

_ENABLED_MODELS = EMBEDDING_MODELS if SEMANTIC_ENABLED else {}

# Which model `/search?mode=semantic` picks when no `model=` param is given.
# Overridable via DEFAULT_SEMANTIC_MODEL env var so prod can switch the default
# without a code change; named (not first-dict-key) so adding a model doesn't
# silently change the default. Validated against the catalog so a typo fails
# fast at startup instead of KeyError-ing on the first semantic search.
DEFAULT_SEMANTIC_MODEL = os.environ.get(
    "DEFAULT_SEMANTIC_MODEL", "embeddinggemma-q8"
)
if DEFAULT_SEMANTIC_MODEL not in EMBEDDING_MODELS:
    raise ValueError(
        f"DEFAULT_SEMANTIC_MODEL={DEFAULT_SEMANTIC_MODEL!r} is not a known model; "
        f"valid: {sorted(EMBEDDING_MODELS)}"
    )


def _apply_prompt(model, kind, text):
    """Prepend the model's task prompt for `kind` ('query' or 'document').

    EmbeddingGemma is trained with asymmetric instruction prefixes; embedding raw
    text without them measurably hurts retrieval (see _EMBEDDINGGEMMA_PROMPTS).
    Models with no "prompts" entry (e.g. mxbai) are returned unchanged.
    """
    prompts = model.get("prompts") if model else None
    if not prompts:
        return text
    return f"{prompts[kind]}{text}"


# ── Shadow sampling ─────────────────────────────────────────────────────────
# Safe semantic rollout: on a random fraction of lexical-served queries, also
# run the semantic query in the background and persist both results + timings to
# the `search_metrics` table in a separate searchdb, for offline comparison.
# The served response is always the lexical one and is never delayed by this.
#
# Percent of lexical-served queries to shadow (0–100). 0 (or unset) = disabled,
# so the feature stays dark until explicitly turned on in prod.
SEARCH_METRICS_SAMPLE_PERCENT = _int_env("SEARCH_METRICS_SAMPLE_PERCENT", 0)
# Background worker pool size and a backlog cap: if semantic latency spikes, drop
# samples rather than let the queue (and memory) grow without bound. Sampling is
# best-effort telemetry — losing a few rows under load is fine.
_SHADOW_WORKERS = _int_env("SEARCH_METRICS_WORKERS", 2)
_SHADOW_MAX_INFLIGHT = _int_env("SEARCH_METRICS_MAX_INFLIGHT", 50)

# Separate searchdb (MySQL) holding `search_metrics`. Lowercase env var names
# match what's provisioned in prod (see .env.sample).
_SEARCHDB_CONFIG = {
    "host": os.environ.get("searchdb_host"),
    "user": os.environ.get("searchdb_username"),
    "password": os.environ.get("searchdb_password"),
    "database": os.environ.get("searchdb_name"),
}

# Bulk-indexing timeouts. Semantic bulk can be slow because ES embeds each
# doc against the inference endpoint (Infinity) unless we shipped inline chunks;
# lexical bulk is just text ingest and stays fast.
LEXICAL_BULK_TIMEOUT_S = 60
SEMANTIC_BULK_TIMEOUT_S = 300


class SearchMode(str, Enum):
    """Search mode for /search?mode=…. str mixin so equality with raw query
    strings and JSON serialization both produce the underlying value
    ('lexical' / 'semantic') without extra plumbing.
    """

    LEXICAL = "lexical"
    SEMANTIC = "semantic"


COLLECTION_BOOSTS = [
    ("bukhari", 5.0),
    ("muslim", 4.8),
    ("nasai", 3.5),
    ("abudawud", 3.0),
    ("tirmidhi", 2.5),
    ("ibnmajah", 2.0),
    ("malik", 2.5),
    ("ahmad", 2.5),
    ("darimi", 2.0),
    ("mishkat", 2.5),
    ("nawawi40", 3.3),
    ("riyadussalihin", 2.5),
]
