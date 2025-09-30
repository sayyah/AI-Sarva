# newscollector.py

from newspaper import Article


class NewsCollector:
    def collect_news(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            text = article.text.strip()

            if not text or len(text.split()) < 50:  # Skip short junk pages
                print("⚠️ Skipping, not enough content.")
                return None

            return text

        except Exception as e:
            print(f"⚠️ Failed to extract news from {url}: {e}")
            return None
