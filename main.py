import hashlib
import logging
import socket
import sys
import time
import urllib.request
import urllib.error
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException
import pymysql
import os
from dotenv import load_dotenv
import json

from elasticsearch import Elasticsearch, helpers, BadRequestError, NotFoundError
from pythonjsonlogger import jsonlogger

from utils.rate_limiter import RateLimiter
from utils.shortcode_pattern import SHORTCODE_PATTERN

load_dotenv(".env.local")


_log_handler = logging.StreamHandler(sys.stdout)
_log_handler.setFormatter(
    jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
)
access_log = logging.getLogger("search.access")
access_log.setLevel(logging.INFO)
access_log.addHandler(_log_handler)
access_log.propagate = False


app = Flask(__name__)


@app.before_request
def _record_request_start():
    g.request_start = time.perf_counter()
    g.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex


@app.after_request
def _emit_access_log(response):
    duration_ms = (time.perf_counter() - g.request_start) * 1000
    access_log.info(
        "request",
        extra={
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
            "query": request.args.to_dict(flat=False),
            "user_agent": request.headers.get("User-Agent"),
        },
    )
    response.headers["X-Request-Id"] = g.request_id
    return response


es_auth = ("elastic", os.environ.get("ELASTIC_PASSWORD"))
es_base_url = f"http://elasticsearch:{os.environ.get('ES_PORT')}"
es_client = Elasticsearch(
    es_base_url,
    http_auth=es_auth,
    max_retries=3,
    retry_on_timeout=True,
    request_timeout=10,
)


def _is_truthy(value):
    return (value or "").lower() in ("1", "true", "yes")


# Pure lexical index — no embeddings, fast to rebuild.
LEXICAL_INDEX = "english-lexical"

# Each model gets its own ES index so you can index and switch independently.
# The semantic field is always called "semantic_text" inside each model's index.
SEMANTIC_FIELD = "semantic_text"

_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
_HUGGING_FACE_KEY = os.environ.get("HUGGING_FACE_KEY")
_HF_DEDICATED_URL = os.environ.get(
    "HF_DEDICATED_URL"
)  # e.g. https://<id>.endpoints.huggingface.cloud

# Embedding vector dimensions for mxbai-embed-large(-v1). Used for inline chunks.
_MXBAI_DIMS = 1024


def _build_remote_mxbai_inference():
    """Index-time embedding via a HuggingFace Inference Endpoint running TEI.

    The endpoint exposes an OpenAI-compatible /v1/embeddings route that returns
    L2-normalized vectors directly. Returns None (→ fall back to ES inference
    via Ollama at index time) when either env var is missing.
    """
    if not (_HUGGING_FACE_KEY and _HF_DEDICATED_URL):
        return None
    return {
        "url": f"{_HF_DEDICATED_URL.rstrip('/')}/v1/embeddings",
        "api_key": _HUGGING_FACE_KEY,
        "model_id": "mxbai",  # TEI ignores model field, but OpenAI shape requires it
        "dims": _MXBAI_DIMS,
    }


SEMANTIC_ENABLED = _is_truthy(os.environ.get("SEMANTIC_ENABLED"))

# Catalog of semantic models. Pure data — no env coupling. Add an entry here
# to register another model; the on/off switch lives on SEMANTIC_ENABLED above.
EMBEDDING_MODELS = {
    "mxbai": {
        "label": "mxbai-embed-large",
        "index": "english-mxbai",
        "inference_id": "mxbai-embed-large",
        "multilingual": False,
        # ES inference endpoint — always bound to local Ollama (query-time embedding).
        # Ollama exposes an OpenAI-compatible API; ES 8.16 has no native ollama service.
        "service": "openai",
        "service_settings": {
            "api_key": "ollama",  # Ollama doesn't require auth; ES requires a non-empty value
            "url": f"{_OLLAMA_URL}/v1/embeddings",
            "model_id": "mxbai-embed-large",
            "similarity": "cosine",
        },
        # Optional remote inference for index time only. When set, the indexer
        # pre-computes vectors via the HF Dedicated Endpoint and ships them
        # inline in the bulk payload (semantic_text accepts pre-populated chunks
        # and skips its own inference call). Query time always goes through the
        # ES inference endpoint above (local Ollama).
        "remote_inference": _build_remote_mxbai_inference(),
    },
}

