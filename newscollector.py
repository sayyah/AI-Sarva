import requests
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import langdetect
import time

# Optional dictionary mapping coin -> source URLs
COIN_URLS = {
    "BTC": [
        "https://cointelegraph.com/tags/bitcoin",
        "https://www.coindesk.com/price/bitcoin/news",
        "https://crypto.news/tag/btc/",
        "https://coinjournal.net/news/"
    ],
    "BNB": [
        "https://cointelegraph.com/tags/binance-coin",
        "https://www.coindesk.com/price/binance-coin/news",
        "https://crypto.news/tag/bnb/",
        "https://coinjournal.net/news/"
    ]
}


class NewsCollector:
    """
    Collects and extracts English-language news articles for a given coin.
    Returns a dictionary {url: article_text}.
    """

    def __init__(self, urls=None, coin=None):
        if urls:
            self.urls = urls
        elif coin and coin.upper() in COIN_URLS:
            self.urls = COIN_URLS[coin.upper()]
        else:
            raise ValueError("No valid URLs provided for NewsCollector.")

    # ------------------------------------------------------
    # 📰 Extract text from a single article URL
    # ------------------------------------------------------
    def extract_article(self, url):
        try:
            article = Article(url, language="en")
            article.download()
            article.parse()
            text = article.text.strip()
            if len(text) < 300:
                raise ValueError(
                    "Text too short for Newspaper3k, fallback triggered.")
            print(f"✅ Extracted text with Newspaper3k ({len(text)} chars)")
            return text
        except Exception as e:
            print(f"⚠️ Newspaper3k failed for {url}: {e}")
            # fallback to simple HTML parsing
            return self.fallback_parser(url)

    # ------------------------------------------------------
    # 🌐 Fallback HTML text extraction
    # ------------------------------------------------------
    def fallback_parser(self, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Try to extract meaningful text
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text() for p in paragraphs)
            text = text.strip()

            # Language filter
            lang = langdetect.detect(text[:500]) if len(
                text) > 500 else "unknown"
            if lang != "en":
                print(f"⚠️ Skipped non-English content ({lang}) from {url}")
                return None

            print(f"✅ Extracted text with fallback parser ({len(text)} chars)")
            return text if text else None
        except Exception as e:
            print(f"⚠️ Fallback parser failed for {url}: {e}")
            return None

    # ------------------------------------------------------
    # 🔍 Collect all news for current coin
    # ------------------------------------------------------
    def collect_news(self):
        results = {}
        for url in self.urls:
            print(f"🌐 Fetching: {url}")
            text = self.extract_article(url)
            if text:
                results[url] = text
            else:
                print(f"⚠️ No text extracted from {url}")
            # polite delay to avoid being blocked
            time.sleep(1.5)
        return results
