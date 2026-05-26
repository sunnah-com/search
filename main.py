import hashlib
import logging
import sys
import time
import uuid
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException
import pymysql
import os
from dotenv import load_dotenv
import math
import json

from elasticsearch import Elasticsearch, helpers, BadRequestError, NotFoundError
from pythonjsonlogger import jsonlogger

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
    """Parse an env var / query param flag the same way everywhere."""
    return (value or "").lower() in ("1", "true", "yes")


INDEX_NAME = "english"

SEMANTIC_ENABLED = _is_truthy(os.environ.get("SEMANTIC_SEARCH_ENABLED"))
SEMANTIC_FIELD = "hadithTextSemantic"
# Per-doc content hash; an incremental reindex diffs against it. See _content_hash.
CONTENT_HASH_FIELD = "contentHash"
INFERENCE_ENDPOINT = "openai-text-embedding"
# helpers.bulk timeout. With semantic_text in the mapping each doc triggers an
# OpenAI embedding call during indexing, so the request needs far longer than a
# plain bulk. Indexing stays single-stream on purpose: OpenAI's tokens-per-minute
# quota is the ceiling, so fanning out across threads just trips 429s.
BULK_REQUEST_TIMEOUT = 300 if SEMANTIC_ENABLED else 60
# RRF constants. k=60 is the value from the original Cormack et al. paper and
# the ES default. RRF_WINDOW is the depth fetched from each retriever before
# fusion — bigger window = better recall at the tail, more cost per query.
RRF_K = 60
RRF_WINDOW = 100

# Search modes. SEMANTIC_MODES are the ones needing the inference endpoint —
# kept as one tuple so the "needs the semantic backend" rule has a single
# source of truth across mode resolution and request dispatch.
SEARCH_MODES = ("lexical", "hybrid", "semantic")
SEMANTIC_MODES = ("hybrid", "semantic")

# Tiebreaker boosts added on top of the text-similarity score so canonical
# collections rise when relevance is otherwise comparable. Sized to swing
# rankings when BM25 scores are within a few points (e.g. the same hadith
# narrated across collections), but still let a clearly stronger text match
# from a less canonical collection win.
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


def create_inference_endpoint():
    """Create the OpenAI text-embedding inference endpoint used by the
    semantic_text field, only if it doesn't already exist.

    Kept stable across re-indexes: the alias swap builds a new index while the
    old one keeps serving traffic, and both reference this endpoint by id —
    force-deleting it mid-reindex would break the live index's semantic field.
    To change the model or dimensions, delete the endpoint manually so the
    next reindex recreates it."""
    try:
        es_client.inference.get(
            task_type="text_embedding", inference_id=INFERENCE_ENDPOINT
        )
        return
    except NotFoundError:
        pass
    es_client.options(request_timeout=60).inference.put(
        task_type="text_embedding",
        inference_id=INFERENCE_ENDPOINT,
        inference_config={
            "service": "openai",
            "service_settings": {
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "model_id": "text-embedding-3-small",
                # OpenAI vectors are mathematically unit-length but drift past
                # ES's strict epsilon for a small fraction of inputs, breaking
                # the default dot_product similarity. See elastic/elasticsearch#122878.
                "similarity": "cosine",
            },
        },
    )


def _content_hash(doc):
    """Stable hash of a document's content. Covers every field except the id,
    the hash itself, and the semantic field (a verbatim copy of hadithText, so
    already captured). Any source change flips the hash and the doc is
    re-indexed — which, for the semantic field, means re-embedded."""
    payload = {
        k: v
        for k, v in doc.items()
        if k not in ("_id", CONTENT_HASH_FIELD, SEMANTIC_FIELD)
    }
    encoded = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _prepare_documents(documents):
    """Assign each doc a deterministic _id and a content hash, in place. The
    _id namespaces urn by language because the English and Arabic URN spaces
    overlap; it lets a reindex match an incoming doc to its indexed copy."""
    for doc in documents:
        doc["_id"] = f"{doc['lang']}:{doc['urn']}"
        doc[CONTENT_HASH_FIELD] = _content_hash(doc)