_ENABLED_MODELS = EMBEDDING_MODELS if SEMANTIC_ENABLED else {}

# Which model `/search?mode=semantic` picks when no `model=` param is given.
# Set explicitly rather than reading the first dict key, so adding another
# semantic model doesn't accidentally change which one is the default.
DEFAULT_SEMANTIC_MODEL = "mxbai"

# Bulk-indexing timeouts. Semantic bulk can be slow because ES embeds each
# doc against the inference endpoint (Ollama) unless we shipped inline chunks;
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


@app.errorhandler(Exception)
def _handle_unexpected(exc):
    if isinstance(exc, HTTPException):
        return exc
    access_log.exception(
        "unhandled_exception",
        extra={
            "request_id": getattr(g, "request_id", None),
            "exception": type(exc).__name__,
        },
    )
    return jsonify({"error": "internal server error"}), 500


@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to sunnah.com search api.</h1>"


# ── Index management ──────────────────────────────────────────────────────────


def _ensure_inference_endpoint(model):
    try:
        es_client.inference.get(
            task_type="text_embedding", inference_id=model["inference_id"]
        )
        return
    except NotFoundError:
        pass
    es_client.options(request_timeout=60).inference.put(
        task_type="text_embedding",
        inference_id=model["inference_id"],
        inference_config={
            "service": model["service"],
            "service_settings": model["service_settings"],
        },
    )


def _content_hash(doc):
    payload = {
        k: v for k, v in doc.items() if k not in ("_id", "contentHash", SEMANTIC_FIELD)
    }
    encoded = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _prepare_documents(documents):
    for doc in documents:
        doc["_id"] = f"{doc['lang']}:{doc['urn']}"
        doc["contentHash"] = _content_hash(doc)


# HF's per-endpoint pool 429s well below TEI's max_concurrent_requests=512.
# batch_size × max_input_length must stay under TEI's max_batch_tokens (16384).
_REMOTE_EMBED_CONCURRENCY = int(os.environ.get("HF_DEDICATED_CONCURRENCY", "4"))
_REMOTE_EMBED_BATCH_SIZE = int(os.environ.get("HF_DEDICATED_BATCH_SIZE", "16"))
# -1 disables throttling; HF Dedicated bills by compute-time, not RPM.
_REMOTE_EMBED_RPM = int(os.environ.get("HF_DEDICATED_RPM", "-1"))
_REMOTE_EMBED_MAX_RETRIES = 6
_REMOTE_EMBED_BACKOFF_FLOOR_S = 5
# Cap server-supplied Retry-After so a misbehaving 503 can't park a worker.
_REMOTE_EMBED_BACKOFF_CEILING_S = 60


