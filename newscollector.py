import requests
from bs4 import BeautifulSoup
from newspaper import Article


class NewsCollector:
    def __init__(self, urls, debug=False):
        self.urls = urls
        self.debug = debug

    def extract_text(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            if len(article.text.strip()) < 200:
                raise ValueError("Too little text, fallback to BeautifulSoup")
            if self.debug:
                print(f"✅ Extracted text with Newspaper3k: {url}")
            return article.text
        except Exception:
            try:
                r = requests.get(url, timeout=10, headers={
                                 "User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(r.text, "html.parser")
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                text = "\n".join(paragraphs)
                if self.debug:
                    print(f"✅ Extracted text with fallback parser: {url}")
                return text
            except Exception as e:
                print(f"⚠️ Failed to extract text from {url}: {e}")
                return None

    def collect_news(self):
        texts = []
        for url in self.urls:
            print(f"🌐 Fetching: {url}")
            text = self.extract_text(url)
            if text:
                texts.append((url, text))
            else:
                print(f"⚠️ No text extracted from {url}")
        return texts
