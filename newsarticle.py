from newspaper import Article
import requests
from bs4 import BeautifulSoup


class NewsCollector:
    def extract_text(self, url):
        """
        Attempt to extract readable text from a news page.
        """
        # Try newspaper3k first
        try:
            article = Article(url)
            article.download()
            article.parse()
            if len(article.text) > 200:
                print(f"✅ Extracted text from {url} with Newspaper3k")
                return article.text
        except Exception as e:
            print(f"⚠️ Newspaper3k failed for {url}: {e}")

        # Fallback to BeautifulSoup
        try:
            resp = requests.get(url, timeout=10, headers={
                                "User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = " ".join(p.get_text() for p in soup.find_all("p"))
            if len(paragraphs) > 100:
                print(f"✅ Extracted text from {url} with fallback parser")
                return paragraphs[:4000]
        except Exception as e:
            print(f"⚠️ Fallback parser failed for {url}: {e}")

        print(f"⚠️ No text extracted from {url}")
        return ""
