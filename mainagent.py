# mainagent.py
import argparse
from loadfinbertmodel import load_finbert
from decisionagent import DecisionAgent
from searchagent import SearchAgent
from newscollector import NewsCollector


class MainAgent:
    def __init__(self, coin_name="BTC", portfolio_value=1000, use_search=True):
        self.coin_name = coin_name
        self.portfolio_value = portfolio_value
        self.use_search = use_search

        # Load FinBERT model + tokenizer
        self.model, self.tokenizer = load_finbert()

        # Debug check
        print("DEBUG model type:", type(self.model))
        print("DEBUG tokenizer type:", type(self.tokenizer))

        # Agents
        self.decision_agent = DecisionAgent(
            self.model, self.tokenizer, portfolio_value)
        self.search_agent = SearchAgent(coin_name)
        self.news_collector = NewsCollector()

    def run(self):
        print(f"🔎 Collecting URLs for {self.coin_name}...")

        urls = []
        if self.use_search:
            urls = self.search_agent.search_news()
        else:
            print("⚠️ Search disabled. Provide URLs manually.")

        if not urls:
            print("⚠️ No URLs found!")
            return

        print(f"✅ Found {len(urls)} URLs")

        results = []
        for url in urls:
            print(f"📰 Collecting news from: {url}")
            text = self.news_collector.get_article_text(url)

            if not text:
                print("⚠️ No text extracted.")
                continue

            decision = self.decision_agent.analyze(text)
            results.append({"url": url, "decision": decision})

        print("\n✅ Final Results:")
        for r in results:
            print(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto News Trading Agent")
    parser.add_argument("--coin", type=str, required=True,
                        help="Coin name (e.g., BTC, ETH, BNB)")
    parser.add_argument("--portfolio", type=float,
                        default=1000, help="Portfolio value")
    parser.add_argument("--no-search", action="store_true",
                        help="Disable search and require manual URLs")

    args = parser.parse_args()

    agent = MainAgent(
        coin_name=args.coin,
        portfolio_value=args.portfolio,
        use_search=not args.no_search
    )
    agent.run()