def _embed_via_remote(model, texts):
    """Batch-embed `texts` via the configured HF Dedicated Endpoint.

    Returns a list of float vectors aligned with input order. Retries on 429
    and transient 5xx with exponential backoff (Retry-After respected when
    ≥ floor). Captures the response body on non-retryable failures (e.g. 400
    "inputs cannot be empty") to make debugging easier.
    """
    cfg = model["remote_inference"]
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    limiter = RateLimiter(_REMOTE_EMBED_RPM, log=access_log)

    def _embed_batch(batch_texts):
        # OpenAI-shape body; TEI accepts the `truncate` field on /v1/embeddings
        # to silently handle inputs over max_input_length.
        payload = json.dumps(
            {"model": cfg["model_id"], "input": batch_texts, "truncate": True}
        ).encode("utf-8")
        for attempt in range(_REMOTE_EMBED_MAX_RETRIES):
            limiter.acquire()
            req = urllib.request.Request(
                cfg["url"], data=payload, headers=headers, method="POST"
            )

            status = None
            retry_after = None
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read())
                # TEI's /v1/embeddings returns OpenAI shape with L2-normalized vectors.
                return [item["embedding"] for item in body["data"]]
            except urllib.error.HTTPError as e:
                status = e.code
                retryable = e.code == 429 or 500 <= e.code < 600
                retry_after = e.headers.get("Retry-After")
                if not retryable or attempt == _REMOTE_EMBED_MAX_RETRIES - 1:
                    # Capture body for non-retryable failures so we can debug
                    # 400-class errors (oversize inputs, bad model id, etc.).
                    body_snippet = e.read()[:400].decode("utf-8", errors="replace")
                    access_log.error(
                        "remote_embed_failed",
                        extra={
                            "status": e.code,
                            "body": body_snippet,
                            "batch_size": len(batch_texts),
                        },
                    )
                    raise
            except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
                # DNS failure, connect refused, read timeout, RST mid-stream —
                # treat as transient and retry rather than killing the run.
                status = "network_error"
                if attempt == _REMOTE_EMBED_MAX_RETRIES - 1:
                    access_log.error(
                        "remote_embed_failed",
                        extra={
                            "status": status,
                            "reason": str(e),
                            "batch_size": len(batch_texts),
                        },
                    )
                    raise

            # Shared backoff path for any retryable failure above.
            parsed = (
                float(retry_after)
                if retry_after and retry_after.replace(".", "", 1).isdigit()
                else 0
            )
            # TEI sometimes returns Retry-After: 0 — enforce a floor so we don't
            # immediately re-fire. Cap Retry-After so a single misbehaving 503
            # can't park a worker for many minutes.
            wait = max(
                min(parsed, _REMOTE_EMBED_BACKOFF_CEILING_S),
                _REMOTE_EMBED_BACKOFF_FLOOR_S,
                min(2**attempt, 30),
            )
            access_log.warning(
                "remote_embed_retry",
                extra={"status": status, "attempt": attempt + 1, "wait_s": wait},
            )
            time.sleep(wait)

    batches = [
        texts[i : i + _REMOTE_EMBED_BATCH_SIZE]
        for i in range(0, len(texts), _REMOTE_EMBED_BATCH_SIZE)
    ]
    out = [None] * len(batches)
    with ThreadPoolExecutor(max_workers=_REMOTE_EMBED_CONCURRENCY) as ex:
        future_to_idx = {ex.submit(_embed_batch, b): i for i, b in enumerate(batches)}
        # as_completed yields futures in completion order, so a single slow batch
        # doesn't idle workers that finished after it but were submitted earlier.
        for f in as_completed(future_to_idx):
            out[future_to_idx[f]] = f.result()
    return [v for batch in out for v in batch]


def _attach_semantic_field(paired):
    """Attach SEMANTIC_FIELD as plain text on each doc.

    ES then auto-embeds via the bound inference endpoint (Ollama) at bulk time,
    unless _rewrite_inline_chunks is called first to pre-populate the field
    with vectors from a remote provider.

    Empty/whitespace-only text is filtered at the SQL source, so by the time we
    get here every paired text is a non-empty string.
    """
    return [{**doc, SEMANTIC_FIELD: text} for doc, text in paired]


def _inline_chunk_doc(doc, text, vec, inference_id, model_settings):
    """Build the doc shape ES's semantic_text accepts when bypassing inference."""
    return {
        **doc,
        SEMANTIC_FIELD: {
            "text": text,
            "inference": {
                "inference_id": inference_id,
                "model_settings": model_settings,
                "chunks": [{"text": text, "embeddings": vec}],
            },
        },
    }


def _rewrite_inline_chunks(docs, model):
    """Replace each doc's plain-text SEMANTIC_FIELD with the full inline-chunks
    structure, with vectors fetched from the model's remote inference API.

    Called only on docs about to be bulk-sent (after incremental diffing) so we
    don't burn API quota embedding unchanged docs.
    """
    remote = model["remote_inference"]
    texts = [doc[SEMANTIC_FIELD] for doc in docs]

    access_log.info(
        "remote_embed_start",
        extra={
            "model": model["label"],
            "doc_count": len(texts),
            "batch_size": _REMOTE_EMBED_BATCH_SIZE,
            "concurrency": _REMOTE_EMBED_CONCURRENCY,
            "rpm": _REMOTE_EMBED_RPM,
        },
    )
    t0 = time.time()
    vectors = _embed_via_remote(model, texts)
    access_log.info(
        "remote_embed_done",
        extra={
            "model": model["label"],
            "doc_count": len(texts),
            "duration_s": round(time.time() - t0, 1),
        },
    )

    model_settings = {
        "task_type": "text_embedding",
        "dimensions": remote["dims"],
        "similarity": "cosine",
        "element_type": "float",
    }
    return [
        _inline_chunk_doc(doc, text, vec, model["inference_id"], model_settings)
        for doc, text, vec in zip(docs, texts, vectors)
    ]


