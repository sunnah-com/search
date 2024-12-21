import time
from flask import Flask, request, jsonify
import pymysql
import os
from dotenv import load_dotenv
import json

from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import InferenceClient

load_dotenv(".env.local")


app = Flask(__name__)
es_auth = ("elastic", os.environ.get("ELASTIC_PASSWORD"))
es_base_url = f"http://elasticsearch:{os.environ.get('ES_PORT')}"
es_client = Elasticsearch(es_base_url, http_auth=es_auth, timeout=30)
if_client = InferenceClient(client=es_client)
INFERENCE_ENDPOINT = "openai-inference"

@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to sunnah.com search api.</h1>"

def create_inference_endpoint():
    try:
        if_client.delete(task_type="text_embedding", inference_id=INFERENCE_ENDPOINT, force=True)
    except Exception as e:
        print(e)
        
    if_client.put(task_type="text_embedding", inference_id=INFERENCE_ENDPOINT, body={
    "service": "openai",
    "service_settings": {
        "api_key": os.environ.get("OPENAI_KEY"),
        "model_id": "text-embedding-3-small",
        "dimensions": 128
    }
    })

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
                        "filter": ["lowercase", "stop", "shingle"],
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
                    "custom_arabic": {
                        "tokenizer":  "standard",
                        "char_filter": ["html_strip"],
                        "filter": [
                            "lowercase",
                            "decimal_digit",
                            "arabic_normalization",
                            "arabic_stemmer",
                            "shingle"
                        ]
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
            },
            "hadithTextSemantic": {
                "type": "semantic_text",
                "inference_id": INFERENCE_ENDPOINT
            }
        }
        | {"arabicText": {"type": "text", "analyzer": "custom_arabic"}}
    }
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(index=index_name, mappings=mappings, settings=settings)
    successCount, errors = 0, []
    try:
        successCount, errors = helpers.bulk(es_client, documents, index=index_name, request_timeout=120)
    except helpers.BulkIndexError as e:
        print(e.errors)
        print("LEN: ", len(e.errors))
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
        englishHadith["hadithTextSemantic"] = englishHadith["hadithText"]
        if englishHadith["urn"] not in matchingArabicHadiths:
           continue
        matchingArabic = matchingArabicHadiths[englishHadith["urn"]]
        englishHadith["arabicText"] = matchingArabic["arabicText"]
        englishHadith["arabicGrade"] = matchingArabic["grade"]
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
    lexical_query = {
        "query_string": {
            "query": query,
            "type": "cross_fields",
            "fields": ["hadithNumber^2", "hadithText", "arabicText", "collection^2"],
            "boost": 1
        }
    }
    semantic_query = {
        "semantic": {
            "field": "hadithTextSemantic",
            "query": query,
            "boost" : 50
        }
    }
    query_dsl = {
     "bool": {
      "should": [
         lexical_query, semantic_query
      ]
        }
      }
    return jsonify(
        es_client.search(
            index=language,
            query=query_dsl,
            from_=request.args.get("from", 0),
            size=request.args.get("size", 10),
            highlight={"number_of_fragments": 0, "fields": {"*": {}}},
            suggest= {
                "text": query,
                "english": {
                     "phrase": get_suggest_query("hadithText.trigram"),
                 },
                "arabic": {
                     "phrase": get_suggest_query("arabicText"),
                 },
            },
            timeout="120s",
            request_timeout=130
        ).body
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
