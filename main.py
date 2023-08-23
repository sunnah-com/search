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
    return "<h1>Welcome to sunnah.com API.</h1>"


def create_and_update_index(index_name, documents, fields_to_not_index):
    mappings = {
        "properties": {
            field: {"type": "text", "index": False} for field in fields_to_not_index
        }
    }
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(index=index_name, mappings=mappings)
    successCount, errors = helpers.bulk(es_client, documents, index=index_name)
    return successCount, errors


@app.route("/index", methods=["GET"])
def index():
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
        """SELECT arabicURN, collection, 
                    hadithNumber, hadithText, 
                    matchingEnglishURN FROM ArabicHadithTable"""
    )
    arabicHadiths = cursor.fetchall()
    arabicSuccessCount, arabicErrors = create_and_update_index(
        "arabic", arabicHadiths, ["arabicURN", "matchingEnglishURN"]
    )

    # English Hadiths
    cursor.execute(
        """SELECT englishURN, collection, 
                    hadithNumber, hadithText, 
                    matchingArabicURN FROM EnglishHadithTable"""
    )
    englishHadiths = cursor.fetchall()
    englishSuccessCount, englishErrors = create_and_update_index(
        "english", englishHadiths, ["englishURN", "matchingArabicURN"]
    )

    connection.close()

    return {
        "english": {
            "success_count": englishSuccessCount,
            "failed": json.dumps(englishErrors),
        },
        "arabic": {
            "success_count": arabicSuccessCount,
            "failed": json.dumps(arabicErrors),
        },
    }


@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    # TODO: 'query_string' is strict and does not allow syntax erorrs. Compare to current behavior
    query_dsl = {
        "query_string": {
            "query": query,
            "default_field": "hadithText",
        }
    }
    return jsonify(
        es_client.search(
            index=language,
            query=query_dsl,
            from_=request.args.get("from", 0),
            size=request.args.get("size", 10),
            highlight={"number_of_fragments": 0, "fields": {"hadithText": {}}},
        ).body
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