def _bulk_index(actions, index, timeout):
    return helpers.bulk(
        es_client,
        actions,
        index=index,
        request_timeout=timeout,
        raise_on_error=False,
        raise_on_exception=False,
    )


def _index_is_incremental(index_name):
    """True if the index has a contentHash field (built by this indexer)."""
    try:
        mapping = es_client.indices.get_mapping(index=index_name)
    except NotFoundError:
        return False
    return all(
        "contentHash" in idx.get("mappings", {}).get("properties", {})
        for idx in mapping.values()
    )


def _make_settings():
    return {
        "index": {
            "number_of_shards": 1,
            "search.slowlog.threshold.query.warn": "1s",
            "search.slowlog.threshold.query.info": "500ms",
            "search.slowlog.threshold.fetch.warn": "500ms",
            "analysis": {
                "analyzer": {
                    "trigram": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip", "shortcode_strip"],
                        "filter": ["lowercase", "stop", "shingle"],
                    },
                    "synonym": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip", "shortcode_strip"],
                        "filter": ["lowercase", "stop", "synonyms_filter", "stemmer"],
                    },
                    "custom_arabic": {
                        "tokenizer": "standard",
                        "char_filter": ["html_strip", "shortcode_strip"],
                        "filter": [
                            "lowercase",
                            "decimal_digit",
                            "arabic_normalization",
                            "arabic_stemmer",
                            "shingle",
                        ],
                    },
                },
                "char_filter": {
                    "shortcode_strip": {
                        "type": "pattern_replace",
                        "pattern": SHORTCODE_PATTERN,
                        "replacement": " ",
                    }
                },
                "filter": {
                    "shingle": {
                        "type": "shingle",
                        "min_shingle_size": 2,
                        "max_shingle_size": 3,
                        "output_unigrams": True,
                    },
                    "synonyms_filter": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "synonyms.txt",
                    },
                    "arabic_stemmer": {"type": "stemmer", "language": "arabic"},
                    "arabic_stop": {"type": "stop", "stopwords": "_arabic_"},
                },
            },
        }
    }


def _make_mappings(non_indexed_fields, model=None):
    props = {field: {"type": "text", "index": False} for field in non_indexed_fields}
    props["hadithText"] = {
        "type": "text",
        "analyzer": "synonym",
        "fields": {"trigram": {"type": "text", "analyzer": "trigram"}},
    }
    props["arabicText"] = {"type": "text", "analyzer": "custom_arabic"}
    props["contentHash"] = {"type": "keyword", "index": False}
    # Reconstruction payloads: kept in _source, kept out of the index entirely.
    props["en"] = {"type": "object", "enabled": False}
    props["ar"] = {"type": "object", "enabled": False}
    if model:
        props[SEMANTIC_FIELD] = {
            "type": "semantic_text",
            "inference_id": model["inference_id"],
        }
    return {"properties": props}


def _rebuild_index(index_name, documents, non_indexed_fields, model=None):
    # time_ns avoids collisions when two rebuilds land in the same second.
    new_index = f"{index_name}-{time.time_ns()}"
    timeout = SEMANTIC_BULK_TIMEOUT_S if model else LEXICAL_BULK_TIMEOUT_S
    es_client.indices.create(
        index=new_index,
        mappings=_make_mappings(non_indexed_fields, model),
        settings=_make_settings(),
    )
    try:
        if model and model.get("remote_inference"):
            documents = _rewrite_inline_chunks(documents, model)
        success, errors = _bulk_index(documents, new_index, timeout=timeout)
        if success == 0:
            es_client.indices.delete(index=new_index, ignore_unavailable=True)
            return {"mode": "rebuild", "success_count": 0, "errors": errors}

        old_indices = []
        if es_client.indices.exists_alias(name=index_name):
            old_indices = list(es_client.indices.get_alias(name=index_name).keys())
        elif es_client.indices.exists(index=index_name):
            es_client.indices.delete(index=index_name)

        actions = [{"add": {"index": new_index, "alias": index_name}}]
        for old in old_indices:
            actions.append({"remove": {"index": old, "alias": index_name}})
        es_client.indices.update_aliases(actions=actions)
        for old in old_indices:
            es_client.indices.delete(index=old, ignore_unavailable=True)
    except Exception:
        es_client.indices.delete(index=new_index, ignore_unavailable=True)
        raise

    return {"mode": "rebuild", "success_count": success, "errors": errors}


