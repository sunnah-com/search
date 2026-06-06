import hashlib
import random
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException
import pymysql
import os
import json

from elasticsearch import Elasticsearch, helpers, BadRequestError, NotFoundError

from logger import access_log
from config import (
    COLLECTION_BOOSTS,
    DEFAULT_SEMANTIC_MODEL,
    EMBEDDING_MODELS,
    LEXICAL_BULK_TIMEOUT_S,
    LEXICAL_INDEX,
    QUERY_MAX_CHARS,
    SEARCH_METRICS_SAMPLE_PERCENT,
    SEMANTIC_BULK_TIMEOUT_S,
    SEMANTIC_ENABLED,
    SEMANTIC_FIELD,
    SearchMode,
    _ENABLED_MODELS,
    _SEARCHDB_CONFIG,
    _SHADOW_MAX_INFLIGHT,
    _SHADOW_WORKERS,
    _apply_prompt,
    _is_truthy,
)
from embedding import (
    _EMBED_CHECKPOINT_DIR,
    _open_checkpoint,
    _rewrite_inline_chunks,
)
from utils.shortcode_pattern import SHORTCODE_PATTERN
from utils.vector_checkpoint import list_checkpoints


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


# When enabled, logs one structured entry per query showing the routing
# decision: route taken, variant, whether the client mode was overridden.
# Set ROUTER_LOG=true in .env to turn on. Off by default.
ROUTER_LOG = _is_truthy(os.environ.get("ROUTER_LOG"))

# Shadow-sampling runtime (sizing constants live in config). The executor and
# backlog semaphore are live objects, so they're built here where the sampler
# that uses them lives.
_SHADOW_EXECUTOR = ThreadPoolExecutor(
    max_workers=_SHADOW_WORKERS, thread_name_prefix="shadow"
)
# Bound the in-flight backlog: a non-blocking acquire fails — and we drop the
# sample — once _SHADOW_MAX_INFLIGHT tasks are outstanding, instead of letting
# the executor queue (and memory) grow without bound under load.
_shadow_slots = threading.BoundedSemaphore(_SHADOW_MAX_INFLIGHT)


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