def _bulk_index(actions, index):
    """helpers.bulk with the project's standard flags: a timeout long enough
    for the semantic_text embedding calls, and errors collected per-doc rather
    than raised so a partial failure still reports."""
    return helpers.bulk(
        es_client,
        actions,
        index=index,
        request_timeout=BULK_REQUEST_TIMEOUT,
        raise_on_error=False,
        raise_on_exception=False,
    )


def _index_supports_incremental():
    """True if the live index was built by the current indexer — detected by
    the content-hash field in its mapping. An older index lacks it (and has
    non-deterministic ids), so it must be rebuilt before incremental diffing
    can work; until then a reindex would churn the whole corpus."""
    try:
        mapping = es_client.indices.get_mapping(index=INDEX_NAME)
    except NotFoundError:
        return False
    if not mapping:
        return False
    return all(
        CONTENT_HASH_FIELD in index_def.get("mappings", {}).get("properties", {})
        for index_def in mapping.values()
    )


def create_and_update_index(documents, fields_to_not_index):
    settings = {
        "index": {
            "number_of_shards": 1,
            "search.slowlog.threshold.query.warn":  "1s",
            "search.slowlog.threshold.query.info":  "500ms",
            "search.slowlog.threshold.fetch.warn":  "500ms",
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
                        "filter": [
                            "lowercase",
                            "stop",
                            "synonyms_filter",
                            "stemmer",
                        ],
                    },
                    "custom_arabic": {
                        "tokenizer":  "standard",
                        "char_filter": ["html_strip", "shortcode_strip"],
                        "filter": [
                            "lowercase",
                            "decimal_digit",
                            "arabic_normalization",
                            "arabic_stemmer",
                            "shingle"
                        ]
                    }
                },
                "char_filter": {
                    "shortcode_strip": {
                        "type": "pattern_replace",
                        "pattern": SHORTCODE_PATTERN,
                        "replacement": " ",
                    }
                },
                "filter": {
                    # 2-3 word shingles for better suggestions
                    "shingle": {
                        "type": "shingle",
                        "min_shingle_size": 2,
                        "max_shingle_size": 3,
                        "output_unigrams": True
                    },
                    "synonyms_filter": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "synonyms.txt",
                    },
                    "arabic_stemmer": {
                        "type":       "stemmer",
                        "language":   "arabic"
                    },
                    "arabic_stop": {
                        "type":       "stop",
                        "stopwords":  "_arabic_" 
                    },
                },
            },
        }
    }
    mappings = {
        "properties": {
            field: {"type": "text", "index": False} for field in fields_to_not_index
        }
        |
        # Configurating field for suggestions
        {
            "hadithText": {
                "type": "text",
                "analyzer": "synonym",
                "fields": {
                    "trigram": {"type": "text", "analyzer": "trigram"},
                },
            }
        }
        | {"arabicText": {"type": "text", "analyzer": "custom_arabic"}}
    }
    if SEMANTIC_ENABLED:
        mappings["properties"][SEMANTIC_FIELD] = {
            "type": "semantic_text",
            "inference_id": INFERENCE_ENDPOINT,
        }
    mappings["properties"][CONTENT_HASH_FIELD] = {"type": "keyword", "index": False}
    # Zero-downtime reindex: build into a fresh concrete index, then atomically
    # repoint the INDEX_NAME alias at it. Searches keep hitting the old index
    # until the swap, so there's no NotFoundError window. The previous
    # delete-then-recreate caused ~2-3 min of downtime.
    new_index = f"{INDEX_NAME}-{int(time.time())}"
    es_client.indices.create(index=new_index, mappings=mappings, settings=settings)

    _prepare_documents(documents)
    successCount, errors = _bulk_index(documents, new_index)
    result = {"mode": "rebuild", "success_count": successCount, "errors": errors}

    # Don't swap an empty/failed build over a working index.
    if successCount == 0:
        es_client.indices.delete(index=new_index, ignore_unavailable=True)
        return result

    # Find whatever currently serves the alias so we can retire it after the swap.
    old_indices = []
    if es_client.indices.exists_alias(name=INDEX_NAME):
        old_indices = list(es_client.indices.get_alias(name=INDEX_NAME).keys())
    elif es_client.indices.exists(index=INDEX_NAME):
        # Legacy concrete index occupying the alias name (pre-alias deploys).
        # It must go before an alias of the same name can exist — one-time,
        # brief gap on the first reindex after this change ships.
        es_client.indices.delete(index=INDEX_NAME)

    # Atomic alias swap: add new + remove old in a single cluster action.
    actions = [{"add": {"index": new_index, "alias": INDEX_NAME}}]
    for old in old_indices:
        actions.append({"remove": {"index": old, "alias": INDEX_NAME}})
    es_client.indices.update_aliases(actions=actions)

    for old in old_indices:
        es_client.indices.delete(index=old, ignore_unavailable=True)

    return result


