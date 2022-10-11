import requests
import feedparser
from redis_resources import redis_client
import redis
import json


def fetch_and_cache_newsfeed(symbol: str):
    """
    input:
    symbol: type str: symbol of a company e.g. AMZN, FB in uppercase. 

    """

    url = f"https://www.nasdaq.com/feed/rssoutbound?symbol={symbol.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }
    try:
        # fetching the xml data from url
        res = requests.get(url, headers=headers).text
        # parsing the xml data.
        data = list(feedparser.parse(res).entries)
        news = []
        for each_news in data:
            news.append({
                "id": each_news['id'],
                "title": each_news['title'],
                "summary": each_news['summary'],
                'link': each_news['link'],
                'published': each_news['published']
            })
        try:
            redis_client.set(symbol, json.dumps(news))
            return 1
        except redis.exceptions.ConnectionError:
            print("Unable to connect to Redis !!!!")
            return 0

        except Exception as e:
            print(e)
            print("Something went wrong with Redis !!")
            return 0

    except requests.exceptions.ConnectionError:
        print("Unable to connect to nasdaq !!")
        print("query is not cached is Redis.")
        return 0