def _attach_semantic_field(paired, model):
    """Attach SEMANTIC_FIELD as plain text on each doc.

    ES then auto-embeds via the bound inference endpoint (Ollama) at bulk time,
    unless _rewrite_inline_chunks is called first to pre-populate the field
    with vectors from a remote provider.

    The model's document prompt (if any) is baked into the stored text here so it
    covers BOTH index paths uniformly — the remote embedder and ES→Ollama both
    read this field as their embedding input. SEMANTIC_FIELD is excluded from
    _source on every search response, so the prefix is never user-visible. It's
    applied after contentHash is computed (_content_hash skips SEMANTIC_FIELD), so
    it doesn't perturb incremental diffing — but changing a prompt later won't
    invalidate hashes, so re-embed via force_rebuild when prompts change.

    Empty/whitespace-only text is filtered at the SQL source, so by the time we
    get here every paired text is a non-empty string.
    """
    return [
        {**doc, SEMANTIC_FIELD: _apply_prompt(model, "document", text)}
        for doc, text in paired
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
    # Checkpoint lifecycle lives here (not in _rewrite_inline_chunks) so the
    # resume cache is only discarded once the bulk index + alias swap succeed;
    # the context manager always close()s it on the way out.
    with _open_checkpoint(model) as checkpoint:
        try:
            if model and model.get("remote_inference"):
                documents = _rewrite_inline_chunks(documents, model, checkpoint)
            success, errors = _bulk_index(documents, new_index, timeout=timeout)
            if success == 0:
                # Bulk wholesale-failed; keep the checkpoint so a retry resumes.
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
            # Index is live — vectors are durably in ES, so the cache is dead weight.
            checkpoint.discard()
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

    # Checkpoint lifecycle lives here (not in _rewrite_inline_chunks) so the
    # resume cache is only discarded once the bulk index actually succeeds; the
    # context manager always close()s it. No real cache unless there's something
    # to embed (passing model=None yields a no-op NullCheckpoint).
    timeout = SEMANTIC_BULK_TIMEOUT_S if model else LEXICAL_BULK_TIMEOUT_S
    success, errors = 0, []
    with _open_checkpoint(model if to_index else None) as checkpoint:
        if to_index and model and model.get("remote_inference"):
            to_index = _rewrite_inline_chunks(to_index, model, checkpoint)

        actions = to_index + [{"_op_type": "delete", "_id": did} for did in to_delete]
        if actions:
            success, errors = _bulk_index(actions, index_name, timeout=timeout)
        # Bulk completed — embedded vectors are durably in ES; drop the cache.
        checkpoint.discard()

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
    # Each SELECT's columns ARE a language's reconstruction payload  — the names match the website's EnglishHadith/ArabicHadith model
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
            arabicByMatchingEnglish[hadith["matchingEnglishURN"]] = ar_obj

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
        ar_obj = arabicByMatchingEnglish.get(hadith["englishURN"])
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
            paired = [(doc, doc["hadithText"]) for doc in englishHadiths]

        model_docs = _attach_semantic_field(paired, model)
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


def _index_language_counts(index):
    """Total + per-language doc counts for a live index/alias.

    `lang` is stored but not indexed, so we can't aggregate on it. Instead break
    down by which text field is present: a doc with hadithText carries an English
    side, one with arabicText carries an Arabic side. A bilingual doc has both
    and is counted under each — matching how it's actually searchable in either
    language, and why "lexical" legitimately reports both English and Arabic.
    """
    r = es_client.search(
        index=index,
        size=0,
        track_total_hits=True,
        aggregations={
            "english": {"filter": {"exists": {"field": "hadithText"}}},
            "arabic": {"filter": {"exists": {"field": "arabicText"}}},
        },
    )
    return {
        "count": r["hits"]["total"]["value"],
        "english": r["aggregations"]["english"]["doc_count"],
        "arabic": r["aggregations"]["arabic"]["doc_count"],
    }


def _temp_index_progress(index):
    """Live doc count + age of an in-flight `{base}-{ns}` rebuild index."""
    info = {"index": index}
    try:
        info["count"] = es_client.count(index=index)["count"]
        settings = es_client.indices.get_settings(index=index)
        created_ms = int(settings[index]["settings"]["index"]["creation_date"])
        info["age_seconds"] = round(time.time() - created_ms / 1000, 1)
    except Exception as e:  # index can vanish mid-call once a rebuild swaps in
        info["error"] = str(e)
    return info


def _index_build_status(base):
    """Status for one logical index, including any rebuild in progress.

    A rebuild bulk-loads a fresh `{base}-{ns}` index and only flips the `{base}`
    alias onto it at the very end (see _rebuild_index). So a concrete `{base}-*`
    index the alias doesn't yet point to is a build in progress (or an abandoned
    one) — surfaced under "building" with its climbing doc count.

    One `_alias` lookup over `{base}*` resolves both the live indices (those the
    `base` alias serves) and the in-flight ones in a single round-trip.
    """
    try:
        resolved = es_client.indices.get_alias(index=f"{base}*")
    except NotFoundError:
        resolved = {}
    live_indices = {idx for idx, meta in resolved.items() if base in meta["aliases"]}
    if not live_indices and base in resolved:
        live_indices = {base}  # plain index, not yet alias-backed
    building_indices = sorted(
        idx
        for idx in resolved
        if idx.startswith(f"{base}-") and idx not in live_indices
    )

    out = {"index": base, "indexed": bool(live_indices)}
    if live_indices:
        out["live_index"] = sorted(live_indices)
        out["incremental"] = _index_is_incremental(base)
        out.update(_index_language_counts(base))

    building = [_temp_index_progress(idx) for idx in building_indices]
    if building:
        out["building"] = building
    return out


def _checkpoint_status():
    """Resume caches on disk → an embed pass is in progress or was interrupted.

    A checkpoint file only exists between the start of a semantic build and its
    success (it's discarded on completion). During the embed phase the temp ES
    index exists but holds 0 docs, so the checkpoint's growing size is the
    progress signal; a stale mtime means a build died and the next run resumes.
    """
    out = []
    for index_name, path in list_checkpoints(_EMBED_CHECKPOINT_DIR):
        try:
            st = os.stat(path)
        except OSError:
            continue
        out.append(
            {
                "index": index_name,
                "size_bytes": st.st_size,
                "idle_seconds": round(time.time() - st.st_mtime, 1),
            }
        )
    return out


@app.route("/index/status", methods=["GET"])
def index_status():
    indexes = {"lexical": _index_build_status(LEXICAL_INDEX)}
    for key, model in EMBEDDING_MODELS.items():
        indexes[key] = _index_build_status(model["index"])
    return jsonify(
        {
            "semantic_enabled": SEMANTIC_ENABLED,
            "indexes": indexes,
            "checkpoints": _checkpoint_status(),
        }
    )


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


def _truncate_query(query):
    """Clip query text to QUERY_MAX_CHARS. Applied once when the request query is
    read, so it covers both the lexical and semantic paths (and the shadow
    sampler, which is handed the already-truncated query)."""
    if query is None or len(query) <= QUERY_MAX_CHARS:
        return query
    access_log.warning(
        "query_truncated",
        extra={"original_len": len(query), "max_chars": QUERY_MAX_CHARS},
    )
    return query[:QUERY_MAX_CHARS]


def build_semantic_query(query, filter_clauses):
    return {
        "bool": {
            "filter": filter_clauses,
            "must": [{"semantic": {"field": SEMANTIC_FIELD, "query": query}}],
        }
    }


_ARABIC_RE = re.compile(r"[؀-ۿ]")
# Ends with a number (with or without preceding text) — "bukhari 1", "abu dawud 200", "5", "42".
# Forces lexical: semantic returns 0/9 correct for reference-style lookups, and a bare
# number has no semantic content worth embedding.
_REF_RE = re.compile(r"(^|\s)\d+[a-z]?\s*$", re.IGNORECASE)
# Explicit boolean operators in ES query_string syntax.
# Semantic embeds AND/OR/NOT as plain text and ignores the logic — keep these on BM25.
_BOOL_RE = re.compile(r"\b(AND|OR|NOT)\b")

_LOG_ROUTE_VARIANT = {
    "phrase": "lexical_phrase",
    "arabic": "lexical_arabic",
    "reference": "lexical_reference",
}


def _route_query(query, mode):
    """Classify the query and return (route, variant, phrase_text).

    route       — "lexical" | mode (passes through for semantic/lexical)
    variant     — None | "phrase" | "arabic" | "reference"
    phrase_text — inner text when variant=="phrase", else None

    Rules (applied in order — earlier rules always win):
      1. Quoted (≥3 chars) → lexical phrase (match_phrase on hadithText + arabicText)
      2. Any Arabic character → lexical arabic BM25, full corpus
      3. Ends with a number (or IS a number) → lexical reference, forced off semantic
      4. Contains AND/OR/NOT → lexical BM25 (operator syntax, semantic ignores these)
      5. Otherwise → mode as requested (lexical BM25 or semantic)
    """
    q = query.strip()

    if len(q) >= 3 and q[0] == '"' and q[-1] == '"':
        return "lexical", "phrase", q[1:-1]

    if _ARABIC_RE.search(q):
        return "lexical", "arabic", None

    if _REF_RE.search(q):
        return "lexical", "reference", None

    if _BOOL_RE.search(q):
        return "lexical", None, None

    return mode, None, None


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
    query = _truncate_query(request.args.get("q"))
    filters = get_filter_from_args(request.args)
    mode = _resolve_mode(request.args)
    size = int(request.args.get("size", 10))

    route, variant, phrase_text = _route_query(query, mode)

    # English route restricts to docs that have hadithText (excludes Arabic-only docs).
    # lang is stored but not indexed, so we can't term-filter on it — exists on
    # hadithText is equivalent: English/bilingual docs always have it, Arabic-only never do.
    # Arabic variant skips this block to search the full corpus.
    if variant != "arabic" and language == "english":
        filters = filters + [{"exists": {"field": "hadithText"}}]

    if ROUTER_LOG:
        log_route = _LOG_ROUTE_VARIANT.get(variant) or ("semantic" if route == SearchMode.SEMANTIC else "lexical")
        # overridden = True when phrase/arabic/reference forced lexical despite mode=semantic
        overridden = route == "lexical" and mode == SearchMode.SEMANTIC
        access_log.info(
            "router_decision",
            extra={
                "request_id": getattr(g, "request_id", None),
                "query": query,
                "mode_requested": str(mode),
                "route": log_route,
                "variant": variant,
                "overridden": overridden,
            },
        )

    # ── Semantic path ──────────────────────────────────────────────────────────
    if route == SearchMode.SEMANTIC:
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
        return _semantic_search(model, query, filters)

    # ── Lexical paths ──────────────────────────────────────────────────────────

    # Phrase search: quoted query → match_phrase on hadithText + arabicText
    if variant == "phrase":
        try:
            result = es_client.search(
                index=LEXICAL_INDEX,
                from_=int(request.args.get("from", 0)),
                size=size,
                query={"function_score": {
                    "query": {"bool": {
                        "filter": filters,
                        "should": [
                            {"match_phrase": {"hadithText": phrase_text}},
                            {"match_phrase": {"arabicText": phrase_text}},
                        ],
                        "minimum_should_match": 1,
                    }},
                    "functions": [
                        {"filter": {"term": {"collection": name}}, "weight": w}
                        for name, w in COLLECTION_BOOSTS
                    ],
                    "score_mode": "sum",
                    "boost_mode": "sum",
                }},
                _source={"excludes": [SEMANTIC_FIELD]},
                highlight={"number_of_fragments": 0, "fields": {"*": {}}},
            )
        except (BadRequestError, NotFoundError) as e:
            return malformed_query_response(e)
        result.body["_meta"] = {"route": "lexical_phrase"}
        return jsonify(result.body)

    # Arabic BM25 and standard BM25 share the same cross-fields query structure.
    # arabicText is mapped with custom_arabic — query_string uses each field's own
    # analyzer automatically, so Arabic tokens get correct morphological analysis
    # without explicit annotation. The Arabic route skips the lang filter (full corpus)
    # and sets _meta.route: lexical_arabic; standard BM25 restricts to lang:en.
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
        "size": size,
        "_source": {"excludes": [SEMANTIC_FIELD]},
        "highlight": {"number_of_fragments": 0, "fields": {"*": {}}},
        "suggest": get_suggest_block(query),
    }
    lexical_start = time.perf_counter()
    try:
        try:
            result = es_client.search(query=build_lexical("query_string"), **kwargs)
        except BadRequestError:
            result = es_client.search(
                query=build_lexical("simple_query_string"), **kwargs
            )
    except BadRequestError as e:
        return malformed_query_response(e)
    lexical_ms = (time.perf_counter() - lexical_start) * 1000

    if variant == "arabic":
        result.body["_meta"] = {"route": "lexical_arabic"}
        return jsonify(result.body)

    _maybe_shadow_sample(
        query,
        filters,
        request.args.get("from", 0),
        size,
        result.body,
        lexical_ms,
    )
    route_tag = "lexical_reference" if variant == "reference" else "lexical"
    result.body.setdefault("_meta", {})["route"] = route_tag
    return jsonify(result.body)


