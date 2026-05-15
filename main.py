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

INDEX_NAME = "english"

SEMANTIC_ENABLED = os.environ.get("SEMANTIC_SEARCH_ENABLED", "").lower() in ("1", "true", "yes")
SEMANTIC_FIELD = "hadithTextSemantic"
INFERENCE_ENDPOINT = "googleai-text-embedding"
# RRF constants. k=60 is the value from the original Cormack et al. paper and
# the ES default. RRF_WINDOW is the depth fetched from each retriever before
# fusion — bigger window = better recall at the tail, more cost per query.
RRF_K = 60
RRF_WINDOW = 100

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
    """Create the Google AI Studio text-embedding inference endpoint used by
    the semantic_text field. Deletes any existing endpoint with the same id
    so re-indexing picks up dimension/model changes."""
    try:
        es_client.inference.delete(
            task_type="text_embedding",
            inference_id=INFERENCE_ENDPOINT,
            force=True,
        )
    except NotFoundError:
        pass
    es_client.options(request_timeout=60).inference.put(
        task_type="text_embedding",
        inference_id=INFERENCE_ENDPOINT,
        inference_config={
            "service": "googleaistudio",
            "service_settings": {
                "api_key": os.environ.get("GOOGLE_AI_STUDIO_API_KEY"),
                "model_id": "text-embedding-005",
            },
        },
    )


def create_and_update_index(index_name, documents, fields_to_not_index):
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
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(index=index_name, mappings=mappings, settings=settings)
    # When semantic_text is in the mapping each doc triggers an embedding API
    # call during indexing, so the bulk request needs a longer timeout.
    bulk_timeout = 300 if SEMANTIC_ENABLED else 60
    successCount, errors = helpers.bulk(
        es_client, documents, index=index_name, request_timeout=bulk_timeout
    )
    return successCount, errors

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
        
    indexingSuccessCount, indexingErrors = create_and_update_index(
        INDEX_NAME, englishHadiths + arabicOnlyHadiths, ["urn", "matchingArabicURN", "lang"]
    )

    connection.close()
    return {
        "all_hadith_index_results": {
            "success_count": indexingSuccessCount,
            "failed": json.dumps(indexingErrors),
        },
       "arabic_only": {
            "count": len(arabicOnlyHadiths),
        },
        "timeInSeconds": time.time() - start
    }


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

@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    filter = get_filter_from_args(request.args)
    use_semantic = SEMANTIC_ENABLED and request.args.get(
        "semantic", ""
    ).lower() in ("1", "true", "yes")

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

    if use_semantic:
        return _semantic_rrf_search(language, query, filter, build_query)

    search_kwargs = {
        "index": language,
        "from_": request.args.get("from", 0),
        "size": request.args.get("size", 10),
        "highlight": {"number_of_fragments": 0, "fields": {"*": {}}},
        "suggest": {
            "text": query,
            "english": {
                "phrase": get_suggest_query("hadithText.trigram"),
            },
            "arabic": {
                "phrase": get_suggest_query("arabicText"),
            },
        },
    }

    try:
        try:
            result = es_client.search(query=build_query("query_string"), **search_kwargs)
        except BadRequestError:
            # query_string syntax is strict; retry once with simple_query_string, which tolerates malformed input
            result = es_client.search(query=build_query("simple_query_string"), **search_kwargs)
    except BadRequestError as e:
        # Don't leak ES internals (field paths, index names) to client.
        access_log.warning(
            "malformed_query",
            extra={
                "request_id": getattr(g, "request_id", None),
                "detail": str(e),
            },
        )
        return jsonify({"error": "malformed query"}), 400

    return jsonify(result.body)


def _semantic_rrf_search(language, query, filter_clauses, build_lexical_query):
    """Run lexical + semantic searches in parallel via msearch and fuse with RRF.
    Lexical query keeps the function_score collection boosts; semantic uses the
    inference-backed semantic_text field. Fusion happens in Python to avoid the
    Enterprise-licensed RRF retriever."""
    from_ = int(request.args.get("from", 0))
    size = int(request.args.get("size", 10))
    window = max(RRF_WINDOW, from_ + size)

    semantic_query = {
        "bool": {
            "filter": filter_clauses,
            "must": [{"semantic": {"field": SEMANTIC_FIELD, "query": query}}],
        }
    }
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
        "suggest": {
            "text": query,
            "english": {"phrase": get_suggest_query("hadithText.trigram")},
            "arabic": {"phrase": get_suggest_query("arabicText")},
        },
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
        access_log.warning(
            "malformed_query",
            extra={"request_id": getattr(g, "request_id", None), "detail": str(e)},
        )
        return jsonify({"error": "malformed query"}), 400

    lex_resp, sem_resp = result["responses"][0], result["responses"][1]
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

    return jsonify(_rrf_merge(lex_resp, sem_resp, RRF_K, from_, size))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
