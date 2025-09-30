from urlfinder import URLFinder
from newscollector import NewsCollector
from tradingagent import TradingAgent


class MainAgent:
    def __init__(self, coin_name="BNB", portfolio_value=1000):
        self.coin_name = coin_name
        self.portfolio_value = portfolio_value
        self.url_finder = URLFinder(coin=coin_name)
        self.news_collector = NewsCollector()
        self.trading_agent = TradingAgent()

    def run(self):
        print(f"🔎 Searching news URLs for {self.coin_name}...")
        urls = self.url_finder.find_urls(limit=5)

        if not urls:
            print("⚠️ No URLs found!")
            return []

        print(f"✅ Found {len(urls)} URLs")

        results = []
        for url in urls:
            print(f"\n📰 Collecting news from: {url}")
            text = self.news_collector.collect_news(url)

            if text:
                decision = self.trading_agent.trading_decision(
                    text, self.portfolio_value)
                results.append({"url": url, "decision": decision})
                print(f"📊 Decision: {decision}")
            else:
                print("⚠️ No text extracted.")

        return results


if __name__ == "__main__":
    agent = MainAgent(coin_name="BNB", portfolio_value=2000)
    all_results = agent.run()
    print("\n✅ Final Results:")
    for r in all_results:
        print(r)
