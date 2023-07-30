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
es_auth = ('elastic', os.environ.get("ELASTIC_PASSWORD"))
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
        database=os.environ.get("MYSQL_DATABASE")
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""SELECT arabicURN, collection, 
                    hadithNumber, hadithText, 
                    matchingEnglishURN FROM ArabicHadithTable""")
    arabicHadiths = cursor.fetchall()
    helpers.bulk(es_client, arabicHadiths, index="arabic")



    cursor.execute("""SELECT englishURN, collection, 
                    hadithNumber, hadithText, 
                    matchingArabicURN FROM EnglishHadithTable""")
    englishHadiths = cursor.fetchall()
    helpers.bulk(es_client, englishHadiths, index="english")

    # Close the connection
    connection.close()

    return "TODO"

@app.route("/<language>/search", methods=["GET"])
def search(language):
    query = request.args.get("query")
    # fields to query on
    # TODO: hadithNumber cant be default field as is, errors out with string query
    fields = request.args.get("fields", ["collection", "hadithText"])
    req_body = {
            "query":{   
                "multi_match" : {
                "query":  query, 
                "fields": fields
                }
            }
        }
    headers = {'Content-Type': 'application/json'}

    return requests.get(f"{es_base_url}/{language}/_search", headers=headers, auth=es_auth, data=json.dumps(req_body)).json()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
