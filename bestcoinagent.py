# bestcoinagent.py
from loadfinbertmodel import load_finbert
from decisionagent import DecisionAgent
from technicalagent import TechnicalAgent
from newscollector import NewsCollector


class BestCoinAgent:
    def __init__(self, timeframe="4h", debug=False):
        self.timeframe = timeframe
        self.debug = debug
        self.model, self.tokenizer = load_finbert()
        self.decision_agent = DecisionAgent(self.model, self.tokenizer)
        self.tech_agent = TechnicalAgent()
        self.news_collector = NewsCollector()
        self.coins = ["BTC", "ETH", "BNB", "SOL", "ADA"]

    def run(self):
        print(
            f"🔍 Scanning {len(self.coins)} coins for the best trading opportunity ({self.timeframe})...\n")

        results = []
        for coin in self.coins:
            print(f"🧩 Analyzing {coin}...")

            # Technical
            tech_bias, tech_strength, tf = self.tech_agent.analyze(
                coin, self.timeframe)

            # News
            news_texts = self.news_collector.collect(coin)
            if not news_texts:
                sentiment, sentiment_score = "NEUTRAL", 0.0
            else:
                combined_score = 0
                for text in news_texts.values():
                    s, sc = self.decision_agent.analyze_sentiment(text)
                    combined_score += sc if s == "POSITIVE" else -sc
                sentiment = "POSITIVE" if combined_score > 0 else "NEGATIVE"
                sentiment_score = abs(combined_score / len(news_texts))

            # Combine
            total_score = (tech_strength + sentiment_score) / 2
            action = "LONG" if tech_bias == "BULLISH" and sentiment == "POSITIVE" else \
                     "SHORT" if tech_bias == "BEARISH" and sentiment == "NEGATIVE" else "HOLD"

            results.append({
                "coin": coin,
                "action": action,
                "tech_bias": tech_bias,
                "sentiment": sentiment,
                "score": total_score,
                "timeframe": tf
            })

        # Sort & display
        results.sort(key=lambda x: x["score"], reverse=True)
        print("\n🏆 Best Coins for Trading:")
        for r in results[:5]:
            print(
                f" - {r['coin']}: {r['action']} ({r['tech_bias']}, {r['sentiment']}) — score={r['score']:.2f}")

        best = results[0]
        print(
            f"\n✅ Recommended: {best['coin']} → {best['action']} ({best['tech_bias']}, {best['sentiment']})")
