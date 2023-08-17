from flask import Flask, request
import pymysql
import os
from dotenv import load_dotenv
import math
import requests
import json

from elasticsearch import Elasticsearch, helpers

load_dotenv(".env.local")


app = Flask(__name__)
es_auth = ("elastic", os.environ.get("ELASTIC_PASSWORD"))
es_base_url = f"http://host.docker.internal:{os.environ.get('ES_PORT')}"
es_client = Elasticsearch(es_base_url, http_auth=es_auth)


@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to sunnah.com API.</h1>"


@app.route("/index", methods=["GET"])
def index():
    connection = pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE"),
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute(
        """SELECT arabicURN, collection, 
                    hadithNumber, hadithText, 
                    matchingEnglishURN FROM ArabicHadithTable"""
    )
    arabicHadiths = cursor.fetchall()
    helpers.bulk(es_client, arabicHadiths, index="arabic")

    cursor.execute(
        """SELECT englishURN, collection, 
                    hadithNumber, hadithText, 
                    matchingArabicURN FROM EnglishHadithTable"""
    )
    englishHadiths = cursor.fetchall()
    helpers.bulk(es_client, englishHadiths, index="english")

    # Close the connection
    connection.close()

    return "TODO"


@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("q")
    query_dsl = {"query_string": {"query": query, "default_field": "hadithText"}}
    return json.dumps(
        es_client.search(
            index=language, query=query_dsl, highlight={"fields": {"hadithText": {}}}
        ).body
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
