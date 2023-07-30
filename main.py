from flask import Flask
import pymysql
import os
from dotenv import load_dotenv

load_dotenv(".env.local")



app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    # Connect to the database
    connection = pymysql.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PASSWORD"),
    database=os.environ.get("MYSQL_DATABASE")
    )
    # Create a cursor
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Execute a query
    cursor.execute("""SELECT arabicURN, collection, 
                    hadithNumber, hadithText, 
                    matchingEnglishURN FROM ArabicHadithTable""")
    # Fetch the results
    arabicHadiths = cursor.fetchall()

    # Print the results
    for row in arabicHadiths:
        print(row.get("hadithText"))

    cursor.execute("""SELECT englishURN, collection, 
                    hadithNumber, hadithText, 
                    matchingArabicURN FROM EnglishHadithTable""")
    # Fetch the results
    englishHadiths = cursor.fetchall()

    # Print the results
    for row in englishHadiths:
        print(row.get("hadithText"))
        
    # Close the connection
    connection.close()

    return "<h1>Welcome to sunnah.com API.</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
