import time
from flask import Flask, request, jsonify
import pymysql
import os
from dotenv import load_dotenv
import math
import json

from elasticsearch import Elasticsearch, helpers, BadRequestError, NotFoundError

from utils.shortcode_pattern import SHORTCODE_PATTERN

load_dotenv(".env.local")


app = Flask(__name__)
es_auth = ("elastic", os.environ.get("ELASTIC_PASSWORD"))
es_base_url = f"http://elasticsearch:{os.environ.get('ES_PORT')}"
es_client = Elasticsearch(es_base_url, http_auth=es_auth)

INDEX_NAME = "english"


@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to sunnah.com search api.</h1>"


def create_and_update_index(index_name, documents, fields_to_not_index):
    settings = {
        "index": {
            "number_of_shards": 1,
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
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(index=index_name, mappings=mappings, settings=settings)
    successCount, errors = helpers.bulk(es_client, documents, index=index_name)
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

    fields = ["hadithNumber^2", "hadithText", "arabicText", "collection^2"]

    # TODO: Query string has a strict syntax and can cause failures when character like ":" appear in a search query.
    # It's not recomended for search. But it's what allows us to do "AND collection:bukhari" or "AND hadithNumber:123" in the search bar
    # Could be better to expose all those fields as filters instead and move away from query_string
    def build_bool_query(query_type):
        inner = {"query": query, "fields": fields}
        if query_type == "query_string":
            inner["type"] = "cross_fields"
        return {
            "bool": {
                "filter": filter,
                "must": [{query_type: inner}],
            }
        }

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
        result = es_client.search(query=build_bool_query("query_string"), **search_kwargs)
    except BadRequestError:
        # query_string syntax is strict; retry once with simple_query_string, which tolerates malformed input
        result = es_client.search(query=build_bool_query("simple_query_string"), **search_kwargs)

    return jsonify(result.body)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
