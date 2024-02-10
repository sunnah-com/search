import time
from flask import Flask, request, jsonify
import pymysql
import os
from dotenv import load_dotenv
import math
import json

from elasticsearch import Elasticsearch, helpers

load_dotenv(".env.local")


app = Flask(__name__)
es_auth = ("elastic", os.environ.get("ELASTIC_PASSWORD"))
es_base_url = f"http://elasticsearch:{os.environ.get('ES_PORT')}"
es_client = Elasticsearch(es_base_url, http_auth=es_auth)


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
                        "char_filter": ["html_strip"],
                        "filter": ["lowercase", "stop", "shingle", "stemmer", "stop"],
                    },
                    "synonym": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": [
                            "lowercase",
                            "stop",
                            "synonyms_filter",
                            "stemmer",
                        ],
                    },
                    "arabic": {
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": [
                            "lowercase",
                            "stop",
                            "stemmer",
                        ],
                    },
                },
                "filter": {
                    # 2-3 word shingles for better suggestions
                    "shingle": {
                        "type": "shingle",
                        "min_shingle_size": 2,
                        "max_shingle_size": 3,
                    },
                    "synonyms_filter": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "synonyms.txt",
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
        | {"arabicText": {"type": "text", "analyzer": "arabic"}}
    }
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(index=index_name, mappings=mappings, settings=settings)
    successCount, errors = helpers.bulk(es_client, documents, index=index_name)
    return successCount, errors


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
                    matchingEnglishURN, "ar" as lang FROM ArabicHadithTable"""
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
                    matchingArabicURN, "en" as lang FROM EnglishHadithTable"""
    )
    englishHadiths = cursor.fetchall()

    # Add arabic text and hadithNumber to english hadith
    for englishHadith in englishHadiths:
        if englishHadith["urn"] not in matchingArabicHadiths:
           continue
        matchingArabic = matchingArabicHadiths[englishHadith["urn"]]
        englishHadith["arabicText"] = matchingArabic["arabicText"]
        englishHadith["hadithNumber"] = matchingArabic["hadithNumber"]
        
    indexingSuccessCount, indexingErrors = create_and_update_index(
        "english", englishHadiths + arabicOnlyHadiths, ["urn", "matchingArabicURN", "lang"]
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


@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    # TODO: 'query_string' is strict and does not allow syntax erorrs. Compare to current behavior
    query_dsl = {
        "query_string": {
            "query": query,
            "type": "cross_fields",
            "fields": ["hadithNumber^2", "hadithText", "arabicText", "collection^2"],
        }
    }
    return jsonify(
        es_client.search(
            index=language,
            query=query_dsl,
            from_=request.args.get("from", 0),
            size=request.args.get("size", 10),
            highlight={"number_of_fragments": 0, "fields": {"*": {}}},
            suggest={
                "text": query,
                "query": {
                    "phrase": {
                        "field": "hadithText.trigram",
                        "size": 1,
                        "gram_size": 3,
                        "direct_generator": [
                            {"field": "hadithText.trigram", "suggest_mode": "always"}
                        ],
                        "highlight": {"pre_tag": "<em>", "post_tag": "</em>"},
                        "collate": {
                            "query": {
                                "source": {
                                    "match": {"hadithText": "\{\{suggestion\}\}"}
                                }
                            },
                            # Only return suggestions with a query match
                            "prune": False,
                        },
                    }
                },
            },
        ).body
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
