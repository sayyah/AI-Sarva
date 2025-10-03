# newscollector.py
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException


class NewsCollector:
    def __init__(self, debug=False):
        self.debug = debug

    def _is_english(self, text):
        try:
            lang = detect(text[:500])  # detect using first 500 chars
            return lang == "en"
        except LangDetectException:
            return False

    def collect(self, url):
        if self.debug:
            print(f"📰 Collecting news from: {url}")

        text = None

        # Try Newspaper3k
        try:
            article = Article(url, language="en")
            article.download()
            article.parse()
            text = article.text.strip()
        except Exception as e:
            if self.debug:
                print(f"⚠️ Newspaper3k failed for {url}: {e}")

        # Fallback with requests + BeautifulSoup
        if not text or len(text) < 200:
            try:
                resp = requests.get(url, timeout=10, headers={
                                    "User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(resp.text, "html.parser")
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                text = "\n".join(paragraphs)
            except Exception as e:
                if self.debug:
                    print(f"⚠️ Fallback failed for {url}: {e}")
                return None

        if not text or len(text) < 200:
            if self.debug:
                print("⚠️ Not enough text extracted.")
            return None

        # Language check
        if not self._is_english(text):
            if self.debug:
                print("⚠️ Skipped non-English article.")
            return None

        return text
