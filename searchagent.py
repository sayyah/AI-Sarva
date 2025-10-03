# searchagent.py
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import unquote, urlparse


class SearchAgent:
    def __init__(self, coin, debug=False):
        self.coin = coin
        self.debug = debug

    async def _bing_search(self, query, max_results=10):
        urls = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            search_url = f"https://www.bing.com/news/search?q={query}+cryptocurrency+news+site"
            await page.goto(search_url, timeout=60000)

            # Extract all hrefs
            hrefs = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            if self.debug:
                print("🔍 DEBUG: Extracted hrefs from Bing page:")

            for idx, href in enumerate(hrefs):
                if self.debug:
                    print(f"   [{idx}] {href}")

                if not href or href.startswith("javascript:"):
                    continue
                if "bing.com" in href:
                    continue  # skip bing internal links

                # Decode tracking redirect links
                decoded = unquote(href)
                if "u=a1" in decoded:
                    parts = decoded.split("u=a1")
                    if len(parts) > 1:
                        decoded = unquote(parts[1])

                urls.append(decoded)

            await browser.close()

        # Deduplicate + filter non-English
        clean_urls = []
        seen = set()
        for u in urls:
            domain = urlparse(u).netloc
            if u not in seen and ".tr." not in domain and ".de." not in domain:
                seen.add(u)
                clean_urls.append(u)

        if self.debug:
            print(f"✅ Found {len(clean_urls)} valid news URLs")
            for idx, u in enumerate(clean_urls):
                print(f"   [{idx}] {u}")

        return clean_urls[:max_results]

    def search(self, max_results=10):
        query = f"{self.coin} cryptocurrency"
        return asyncio.run(self._bing_search(query, max_results))
