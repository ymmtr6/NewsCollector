import feedparser
from bs4 import BeautifulSoup
import requests

# TOPICS
# RSS_URL = "https://news.yahoo.co.jp/pickup/rss.xml"
# 国内
# RSS_URL = "https://news.yahoo.co.jp/pickup/domestic/rss.xml"
# ITmedia


# .ynDetailText.yjDirectSLinkTarget0


def parseElement(url, selector, select_one=True, parser="html.parser"):
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, parser)
        if select_one:
            return soup.select_one(selector)
        else:
            return soup.select(selector)
    else:
        return None


def sanitize(text):
    return text.strip().replace("\n", "").replace("\t", "").replace("\u3000", "").replace(" ", "")


if __name__ == "__main__":
    # TOPICS
    # RSS_URL = "https://news.yahoo.co.jp/pickup/rss.xml"
    # 国内
    # RSS_URL = "https://news.yahoo.co.jp/pickup/domestic/rss.xml"
    RSS_URL = "https://headlines.yahoo.co.jp/rss/zdn_mkt-dom.xml"
    print("YAHOO! NEWS COLLECTOR v1.0 START+")
    yahoo_news_dic = feedparser.parse(RSS_URL)
    for entry in yahoo_news_dic.entries:
        print(entry.title)
        print(entry.link)
        print(entry.published)
        # リンクを取得
        detail_link = entry.link
        if "pickup" in entry.link:
            detail_link = parseElement(
                entry.link, ".pickupMain_detailLink a").get("href")
        paragraphs = parseElement(
            detail_link, ".articleMain .paragraph", select_one=False)
        text = " ".join([sanitize(p.text) for p in paragraphs])
        print(text)
