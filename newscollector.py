import requests
from newspaper import Article
from bs4 import BeautifulSoup


class NewsCollector:
    def __init__(self, debug=False):
        self.debug = debug

    def extract_text(self, url):
        """Extracts and cleans article text from a single URL."""
        print(f"🌐 Fetching: {url}")

        # Try Newspaper3k first
        try:
            article = Article(url)
            article.download()
            article.parse()
            text = article.text.strip()

            if len(text) > 500:
                if self.debug:
                    print(
                        f"✅ Extracted text with Newspaper3k ({len(text)} chars)")
                return text
            else:
                print("⚠️ Newspaper3k returned too little text, using fallback...")
        except Exception as e:
            print(f"⚠️ Newspaper3k failed for {url}: {e}")

        # Fallback: requests + BeautifulSoup
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            text = "\n".join(paragraphs)
            if len(text) > 300:
                if self.debug:
                    print(
                        f"✅ Extracted text with fallback parser ({len(text)} chars)")
                return text
            else:
                print(
                    f"⚠️ Fallback parser failed for {url}: not enough content")
        except Exception as e:
            print(f"⚠️ Fallback parser failed for {url}: {e}")

        print(f"⚠️ No text extracted from {url}")
        return ""