def _incremental_index(index_name, documents, model=None):
    incoming = {doc["_id"]: doc for doc in documents}
    if not incoming:
        # Refuse to wipe the live index when the source returns nothing
        # (transient DB failure, wrong DATABASE env, etc.).
        return {
            "mode": "incremental",
            "indexed": 0,
            "deleted": 0,
            "unchanged": 0,
            "success_count": 0,
            "errors": ["source returned 0 documents — refusing to delete live index"],
        }
    existing_hashes = {}
    for hit in helpers.scan(
        es_client, index=index_name, query={"_source": ["contentHash"]}, size=2000
    ):
        existing_hashes[hit["_id"]] = hit["_source"].get("contentHash")

    to_index = [
        doc
        for doc_id, doc in incoming.items()
        if existing_hashes.get(doc_id) != doc["contentHash"]
    ]
    to_delete = [doc_id for doc_id in existing_hashes if doc_id not in incoming]

    if to_index and model and model.get("remote_inference"):
        to_index = _rewrite_inline_chunks(to_index, model)

    actions = to_index + [{"_op_type": "delete", "_id": did} for did in to_delete]

    timeout = SEMANTIC_BULK_TIMEOUT_S if model else LEXICAL_BULK_TIMEOUT_S
    success, errors = 0, []
    if actions:
        success, errors = _bulk_index(actions, index_name, timeout=timeout)

    return {
        "mode": "incremental",
        "indexed": len(to_index),
        "deleted": len(to_delete),
        "unchanged": len(incoming) - len(to_index),
        "success_count": success,
        "errors": errors,
    }


def _index_one(
    index_name, documents, non_indexed_fields, model=None, force_rebuild=False
):
    """Rebuild or incrementally update a single index."""
    if force_rebuild or not _index_is_incremental(index_name):
        return _rebuild_index(index_name, documents, non_indexed_fields, model)
    return _incremental_index(index_name, documents, model)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.route("/index", methods=["GET"])
