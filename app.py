import json
import os
from flask import Flask, jsonify
from redis_resources import redis_client, redis_queue
from functions import fetch_and_cache_newsfeed

# Flask configs
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    welcome = {
        "note":"welcome to '/'.",
        "usage": {
            "cache news":"/cache_news/<symbol or ticker>",
            "get news": "/get_news/<symbol or ticker>"
        }
    }
    return jsonify(welcome)


@app.route("/cache_news/<string:symbol>", methods=['GET'])
def cache_news(symbol: str):
    
    symbol = symbol.upper()
    job = redis_queue.enqueue(fetch_and_cache_newsfeed, symbol)
    return jsonify({"status": "OK", "job_id":job.get_id()})

@app.route("/get_news/<string:symbol>", methods=['GET'])
def get_news(symbol: str):
    symbol = symbol.upper()
    try:
        news = redis_client.get(symbol)
        if news == None:
            return jsonify({"message":f"{symbol} not cached in database. please do /cache_news/{symbol}"})
        return json.loads(news), 200
    except Exception:
        return jsonify({"status":"500 internal server error"}), 500

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)
