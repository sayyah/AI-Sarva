import yfinance as yf
from decisionagent import DecisionAgent
from technicalagent import TechnicalAgent
from calculates import CalculateAgent
from transformers import BertTokenizer, BertForSequenceClassification
import requests


class FindBestAgent:
    def __init__(self, portfolio_value, timeframe="4h", debug=False):
        self.portfolio_value = portfolio_value
        self.timeframe = timeframe
        self.debug = debug

        # Load BERT model & tokenizer once for reuse
        model_name = "bert-base-uncased"
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)

        self.decision_agent = DecisionAgent(self.model, self.tokenizer)
        self.technical_agent = TechnicalAgent()
        self.trade_calc = CalculateAgent(portfolio_value)

        self.api_url = "https://apiv2.nobitex.ir/market/stats"

    # --- Helper: Fetch all markets from Nobitex ---
    def fetch_nobitex_markets(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            data = response.json()
            markets = list(data.get("stats", {}).keys())
            # Filter out anything with 'rls' and only USD/USDT pairs
            clean = [m.replace("-", "").upper()
                     for m in markets if "rls" not in m.lower()]
            return clean
        except Exception as e:
            print(f"⚠️ Failed to fetch Nobitex data: {e}")
            return []

    # --- Helper: normalize coin name for yfinance ---
    def format_ticker(self, coin):
        """Convert coin to Yahoo Finance ticker like BTC-USD"""
        if "-" in coin:
            coin = coin.split("-")[0]
        if "USD" in coin:
            return f"{coin}-USD"
        elif "USDT" in coin:
            return f"{coin.replace('USDT', '')}-USD"
        return f"{coin}-USD"

    # --- Analyze one coin ---
    def analyze_coin(self, coin):
        ticker = self.format_ticker(coin)
        if self.debug:
            print(f"\n📊 Analyzing {ticker}...")

        try:
            tech_bias, strength, tf, reason = self.technical_agent.analyze(
                coin, self.timeframe)
        except Exception as e:
            print(f"⚠️ No data for {coin}: {e}")
            return None

        # Only keep coins with clear bullish signal
        if tech_bias != "BULLISH":
            return None

        entry, exit_price, stop, current = self.trade_calc.calculate(
            coin, "LONG")
        return {
            "coin": coin,
            "bias": tech_bias,
            "strength": round(strength, 2),
            "reason": reason,
            "entry": entry,
            "exit": exit_price,
            "stop": stop,
            "current": current,
        }

    # --- Main runner ---
    def run(self):
        coins = self.fetch_nobitex_markets()
        if not coins:
            print("⚠️ No data fetched from Nobitex.")
            return

        print(f"📈 Checking {len(coins)} coins from Nobitex...")

        best_trades = []
        for coin in coins:
            result = self.analyze_coin(coin)
            if result:
                best_trades.append(result)

        if not best_trades:
            print("⚠️ No bullish coins found.")
            return

        # Rank by strength
        best_trades = sorted(
            best_trades, key=lambda x: x["strength"], reverse=True)
        best = best_trades[0]

        print(
            f"\n🏆 BEST TRADE: {best['coin']} → LONG ({best['strength']*100:.2f}%) | "
            f"Tech: {best['bias']}, Reason: {best['reason']}"
        )

        # Save CSV summary
        import pandas as pd
        import os

        os.makedirs("reports", exist_ok=True)
        pd.DataFrame(best_trades).to_csv(
            "reports/findbest_results.csv", index=False)
        print("📄 Results saved to reports/findbest_results.csv")
