import asyncio
import base64
import urllib.parse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re


class SearchAgent:
    def __init__(self, coin_name: str, debug: bool = False):
        self.coin_name = coin_name
        self.debug = debug

        # Whitelist of good English crypto/finance news sources
        self.allowed_domains = [
            "cointelegraph.com", "coindesk.com", "coinjournal.net",
            "beincrypto.com", "cryptonews.com", "newsbtc.com",
            "forbes.com", "coinmarketcap.com", "decrypt.co",
            "analyticsinsight.net", "bloomberg.com", "reuters.com",
            "finance.yahoo.com", "markets.businessinsider.com",
            "investing.com", "nasdaq.com", "techcrunch.com",
            "theblock.co", "ambcrypto.com", "cryptopolitan.com"
        ]

        # Blacklist: junk/redirect/ads
        self.blocked_domains = [
            "bing.com", "microsoft.com", "msn.com", "linkedin.com",
            "youtube.com", "facebook.com", "twitter.com", "x.com"
        ]

    async def _bing_search_playwright(self, query: str):
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()

            search_url = (
                f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
                f"&setlang=en&cc=US&lr=en&FORM=HDRSC1"
            )
            if self.debug:
                print(
                    f"🔎 Searching Bing for {self.coin_name} news (Playwright)...")
                print(f"URL: {search_url}")

            await page.goto(search_url, timeout=60000)
            content = await page.content()
            await browser.close()
            return content

    def _decode_bing_url(self, raw_url: str):
        match = re.search(r"u=a1([^&]+)", raw_url)
        if not match:
            return None
        encoded_part = match.group(1)
        try:
            decoded = base64.b64decode(encoded_part).decode("utf-8")
            return decoded
        except Exception:
            return None

    def _is_valid_news_url(self, url: str):
        if not url or not url.startswith("http"):
            return False
        if any(bad in url for bad in self.blocked_domains):
            return False
        if not any(domain in url for domain in self.allowed_domains):
            return False
        return True

    async def search_news_async(self):
        query = f"{self.coin_name} cryptocurrency news site"
        html = await self._bing_search_playwright(query)

        soup = BeautifulSoup(html, "html.parser")
        hrefs = [a.get("href") for a in soup.find_all("a", href=True)]

        if self.debug:
            print("🔍 DEBUG: Extracted hrefs from Bing page:")
            for i, href in enumerate(hrefs):
                print(f"   [{i}] RAW: {href}")

        decoded_urls = []
        for href in hrefs:
            if not href:
                continue
            if "bing.com/ck/a" in href:
                decoded = self._decode_bing_url(href)
                if decoded:
                    decoded_urls.append(decoded)
                    if self.debug:
                        print(f"        ✅ Decoded: {decoded}")
            elif href.startswith("http") and "bing.com" not in href:
                decoded_urls.append(href)

        # Keep only real English news domains
        final_urls = [u for u in decoded_urls if self._is_valid_news_url(u)]

        if final_urls:
            print(f"✅ Found {len(final_urls)} valid English news URLs")
            for i, url in enumerate(final_urls):
                print(f"   [{i}] {url}")
        else:
            print("⚠️ No valid English news URLs found!")

        return list(dict.fromkeys(final_urls))  # deduplicate

    def search_news(self):
        return asyncio.run(self.search_news_async())
