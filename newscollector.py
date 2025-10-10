import requests
from newspaper import Article
from bs4 import BeautifulSoup


class NewsCollector:
    def __init__(self, urls):
        self.urls = urls

    def fetch_text(self, url):
        """Try newspaper3k first, fallback to BeautifulSoup."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            if len(article.text.strip()) > 200:
                print(f"✅ Extracted text from {url} with Newspaper3k")
                return article.text
        except Exception as e:
            print(f"⚠️ Newspaper3k failed for {url}: {e}")

        # Fallback parser
        try:
            resp = requests.get(url, timeout=10, headers={
                                "User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            text = " ".join(paragraphs)
            if len(text) > 200:
                print(f"✅ Extracted text from {url} with fallback parser")
                return text
        except Exception as e:
            print(f"⚠️ Fallback parser failed for {url}: {e}")
        return ""

    def collect(self):
        """Fetch text from all URLs."""
        collected = {}
        for url in self.urls:
            print(f"🌐 Fetching: {url}")
            text = self.fetch_text(url)
            if text:
                collected[url] = text
            else:
                print(f"⚠️ No text extracted from {url}")
        return collected
