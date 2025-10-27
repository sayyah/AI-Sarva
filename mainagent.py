import argparse
from decisionagent import DecisionAgent
from technicalagent import TechnicalAgent
from newscollector import NewsCollector
from calculates import CalculateAgent
from findbestagent import FindBestAgent
from datetime import datetime


class MainAgent:
    def __init__(self, coin_name, portfolio_value, timeframe="4h", debug=False, report=False):
        self.coin_name = coin_name.upper()
        self.portfolio_value = portfolio_value
        self.timeframe = timeframe
        self.debug = debug
        self.report = report

        self.technical_agent = TechnicalAgent()
        self.decision_agent = DecisionAgent()
        self.trade_calc = CalculateAgent(portfolio_value)

        # Initialize NewsCollector for this specific coin
        self.news_collector = NewsCollector(coin=self.coin_name)

        print(
            f"🪙 Initializing MainAgent for {self.coin_name} (Timeframe: {self.timeframe})")

    def analyze_coin(self, coin):
        if self.debug:
            print(f"🔎 Starting analysis for {coin}...")

        # ---- Step 1: Technical Analysis ----
        tech_bias, strength, tf, reason = self.technical_agent.analyze(
            coin, self.timeframe)
        if self.debug:
            print(
                f"📊 Technical bias: {tech_bias} ({strength:.2f}) [{tf}] → {reason}")

        # ---- Step 2: Collect News ----
        news_collector = NewsCollector(coin)
        news_texts = news_collector.collect_news()
        if not news_texts:
            print(f"⚠️ No news articles for {coin}.")
            return None

        if self.debug:
            print(f"📰 Collected {len(news_texts)} news articles for {coin}")

        # ---- Step 3: Analyze Sentiment ----
        combined_results = []
        for url, text in news_texts.items():
            if self.debug:
                print(f"\n🧠 Analyzing news sentiment for: {url}")

            sentiment, confidence = self.decision_agent.classify_news(text)

            if self.debug:
                print(f"🧠 DEBUG SENTIMENT ANALYSIS")
                print(
                    f"📰 Sentiment: {sentiment.upper()} (confidence={confidence:.4f})")
                print(f"📈 Technical Bias: {tech_bias} [{tf}]")

            # Combine sentiment + technical
            action, final_conf = self.decision_agent.combine_signals(
                sentiment, confidence, tech_bias, strength
            )

            if self.debug:
                print(
                    f"⚙️ Combined Decision: {action.upper()} ({final_conf*100:.2f}%)")

            # ---- Step 4: Trading Calculation ----
            entry_price, exit_price, stop_loss, current_price = self.trade_calc.calculate(
                coin, action
            )

            result = {
                "url": url,
                "decision": {
                    "action": action,
                    "confidence": round(final_conf, 4),
                    "amount": round((self.portfolio_value * final_conf) / 5, 2),
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "stop_loss": stop_loss,
                    "current_price": current_price,
                    "sentiment": sentiment,
                    "technical": tech_bias,
                },
            }

            combined_results.append(result)

        # ---- Step 5: Reporting ----
        self.display_results(combined_results)
        if self.report:
            self.save_report(combined_results, coin)

        return combined_results

    def display_results(self, results):
        print("\n✅ FINAL DECISIONS")
        for res in results:
            d = res["decision"]
            print(
                f"🎯 {res['url']}\n"
                f"→ {d['action']} ({d['confidence']*100:.2f}%) | "
                f"Sentiment={d['sentiment']} | Tech={d['technical']}\n"
                f"💹 Entry={d['entry_price']}, Exit={d['exit_price']}, Stop={d['stop_loss']}\n"
            )

    def save_report(self, results, coin):
        import json
        import os

        filename = f"reports/{coin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("reports", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"📊 Report saved to {filename}")

    def run(self):
        self.analyze_coin(self.coin_name)


# ---------------------- ENTRY POINT ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI Trading Agent (News + Technical)")
    parser.add_argument("--coin", type=str, help="Coin name (e.g., BTC, ETH)")
    parser.add_argument("--portfolio", type=float,
                        required=True, help="Total portfolio value")
    parser.add_argument("--timeframe", type=str,
                        default="4h", help="Timeframe for analysis")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")
    parser.add_argument("--report", action="store_true",
                        help="Save report to file")
    parser.add_argument("--findbest", action="store_true",
                        help="Find best coin for long position")

    args = parser.parse_args()

    # ---- Find Best Coin ----
    if args.findbest:
        from findbestagent import FindBestAgent

        finder = FindBestAgent(
            portfolio_value=args.portfolio,
            timeframe=args.timeframe,
            debug=args.debug,
        )
        finder.run()
    else:
        # ---- Run Standard Analysis ----
        if not args.coin:
            parser.error("--coin is required unless --findbest is used")

        agent = MainAgent(
            coin_name=args.coin,
            portfolio_value=args.portfolio,
            timeframe=args.timeframe,
            debug=args.debug,
            report=args.report,
        )
        agent.run()
