# urlfinder.py

import requests
from bs4 import BeautifulSoup


class URLFinder:
    def __init__(self, coin="BNB"):
        self.coin = coin.lower()
        self.sources = [
            "https://cointelegraph.com/tags/binance-coin",
            "https://cryptoslate.com/coins/binance-coin/",
            "https://u.today/tags/binance",
            "https://newsbtc.com/tag/binance-coin/",
            "https://decrypt.co/search/binance"
        ]

    def find_urls(self, limit=5):
        urls = []

        for site in self.sources:
            try:
                print(f"🌐 Checking {site}")
                response = requests.get(
                    site, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code != 200:
                    print(
                        f"⚠️ Failed to fetch {site} (status {response.status_code})")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                for a in soup.find_all("a", href=True):
                    href = a["href"]

                    # Filter only news/article URLs
                    if any(x in href.lower() for x in ["news", "article", "post"]):
                        if href.startswith("/"):
                            base = site.split("/")[0] + \
                                "//" + site.split("/")[2]
                            href = base + href
                        if href not in urls:
                            urls.append(href)

                if len(urls) >= limit:
                    break

            except Exception as e:
                print(f"⚠️ Error scraping {site}: {e}")

        return urls[:limit]
