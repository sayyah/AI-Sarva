import argparse
import json
import os
from datetime import datetime
from loadfinbertmodel import load_finbert
from decisionagent import DecisionAgent
from technicalagent import TechnicalAgent
from newscollector import NewsCollector
from calculates import CalculateAgent
from urls import COIN_URLS
from rich.console import Console
from rich.table import Table


class MainAgent:
    def __init__(self, coin_name, portfolio_value, timeframe="4h", debug=False, report=False, findbest=False):
        self.coin_name = coin_name.upper() if coin_name else None
        self.portfolio_value = portfolio_value
        self.timeframe = timeframe
        self.debug = debug
        self.report = report
        self.findbest = findbest

        self.console = Console()
        self.console.print(
            f"🪙 [bold cyan]Initializing MainAgent[/] ({'FindBest Mode' if findbest else self.coin_name}) | [yellow]{self.timeframe}[/]")

        self.model, self.tokenizer = load_finbert()
        self.technical_agent = TechnicalAgent()
        self.decision_agent = DecisionAgent(self.model, self.tokenizer)
        self.trade_calc = CalculateAgent(portfolio_value=self.portfolio_value)

        if self.report:
            os.makedirs("reports", exist_ok=True)

    # -------------------------------------------------------------------------
    def analyze_coin(self, coin):
        """Perform full analysis for a single coin."""
        self.console.print(f"\n🔍 [bold yellow]Analyzing {coin}...[/]")

        urls = COIN_URLS.get(coin, [])
        if not urls:
            self.console.print(
                f"⚠️ No URLs found for {coin}. Skipping.", style="red")
            return None

        news_collector = NewsCollector(urls)

        # --- Technical analysis ---
        tech_bias, strength, tf, reason = self.technical_agent.analyze(
            coin, self.timeframe)
        self.console.print(
            f"📊 [bold blue]Technical bias:[/] {tech_bias} ({strength:.2f}) [{tf}] → {reason}")

        # --- News collection ---
        news_texts = news_collector.collect()
        if not news_texts:
            self.console.print(f"⚠️ No news articles for {coin}.", style="red")
            return None

        best_decision = None

        for url, text in news_texts.items():
            self.console.print(
                f"\n🧠 [bold]Analyzing sentiment for[/] {coin}: [cyan]{url}[/]")

            action, conf, sentiment, tech_bias, tf = self.decision_agent.analyze(
                text, tech_bias=tech_bias, timeframe=tf, debug=self.debug
            )

            # ✅ FIXED unpack
            entry_price, exit_price, stop_loss, current_price = self.trade_calc.calculate_prices(
                coin, action)

            self.console.print(
                f"🗞️ [green]{coin}[/] | Sentiment: [bold]{sentiment}[/], "
                f"Tech: [bold]{tech_bias}[/], Action: [bold yellow]{action}[/], "
                f"Conf: {conf:.3f}, Entry: {entry_price:.2f}"
            )

            decision = {
                "coin": coin,
                "url": url,
                "sentiment": sentiment,
                "tech_bias": tech_bias,
                "action": action,
                "confidence": conf,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "stop_loss": stop_loss,
                "current_price": current_price,
                "reason": reason,
                "timeframe": tf,
                "timestamp": datetime.now().isoformat(),
            }

            if best_decision is None or conf > best_decision["confidence"]:
                best_decision = decision

            # Save per-coin report
            if self.report:
                with open(f"reports/{coin}_report.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(decision) + "\n")

        return best_decision

    # -------------------------------------------------------------------------
    def run(self):
        """Main execution flow."""
        if self.findbest:
            self.console.print(
                "\n🚀 [bold green]FindBest mode activated — scanning all coins...[/]\n")
            all_results = []

            for coin in COIN_URLS.keys():
                result = self.analyze_coin(coin)
                if result:
                    all_results.append(result)

            if not all_results:
                self.console.print(
                    "⚠️ No valid results from any coin.", style="red")
                return

            # Create visual summary table
            table = Table(title="📊 Trading Summary", style="bold white")
            table.add_column("Coin", style="cyan", justify="center")
            table.add_column("Sentiment", style="magenta", justify="center")
            table.add_column("Tech Bias", style="blue", justify="center")
            table.add_column("Action", style="yellow", justify="center")
            table.add_column("Confidence", style="green", justify="center")
            table.add_column("Entry", justify="right")
            table.add_column("Exit", justify="right")
            table.add_column("Stop", justify="right")

            for r in all_results:
                table.add_row(
                    r["coin"],
                    r["sentiment"],
                    r["tech_bias"],
                    r["action"],
                    f"{r['confidence']:.2%}",
                    f"{r['entry_price']:.2f}",
                    f"{r['exit_price']:.2f}",
                    f"{r['stop_loss']:.2f}",
                )

            self.console.print(table)

            best = max(all_results, key=lambda r: r["confidence"])
            self.console.print(
                f"\n🏆 [bold green]BEST TRADE:[/] {best['coin']} → [bold yellow]{best['action']}[/] "
                f"({best['confidence']:.2%}) | Tech: {best['tech_bias']}, Sent: {best['sentiment']}"
            )

            # Save report
            if self.report:
                with open("reports/best_trade.json", "w", encoding="utf-8") as f:
                    json.dump(best, f, indent=2)
            return

        # Normal mode
        result = self.analyze_coin(self.coin_name)
        if not result:
            self.console.print("⚠️ No actionable result.", style="red")
            return

        self.console.print("\n✅ [bold green]FINAL DECISION[/]")
        self.console.print(
            f"🎯 {result['coin']} → [yellow]{result['action']}[/] "
            f"({result['confidence']:.2%}) | Sentiment={result['sentiment']} | Tech={result['tech_bias']}"
        )
        self.console.print(
            f"💹 Entry={result['entry_price']:.2f}, Exit={result['exit_price']:.2f}, "
            f"Stop={result['stop_loss']:.2f}"
        )


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crypto AI Trading Agent with Technical & News Analysis")
    parser.add_argument("--coin", help="Coin symbol (e.g. BTC, ETH, BNB)")
    parser.add_argument("--portfolio", type=float,
                        required=True, help="Total portfolio value in USD")
    parser.add_argument("--timeframe", default="4h",
                        help="Technical analysis timeframe")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--report", action="store_true",
                        help="Save report files")
    parser.add_argument("--findbest", action="store_true",
                        help="Analyze all coins and pick the best one")

    args = parser.parse_args()

    agent = MainAgent(
        coin_name=args.coin,
        portfolio_value=args.portfolio,
        timeframe=args.timeframe,
        debug=args.debug,
        report=args.report,
        findbest=args.findbest,
    )

    agent.run()
