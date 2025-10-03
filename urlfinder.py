# urlfinder.py (improved with article extraction from tag pages)

import requests
from bs4 import BeautifulSoup


class URLFinder:
    def __init__(self, coin="BNB"):
        self.coin = coin.lower()

    def extract_articles_from_category(self, category_url, limit=3):
        """Fetch article links from a category/tag page"""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(category_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            links = []

            for a in soup.find_all("a", href=True):
                href = a["href"].lower()

                # Filter: real-looking news articles
                if "2025" in href or "2024" in href or "/news/" in href:
                    if href.startswith("/"):
                        base = category_url.split(
                            "/")[0] + "//" + category_url.split("/")[2]
                        href = base + href
                    if href not in links:
                        links.append(href)

                if len(links) >= limit:
                    break

            return links
        except Exception as e:
            print(f"⚠️ Failed to extract from category {category_url}: {e}")
            return []
