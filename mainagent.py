import argparse
from transformers import BertTokenizer, BertForSequenceClassification
from decisionagent import DecisionAgent
from technicalagent import TechnicalAgent
from newscollector import NewsCollector
from calculations import CalculateAgent

# Optional best coin analyzer
from bestcoinagent import BestCoinAgent


class MainAgent:
    def __init__(self, coin_name=None, portfolio_value=1000, timeframe="4h", debug=False):
        self.coin_name = coin_name
        self.portfolio_value = portfolio_value
        self.timeframe = timeframe
        self.debug = debug

        # Load model + tokenizer
        self.model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased", num_labels=3)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

        # Initialize sub-agents
        self.decision_agent = DecisionAgent(self.model, self.tokenizer)
        self.tech_agent = TechnicalAgent()
        self.news_collector = NewsCollector()
        self.calculate_agent = CalculateAgent(timeframe=self.timeframe)

    def run(self):
        print(
            f"🔎 Running MainAgent for {self.coin_name} ({self.timeframe})...")

        # 1️⃣ Fetch news
        print(f"📰 Fetching news for {self.coin_name}...")
        urls = self.news_collector.get_urls(self.coin_name)
        if not urls:
            print(f"⚠️ No news URLs found for {self.coin_name}.")
            return

        all_text = ""
        for url in urls:
            text = self.news_collector.extract_text(url)
            if text:
                if self.debug:
                    print(f"🧾 DEBUG: Extracted {len(text)} chars from {url}")
                all_text += text + "\n"

        if not all_text.strip():
            print("⚠️ No text extracted from any news source.")
            return

        # 2️⃣ Technical analysis
        tech_bias, tech_strength, tf = self.tech_agent.analyze(
            self.coin_name, self.timeframe)

        # 3️⃣ Combine both analyses
        print(
            f"🤖 Running sentiment + technical decision for {self.coin_name}...")
        action, confidence, sentiment, tech_bias, tf = self.decision_agent.analyze(
            all_text, tech_bias, self.timeframe
        )

        # 4️⃣ Trading calculation
        result = self.calculate_agent.calculate(
            action, confidence, self.portfolio_value, self.coin_name
        )

        if result:
            result["sentiment"] = sentiment
            result["tech_bias"] = tech_bias
            result["timeframe"] = tf

            print("\n✅ Final Decision:")
            print(result)
        else:
            print("❌ Could not compute a final decision.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto AI Trading Agent")
    parser.add_argument("--coin", type=str, default="BTC",
                        help="Coin symbol to analyze, e.g. BTC, ETH, BNB")
    parser.add_argument("--portfolio", type=float,
                        default=1000, help="Portfolio value in USD")
    parser.add_argument("--timeframe", type=str, default="4h",
                        help="Chart timeframe (e.g., 1h, 4h, 1d)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")
    parser.add_argument("--findbest", action="store_true",
                        help="Find the best coin to trade")

    args = parser.parse_args()

    # 🧩 If --findbest flag is given, activate the multi-coin search agent
    if args.findbest:
        print("🚀 Running BestCoinAgent to find best trading opportunity...")
        best_agent = BestCoinAgent(
            portfolio_value=args.portfolio, timeframe=args.timeframe)
        best_agent.find_best()
    else:
        # 🪙 Otherwise, analyze a single coin
        agent = MainAgent(
            coin_name=args.coin,
            portfolio_value=args.portfolio,
            timeframe=args.timeframe,
            debug=args.debug
        )
        agent.run()
