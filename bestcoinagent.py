import time
from technicalagent import TechnicalAgent
from decisionagent import DecisionAgent
from calculations import CalculateAgent
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import yfinance as yf


class BestCoinAgent:
    def __init__(self, portfolio_value=1000, timeframe="4h", top_n=3):
        self.portfolio_value = portfolio_value
        self.timeframe = timeframe
        self.top_n = top_n
        self.coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA"]

        # Load AI model once
        self.model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased", num_labels=3)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

        # Shared agents
        self.tech_agent = TechnicalAgent()
        self.decision_agent = DecisionAgent(self.model, self.tokenizer)
        self.calculate_agent = CalculateAgent(timeframe=self.timeframe)

    def analyze_coin(self, coin):
        try:
            print(f"\n🔎 Analyzing {coin}...")

            # Technical analysis
            tech_bias, tech_strength, tf = self.tech_agent.analyze(
                coin, self.timeframe)
            time.sleep(1)

            # Dummy text sentiment (in a full system, fetch latest news)
            sentiment_text = f"{coin} latest price trend and news show {tech_bias.lower()} signals."

            action, conf, sentiment, tech_bias, tf = self.decision_agent.analyze(
                sentiment_text, tech_bias, self.timeframe
            )

            result = self.calculate_agent.calculate(
                action, conf, self.portfolio_value, coin)

            if result:
                score = conf * (1.2 if tech_bias == "BULLISH" else 0.8)
                result["score"] = score
                result["sentiment"] = sentiment
                result["tech_strength"] = tech_strength
                return result
            else:
                return None

        except Exception as e:
            print(f"⚠️ Failed to analyze {coin}: {e}")
            return None

    def find_best(self):
        print("🚀 Finding best trading opportunity among coins...")
        results = []

        for coin in self.coins:
            res = self.analyze_coin(coin)
            if res:
                results.append(res)

        if not results:
            print("❌ No valid trading opportunities found.")
            return None

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        print("\n🏆 Top Trading Candidates:")
        for i, r in enumerate(results[:self.top_n]):
            print(
                f"#{i+1}: {r['action']} {r['score']:.3f} | "
                f"{r['confidence']:.3f} conf | {r['current_price']} USD ({r['timeframe']})"
            )

        best = results[0]
        print(
            f"\n✅ Best Coin: {best['action']} {best['score']:.3f} on {best['timeframe']}")
        return best