def index():
    start = time.time()
    if request.args.get("password") != os.environ.get("INDEXING_PASSWORD"):
        return "Must provide valid password to index", 401

    force_rebuild = _is_truthy(request.args.get("rebuild"))

    # ?targets=… is a comma-separated subset of {lexical, <each enabled model>}.
    # Missing → build everything. Empty or unknown → 400 (don't silently
    # misinterpret a typo as "do nothing" or "do everything").
    valid_targets = {"lexical", *_ENABLED_MODELS}
    raw_targets = request.args.get("targets")
    if raw_targets is None:
        targets = valid_targets
    else:
        targets = {t.strip() for t in raw_targets.split(",") if t.strip()}
        if not targets:
            return jsonify(
                {"error": "targets= must be a non-empty comma-separated list"}
            ), 400
        unknown = targets - valid_targets
        if unknown:
            return jsonify(
                {
                    "error": f"unknown targets {sorted(unknown)}; "
                    f"valid: {sorted(valid_targets)}"
                }
            ), 400

    connection = pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE"),
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    # Filter out empty rows at the source so the rest of the pipeline doesn't
    # have to handle them — TEI rejects empty inputs, ES wastes an _id storing
    # them, and a hadith with no text can't match any query anyway.
    #
    # Each SELECT's columns ARE a language's reconstruction payload (`dict(r)`
    # below) — the names match the website's EnglishHadith/ArabicHadith model
    # properties, so keep them in sync. bookID is DECIMAL — cast to CHAR so it
    # JSON-serializes and matches how the website keys books ("1.0").
    cursor.execute(
        """SELECT arabicURN, collection, volumeNumber, bookNumber, hadithNumber,
                    hadithText, CAST(bookID AS CHAR) AS bookID, grade1,
                    ourHadithNumber, matchingEnglishURN
                  FROM ArabicHadithTable
                  WHERE hadithText IS NOT NULL AND TRIM(hadithText) != ''"""
    )
    arabicRows = cursor.fetchall()

    # One doc per Arabic hadith; index the `ar` payload by matching English URN
    # so the English pass can fold paired hadiths into one bilingual doc.
    arabicHadiths = []
    arabicOnlyHadiths = []
    arabicByMatchingEnglish = {}
    for hadith in arabicRows:
        ar_obj = dict(hadith)
        doc = {
            "lang": "ar",
            "urn": hadith["arabicURN"],
            "collection": hadith["collection"],
            "hadithNumber": hadith["hadithNumber"],
            "arabicText": hadith["hadithText"],
            "grade": hadith["grade1"],
            "ar": ar_obj,
        }
        arabicHadiths.append(doc)
        if hadith["matchingEnglishURN"] == 0:
            arabicOnlyHadiths.append(doc)
        else:
            arabicByMatchingEnglish[r["matchingEnglishURN"]] = ar_obj

    cursor.execute(
        """SELECT englishURN, collection, volumeNumber, bookNumber, hadithNumber,
                    hadithText, CAST(bookID AS CHAR) AS bookID, grade1,
                    ourHadithNumber, matchingArabicURN
                  FROM EnglishHadithTable
                  WHERE hadithText IS NOT NULL AND TRIM(hadithText) != ''"""
    )
    englishRows = cursor.fetchall()

    englishHadiths = []
    for hadith in englishRows:
        doc = {
            "lang": "en",
            "urn": hadith["englishURN"],
            "collection": hadith["collection"],
            "hadithText": hadith["hadithText"],
            "grade": hadith["grade1"],
            "en": dict(hadith),
        }
        # Fold in the matching Arabic side → one bilingual doc. Arabic
        # hadithNumber stays top-level to preserve search ranking (hadithNumber^2).
        ar_obj = arabicByMatchingEnglish.get(r["englishURN"])
        if ar_obj is not None:
            doc["arabicText"] = ar_obj["hadithText"]
            doc["hadithNumber"] = ar_obj["hadithNumber"]
            doc["ar"] = ar_obj
        englishHadiths.append(doc)

    connection.close()

    non_indexed = ["urn", "lang"]

    # Prepare IDs and content hashes. arabicHadiths is a superset of arabicOnlyHadiths
    # (same dict objects), so preparing arabicHadiths covers both.
    _prepare_documents(arabicHadiths)
    _prepare_documents(englishHadiths)

    # Lexical index: English + Arabic-only (avoids duplicate hits for paired hadiths).
    lexical_docs = englishHadiths + arabicOnlyHadiths

    # Semantic index: full multilingual corpus — every Arabic doc gets its Arabic text
    # embedded, every English doc gets its English text embedded. This lets a multilingual
    # model like text-embedding-3-small retrieve across both languages from one index.
    results = {}
    if "lexical" in targets:
        results["lexical"] = _index_one(
            LEXICAL_INDEX,
            lexical_docs,
            non_indexed,
            model=None,
            force_rebuild=force_rebuild,
        )
    models_to_index = {k: v for k, v in _ENABLED_MODELS.items() if k in targets}
    for model_key, model in models_to_index.items():
        _ensure_inference_endpoint(model)
        if model.get("multilingual"):
            # Full corpus: every Arabic doc embeds Arabic text, every English doc embeds English.
            en_docs = [(doc, doc["hadithText"]) for doc in englishHadiths]
            ar_docs = [(doc, doc["arabicText"]) for doc in arabicHadiths]
            paired = en_docs + ar_docs
        else:
            # English-only — replicates colleague's original PR approach.
            paired = [(doc, doc["hadithText"]) for doc in englishHadiths]

        model_docs = _attach_semantic_field(paired)
        results[model_key] = _index_one(
            model["index"],
            model_docs,
            non_indexed,
            model=model,
            force_rebuild=force_rebuild,
        )
        results[model_key]["failed"] = json.dumps(results[model_key].pop("errors"))

    if "lexical" in results:
        results["lexical"]["failed"] = json.dumps(results["lexical"].pop("errors"))

    results["arabic_only_count"] = len(arabicOnlyHadiths)
    results["timeInSeconds"] = round(time.time() - start, 1)
    return jsonify(results)


@app.route("/index/status", methods=["GET"])
def index_status():
    out = {}
    for index_name in [LEXICAL_INDEX] + [m["index"] for m in EMBEDDING_MODELS.values()]:
        try:
            r = es_client.search(index=index_name, size=0, track_total_hits=True)
            out[index_name] = {"indexed": True, "count": r["hits"]["total"]["value"]}
        except NotFoundError:
            out[index_name] = {"indexed": False}
    return jsonify(out)


# ── Search helpers ────────────────────────────────────────────────────────────


