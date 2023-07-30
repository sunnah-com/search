from flask import Flask
import pymysql
import os
from dotenv import load_dotenv
import math
from elasticsearch import Elasticsearch, helpers

load_dotenv(".env.local")



app = Flask(__name__)
es_client = Elasticsearch(f"http://host.docker.internal:{os.environ.get('ES_PORT')}",
                        http_auth=('elastic', os.environ.get("ELASTIC_PASSWORD")))

@app.route("/", methods=["GET"])
def home():
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

    return "<h1>Welcome to sunnah.com API.</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