def incremental_update_index(documents):
    """Reindex by diffing against the live index instead of rebuilding it.

    Each incoming doc carries a content hash; we fetch the stored hashes from
    the live index and only touch what changed:
      - new / changed docs are re-indexed (and, for the semantic field,
        re-embedded — the only OpenAI calls made)
      - docs no longer in the source are deleted
      - unchanged docs are left untouched

    Hadith text is near-static, so a typical run embeds a handful of docs
    rather than the whole corpus — sidestepping the OpenAI rate limit a full
    rebuild hits. Updates apply in place and atomically per doc, so there's no
    downtime and no alias swap. A mapping/analysis change still needs a full
    rebuild (use ?rebuild=true)."""
    _prepare_documents(documents)
    incoming = {doc["_id"]: doc for doc in documents}

    # Pull just {_id: contentHash} for every indexed doc — no _source bodies,
    # so this stays cheap even for the full corpus.
    existing_hashes = {}
    for hit in helpers.scan(
        es_client,
        index=INDEX_NAME,
        query={"_source": [CONTENT_HASH_FIELD]},
        size=2000,
    ):
        existing_hashes[hit["_id"]] = hit["_source"].get(CONTENT_HASH_FIELD)

    to_index = [
        doc
        for doc_id, doc in incoming.items()
        if existing_hashes.get(doc_id) != doc[CONTENT_HASH_FIELD]
    ]
    to_delete = [doc_id for doc_id in existing_hashes if doc_id not in incoming]

    actions = to_index + [
        {"_op_type": "delete", "_id": doc_id} for doc_id in to_delete
    ]
    success_count, errors = 0, []
    if actions:
        success_count, errors = _bulk_index(actions, INDEX_NAME)
    return {
        "mode": "incremental",
        "indexed": len(to_index),
        "deleted": len(to_delete),
        "unchanged": len(incoming) - len(to_index),
        "success_count": success_count,
        "errors": errors,
    }


def get_suggest_query(suggest_field):
    return {
        "field": suggest_field,
        "size": 3,
        "gram_size": 3,
        "direct_generator": [
            {"field": suggest_field, "suggest_mode": "missing"}
        ],
        "highlight": {"pre_tag": "<em>", "post_tag": "</em>"},
        "collate": {
            "query": {
                "source": {
                    "match": {suggest_field: "{{suggestion}}"}
                }
            },
            # Only return suggestions with a query match
            "prune": False,
        },
    }


def get_suggest_block(query):
    """Phrase-suggester ("did you mean") block covering English + Arabic text."""
    return {
        "text": query,
        "english": {"phrase": get_suggest_query("hadithText.trigram")},
        "arabic": {"phrase": get_suggest_query("arabicText")},
    }


