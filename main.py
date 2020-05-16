import json
import news_feed
import feedparser
import time
from pymongo import MongoClient
import pymongo


class NewsCollector():
    """
    mongo
    """

    def __init__(self, db_access=True, url="localhost", db="news", collection="yahoo"):
        """
        """
        self.db_access = db_access
        if db_access:
            self.connect(url=url, db=db, collection=collection)

    def connect(self, url="localhost", db="news", collection="yahoo"):
        print("[CONNECT]mongodb://{}:{}@{}".format("xxxx", "xxxx", url))
        self.client = MongoClient(
            "mongodb://{}:{}@{}".format("root", "example", url))
        self.db = self.client[db]
        self.coll = self.db[collection]
        self.coll.create_index("link", unique=True)
        self.topics = self.db["topics"]
        self.topics.create_index(
            [("published", pymongo.DESCENDING), ("title", pymongo.DESCENDING)], unique=True)

    def insert(self, query):
        if not self.db_access:
            print(query)
            return
        try:
            self.coll.insert_one(query)
        except pymongo.errors.DuplicateKeyError as e:
            print("[DuplicateKey]{}".format(query["link"]))
        except:
            import traceback
            print(query)
            traceback.print_exc()

    def topic_insert(self, rss_link, yahoo_news_dic):
        if not self.db_access:
            print(yahoo_news_dic)
            return
        try:
            query = {
                "published": yahoo_news_dic.feed.published,
                "title": yahoo_news_dic.feed.title,
                "subtitle": yahoo_news_dic.feed.subtitle,
                "rss_link": rss_link,
                "entries": yahoo_news_dic.entries
            }
            self.topics.insert_one(query)
        except:
            import traceback
            print(rss_link)
            traceback.print_exc()

    def yahoo_news(self, link):
        yahoo_news_dic = feedparser.parse(link)
        if "pickup" in link:
            self.topic_insert(link, yahoo_news_dic)
        for entry in yahoo_news_dic.entries:
            # リンクを取得
            detail_link = entry.link
            if "pickup" in entry.link:
                detail_link = news_feed.parseElement(
                    entry.link, ".pickupMain_detailLink a").get("href")
            if "byline" in detail_link:
                para = news_feed.parseElement(
                    detail_link, "#byline_detail_article div p,h2",
                    select_one=False)
            else:
                para = news_feed.parseElement(
                    detail_link, ".articleMain .paragraph", select_one=False)
            text = " ".join([news_feed.sanitize(p.text) for p in para])
            self.write_article(entry.title, detail_link,
                               entry.published, text, link)

    def write_article(self, title, link, published, text, rss_link):
        d = {
            "title": title,
            "link": link,
            "published": published,
            "text": text,
            "rss_link": rss_link
        }
        self.insert(d)

    def main(self, interval=1, rss_link="rss_link.json"):
        with open(rss_link) as f:
            data = json.load(f)
        links = data["yahoo_news"]
        for l in links:
            try:
                self.yahoo_news(l)
            except:
                import traceback
                print(l)
                traceback.print_exc()
            time.sleep(interval)


if __name__ == "__main__":
    import os
    mongo_url = os.environ.get("MONGO_URL", "localhost")
    rss_link_json = os.environ.get("RSS_LINK", "rss_link.json")
    obj = NewsCollector(db_access=True, url=mongo_url)
    obj.main(rss_link=rss_link_json)