def _execute_semantic_search(model, query, filters, from_, size):
    """Run the semantic ES query. Shared by the request route and the shadow
    sampler so the query shape (timeout, source excludes, suggest) lives once.

    The model's query prompt is applied only to the text ES embeds; the raw query
    still feeds get_suggest_block so spelling suggestions aren't built from the
    instruction prefix."""
    return es_client.options(request_timeout=130).search(
        index=model["index"],
        from_=int(from_),
        size=int(size),
        query=build_semantic_query(_apply_prompt(model, "query", query), filters),
        _source={"excludes": [SEMANTIC_FIELD]},
        suggest=get_suggest_block(query),
    )


def _semantic_search(model, query, filters):
    try:
        result = _execute_semantic_search(
            model,
            query,
            filters,
            request.args.get("from", 0),
            request.args.get("size", 10),
        )
    except BadRequestError as e:
        return malformed_query_response(e)
    result.body.setdefault("_meta", {})["route"] = "semantic"
    return jsonify(result.body)


# ── Shadow sampling ─────────────────────────────────────────────────────────


def _shadow_sampling_enabled():
    """True only when everything sampling needs is configured: a non-zero rate,
    semantic search enabled with at least one model, and searchdb credentials."""
    return (
        SEARCH_METRICS_SAMPLE_PERCENT > 0
        and SEMANTIC_ENABLED
        and bool(_ENABLED_MODELS)
        and all(_SEARCHDB_CONFIG.values())
    )