def build_semantic_query(query, filter_clauses):
    """bool query matching the inference-backed semantic_text field."""
    return {
        "bool": {
            "filter": filter_clauses,
            "must": [{"semantic": {"field": SEMANTIC_FIELD, "query": query}}],
        }
    }


def malformed_query_response(exc):
    """400 for a query ES rejected. Logs the detail but doesn't leak ES
    internals (field paths, index names) to the client."""
    access_log.warning(
        "malformed_query",
        extra={"request_id": getattr(g, "request_id", None), "detail": str(exc)},
    )
    return jsonify({"error": "malformed query"}), 400

@app.route("/index", methods=["GET"])
def index():
    start = time.time()
    if request.args.get("password") != os.environ.get("INDEXING_PASSWORD"):
        return "Must provide valid password to index", 401

    if SEMANTIC_ENABLED:
        create_inference_endpoint()

    connection = pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE"),
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    # Arabic Hadiths
    cursor.execute(
        """SELECT arabicURN as urn, collection, hadithNumber, hadithText as arabicText, 
                    matchingEnglishURN, "ar" as lang, grade1 as grade FROM ArabicHadithTable"""
    )
    arabicHadiths = cursor.fetchall()

    arabicOnlyHadiths = []
    matchingArabicHadiths = {}
    for arabicHadith in arabicHadiths:
        if arabicHadith["matchingEnglishURN"] == 0:
            arabicOnlyHadiths.append(arabicHadith)
        else:
            matchingArabicHadiths[arabicHadith["matchingEnglishURN"]] = arabicHadith
    

    # English Hadiths
    cursor.execute(
        """SELECT englishURN as urn, collection, hadithText, 
                    matchingArabicURN, "en" as lang, grade1 as grade FROM EnglishHadithTable"""
    )
    englishHadiths = cursor.fetchall()

    # Add arabic text and hadithNumber to english hadith
    for englishHadith in englishHadiths:
        if SEMANTIC_ENABLED:
            englishHadith[SEMANTIC_FIELD] = englishHadith["hadithText"]
        if englishHadith["urn"] not in matchingArabicHadiths:
           continue
        matchingArabic = matchingArabicHadiths[englishHadith["urn"]]
        englishHadith["arabicText"] = matchingArabic["arabicText"]
        englishHadith["arabicGrade"] = matchingArabic["grade"]
        englishHadith["hadithNumber"] = matchingArabic["hadithNumber"]
        
    connection.close()
    documents = englishHadiths + arabicOnlyHadiths

    # Full rebuild when explicitly asked (?rebuild=true — needed after a
    # mapping/analysis change) or when there's no current-format index to diff
    # against. Otherwise diff against the live index and touch only what changed.
    if _is_truthy(request.args.get("rebuild")) or not _index_supports_incremental():
        result = create_and_update_index(documents, ["urn", "matchingArabicURN", "lang"])
    else:
        result = incremental_update_index(documents)

    result["failed"] = json.dumps(result.pop("errors"))
    result["arabic_only"] = {"count": len(arabicOnlyHadiths)}
    result["timeInSeconds"] = time.time() - start
    return result


@app.route("/index/status", methods=["GET"])
def index_status():
    try:
        result = es_client.search(
            index=INDEX_NAME,
            size=0,
            track_total_hits=True,
            aggs={"english": {"filter": {"exists": {"field": "hadithText"}}}},
        )
    except NotFoundError:
        return {"indexed": False}

    total = result["hits"]["total"]["value"]
    english = result["aggregations"]["english"]["doc_count"]
    return {
        "indexed": True,
        "total_count": total,
        "english_count": english,
        "arabic_only_count": total - english,
    }