def get_suggest_query(field):
    return {
        "field": field,
        "size": 3,
        "gram_size": 3,
        "direct_generator": [{"field": field, "suggest_mode": "missing"}],
        "highlight": {"pre_tag": "<em>", "post_tag": "</em>"},
        "collate": {
            "query": {"source": {"match": {field: "{{suggestion}}"}}},
            "prune": False,
        },
    }


def get_suggest_block(query):
    return {
        "text": query,
        "english": {"phrase": get_suggest_query("hadithText.trigram")},
        "arabic": {"phrase": get_suggest_query("arabicText")},
    }


def build_semantic_query(query, filter_clauses):
    return {
        "bool": {
            "filter": filter_clauses,
            "must": [{"semantic": {"field": SEMANTIC_FIELD, "query": query}}],
        }
    }


def get_filter_from_args(args):
    filters = []
    if collection := args.getlist("collection"):
        filters.append({"terms": {"collection": collection}})
    if grade := args.getlist("grade"):
        filters.append({"terms": {"grade": grade}})
    return filters


def _resolve_mode(args):
    """Normalize ?mode=... to a SearchMode. Falls back to LEXICAL for unknown
    values and whenever SEMANTIC_ENABLED is off.
    """
    try:
        mode = SearchMode((args.get("mode") or "").lower())
    except ValueError:
        return SearchMode.LEXICAL
    if mode == SearchMode.SEMANTIC and not SEMANTIC_ENABLED:
        return SearchMode.LEXICAL
    return mode


def _resolve_model_key(args):
    """Returns (key, error_message). error_message is non-None for explicit invalid input."""
    key = args.get("model") or DEFAULT_SEMANTIC_MODEL
    if key in _ENABLED_MODELS:
        return key, None
    return None, f"unknown model '{key}'; enabled: {sorted(_ENABLED_MODELS)}"


def malformed_query_response(exc):
    access_log.warning(
        "malformed_query",
        extra={"request_id": getattr(g, "request_id", None), "detail": str(exc)},
    )
    return jsonify({"error": "malformed query"}), 400


@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    filters = get_filter_from_args(request.args)
    mode = _resolve_mode(request.args)

    if mode == SearchMode.SEMANTIC:
        model_key, err = _resolve_model_key(request.args)
        if err:
            return jsonify({"error": err}), 400
        model = _ENABLED_MODELS[model_key]
        access_log.info(
            "semantic_search",
            extra={
                "request_id": getattr(g, "request_id", None),
                "mode": mode,
                "model": model_key,
                "query": query,
            },
        )
        return _semantic_search(model["index"], query, filters)

    # Lexical path
    fields = ["hadithNumber^2", "hadithText", "arabicText", "collection^2"]

    def build_lexical(query_type):
        inner = {"query": query, "fields": fields}
        if query_type == "query_string":
            inner["type"] = "cross_fields"
        return {
            "function_score": {
                "query": {"bool": {"filter": filters, "must": [{query_type: inner}]}},
                "functions": [
                    {"filter": {"term": {"collection": name}}, "weight": w}
                    for name, w in COLLECTION_BOOSTS
                ],
                "score_mode": "sum",
                "boost_mode": "sum",
            }
        }

    kwargs = {
        "index": LEXICAL_INDEX,
        "from_": request.args.get("from", 0),
        "size": request.args.get("size", 10),
        "_source": {"excludes": [SEMANTIC_FIELD]},
        "highlight": {"number_of_fragments": 0, "fields": {"*": {}}},
        "suggest": get_suggest_block(query),
    }
    try:
        try:
            result = es_client.search(query=build_lexical("query_string"), **kwargs)
        except BadRequestError:
            result = es_client.search(
                query=build_lexical("simple_query_string"), **kwargs
            )
    except BadRequestError as e:
        return malformed_query_response(e)
    return jsonify(result.body)


def _semantic_search(search_index, query, filters):
    try:
        result = es_client.options(request_timeout=130).search(
            index=search_index,
            from_=int(request.args.get("from", 0)),
            size=int(request.args.get("size", 10)),
            query=build_semantic_query(query, filters),
            _source={"excludes": [SEMANTIC_FIELD]},
            suggest=get_suggest_block(query),
        )
    except BadRequestError as e:
        return malformed_query_response(e)
    return jsonify(result.body)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