def _run_semantic_shadow(model, query, filters, from_, size):
    """Run the semantic query for comparison. Returns (result_body, elapsed_ms).

    Runs the same query as the request route (via _execute_semantic_search) but
    is request-context-free — it runs on a background thread, where Flask's
    `request`/`g` are gone, so all inputs are passed in.
    """
    t0 = time.perf_counter()
    result = _execute_semantic_search(model, query, filters, from_, size)
    return result.body, (time.perf_counter() - t0) * 1000


def _persist_search_metrics(
    query,
    lexical_results,
    lexical_ms,
    semantic_results,
    semantic_ms,
    model_name,
    routing_decision=None,
):
    """Insert one row into search_metrics. Opens a fresh connection per write —
    sampled volume is low, so a pool isn't worth the added lifecycle."""
    conn = pymysql.connect(charset="utf8mb4", **_SEARCHDB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO search_metrics
                       (query, lexical_results, lexical_query_time_ms,
                        semantic_results, semantic_query_time_ms,
                        semantic_model_name, routing_decision)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    query,
                    json.dumps(lexical_results, ensure_ascii=False, default=str),
                    round(lexical_ms, 3),
                    json.dumps(semantic_results, ensure_ascii=False, default=str),
                    round(semantic_ms, 3),
                    model_name,
                    routing_decision,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def _shadow_sample_task(query, filters, from_, size, lexical_body, lexical_ms):
    """Background task: run the semantic side and persist both results. Swallows
    every error — shadow telemetry must never affect the served request, and it
    already returned by the time this runs."""
    try:
        model = _ENABLED_MODELS[DEFAULT_SEMANTIC_MODEL]
        semantic_body, semantic_ms = _run_semantic_shadow(
            model, query, filters, from_, size
        )
        _persist_search_metrics(
            query,
            lexical_body,
            lexical_ms,
            semantic_body,
            semantic_ms,
            model["label"],
        )
    except Exception:
        access_log.exception("shadow_sample_failed", extra={"query": query})
    finally:
        _shadow_slots.release()


def _maybe_shadow_sample(query, filters, from_, size, lexical_body, lexical_ms):
    """Roll the dice on a lexical-served query and, if it wins, hand the semantic
    comparison off to the background pool. Returns immediately; never raises."""
    if not query or not _shadow_sampling_enabled():
        return
    if random.randint(1, 100) > SEARCH_METRICS_SAMPLE_PERCENT:
        return
    if not _shadow_slots.acquire(blocking=False):
        access_log.warning("shadow_sample_dropped")
        return
    try:
        _SHADOW_EXECUTOR.submit(
            _shadow_sample_task, query, filters, from_, size, lexical_body, lexical_ms
        )
    except RuntimeError:
        # Executor shutting down (e.g. interpreter exit) — release the slot.
        _shadow_slots.release()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