def _rrf_merge(lexical_resp, semantic_resp, k, from_, size):
    """Reciprocal rank fusion of two ES result sets. Each doc's fused score
    is sum(1/(k+rank)) across retrievers it appears in; rank is 1-indexed."""
    scores = {}
    hits_by_id = {}
    for rank, h in enumerate(lexical_resp.get("hits", {}).get("hits", []), start=1):
        doc_id = h["_id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        # Lexical hits own the highlight slot — semantic queries don't produce one.
        hits_by_id[doc_id] = h
    for rank, h in enumerate(semantic_resp.get("hits", {}).get("hits", []), start=1):
        doc_id = h["_id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        hits_by_id.setdefault(doc_id, h)

    sorted_ids = sorted(scores, key=scores.get, reverse=True)
    merged_hits = []
    for doc_id in sorted_ids[from_ : from_ + size]:
        h = dict(hits_by_id[doc_id])
        h["_score"] = scores[doc_id]
        merged_hits.append(h)

    # Lexical total is the keyword-match count and stays comparable to the
    # non-semantic path; semantic returns top-N by similarity with no total.
    total = lexical_resp.get("hits", {}).get(
        "total", {"value": len(sorted_ids), "relation": "eq"}
    )
    max_score = scores[sorted_ids[0]] if sorted_ids else None
    return {
        "took": lexical_resp.get("took", 0) + semantic_resp.get("took", 0),
        "hits": {"total": total, "max_score": max_score, "hits": merged_hits},
        "suggest": lexical_resp.get("suggest"),
    }


def get_filter_from_args(args):
    filters = []
    collection = args.getlist("collection")
    if collection:
        filters.append({"terms": {"collection": collection}})

    grade = args.getlist("grade")
    if grade:
        filters.append({"terms": {"grade": grade}})
    return filters

def _resolve_search_mode(args):
    """Resolve the ?mode= arg, falling a semantic-backed mode back to lexical
    when SEMANTIC_SEARCH_ENABLED is off — so a deploy without an inference
    endpoint degrades gracefully instead of erroring."""
    mode = args.get("mode", "lexical").lower()
    if mode not in SEARCH_MODES:
        mode = "lexical"
    if mode in SEMANTIC_MODES and not SEMANTIC_ENABLED:
        return "lexical"
    return mode

@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    filter = get_filter_from_args(request.args)
    mode = _resolve_search_mode(request.args)

    fields = ["hadithNumber^2", "hadithText", "arabicText", "collection^2"]

    # TODO: Query string has a strict syntax and can cause failures when character like ":" appear in a search query.
    # It's not recomended for search. But it's what allows us to do "AND collection:bukhari" or "AND hadithNumber:123" in the search bar
    # Could be better to expose all those fields as filters instead and move away from query_string
    def build_query(query_type):
        inner = {"query": query, "fields": fields}
        if query_type == "query_string":
            inner["type"] = "cross_fields"
        return {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": filter,
                        "must": [{query_type: inner}],
                    }
                },
                "functions": [
                    {"filter": {"term": {"collection": name}}, "weight": weight}
                    for name, weight in COLLECTION_BOOSTS
                ],
                "score_mode": "sum",
                "boost_mode": "sum",
            }
        }

    if mode in SEMANTIC_MODES:
        access_log.info(
            "semantic_search_mode",
            extra={
                "request_id": getattr(g, "request_id", None),
                "language": language,
                "query": query,
                "filters": filter,
                "mode": mode,
            },
        )
        if mode == "hybrid":
            return _semantic_rrf_search(language, query, filter, build_query)
        return _semantic_only_search(language, query, filter)

    search_kwargs = {
        "index": language,
        "from_": request.args.get("from", 0),
        "size": request.args.get("size", 10),
        "_source": {"excludes": [SEMANTIC_FIELD]},
        "highlight": {"number_of_fragments": 0, "fields": {"*": {}}},
        "suggest": get_suggest_block(query),
    }

    try:
        try:
            result = es_client.search(query=build_query("query_string"), **search_kwargs)
        except BadRequestError:
            # query_string syntax is strict; retry once with simple_query_string, which tolerates malformed input
            result = es_client.search(query=build_query("simple_query_string"), **search_kwargs)
    except BadRequestError as e:
        return malformed_query_response(e)

    return jsonify(result.body)


def _semantic_rrf_search(language, query, filter_clauses, build_lexical_query):
    """Run lexical + semantic searches in parallel via msearch and fuse with RRF.
    Lexical query keeps the function_score collection boosts; semantic uses the
    inference-backed semantic_text field. Fusion happens in Python to avoid the
    Enterprise-licensed RRF retriever."""
    from_ = int(request.args.get("from", 0))
    size = int(request.args.get("size", 10))
    window = max(RRF_WINDOW, from_ + size)

    semantic_query = build_semantic_query(query, filter_clauses)
    # The semantic_text field stores chunked embeddings + a copy of the input
    # text; excluding it keeps responses lean.
    common_body = {
        "from": 0,
        "size": window,
        "_source": {"excludes": [SEMANTIC_FIELD]},
    }
    # Highlight + suggest run on the lexical leg only — _rrf_merge keeps the
    # lexical hit for any doc that appears in both legs, so a semantic-leg
    # highlight would be computed and then discarded.
    lexical_body = {
        **common_body,
        "highlight": {"number_of_fragments": 0, "fields": {"*": {}}},
        "suggest": get_suggest_block(query),
    }

    def _run(query_type):
        searches = [
            {"index": language},
            {**lexical_body, "query": build_lexical_query(query_type)},
            {"index": language},
            {**common_body, "query": semantic_query},
        ]
        return es_client.options(request_timeout=130).msearch(searches=searches)

    try:
        result = _run("query_string")
        if result["responses"][0].get("error"):
            # Only the lexical leg can hit query_string strictness; the
            # semantic leg uses a `semantic` clause that doesn't parse the
            # user's query as a syntax.
            result = _run("simple_query_string")
    except BadRequestError as e:
        return malformed_query_response(e)

    lex_resp, sem_resp = result["responses"][0], result["responses"][1]
    access_log.info(
        "semantic_rrf_legs",
        extra={
            "request_id": getattr(g, "request_id", None),
            "lexical_hits": len(lex_resp.get("hits", {}).get("hits", [])),
            "semantic_hits": len(sem_resp.get("hits", {}).get("hits", [])),
            "lexical_took_ms": lex_resp.get("took"),
            "semantic_took_ms": sem_resp.get("took"),
            "window": window,
        },
    )
    for resp, label in ((lex_resp, "lexical"), (sem_resp, "semantic")):
        if resp.get("error"):
            access_log.warning(
                "rrf_subquery_failed",
                extra={
                    "request_id": getattr(g, "request_id", None),
                    "leg": label,
                    "error": resp["error"],
                },
            )
            return jsonify({"error": "malformed query"}), 400

    merged = _rrf_merge(lex_resp, sem_resp, RRF_K, from_, size)
    access_log.info(
        "semantic_rrf_merged",
        extra={
            "request_id": getattr(g, "request_id", None),
            "returned_hits": len(merged["hits"]["hits"]),
            "max_score": merged["hits"]["max_score"],
            "from": from_,
            "size": size,
        },
    )
    return jsonify(merged)


def _semantic_only_search(language, query, filter_clauses):
    """Single semantic query against the semantic_text field — no lexical leg
    and no RRF fusion, so collection boosts (a function_score wrapper) don't
    apply and there's no highlight (a semantic_text field can't be highlighted)."""
    try:
        result = es_client.options(request_timeout=130).search(
            index=language,
            from_=int(request.args.get("from", 0)),
            size=int(request.args.get("size", 10)),
            query=build_semantic_query(query, filter_clauses),
            _source={"excludes": [SEMANTIC_FIELD]},
            suggest=get_suggest_block(query),
        )
    except BadRequestError as e:
        return malformed_query_response(e)
    return jsonify(result.body)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
