import os
import csv
import random
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
from rich.console import Console


class CalculateAgent:
    """
    This agent calculates entry/exit/stop levels based on volatility,
    determines trade size, and can simulate trade outcomes.
    """

    def __init__(self, portfolio_value: float):
        self.portfolio_value = portfolio_value
        self.console = Console()
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    # -----------------------------------------------------------------
    def calculate_prices(self, coin: str, action: str, timeframe: str = "4h"):
        """Calculate trade levels dynamically using recent volatility."""
        ticker = f"{coin}-USD"
        self.console.print(
            f"\n💰 [cyan]Calculating trade levels for[/] {ticker} ({timeframe})...")

        # Select historical range based on timeframe
        if "d" in timeframe:
            period, interval = "90d", "1d"
        elif "h" in timeframe:
            period, interval = "30d", timeframe
        else:
            period, interval = "7d", "1h"

        try:
            data = yf.download(ticker, period=period,
                               interval=interval, progress=False)
        except Exception as e:
            self.console.print(
                f"⚠️ [red]Error fetching market data for {ticker}: {e}[/]")
            return None, None, None, None

        if data.empty:
            self.console.print(
                f"⚠️ [red]No data found for {ticker} {timeframe}[/]")
            return None, None, None, None

        # Average True Range (simplified)
        data["HL_range"] = data["High"] - data["Low"]
        atr = data["HL_range"].rolling(window=14).mean().iloc[-1]
        current_price = float(data["Close"].iloc[-1])

        risk_pct, reward_pct = 0.03, 0.05
        if atr > 0:
            vol_factor = min(2.0, max(0.5, atr / current_price * 50))
            risk_pct *= vol_factor
            reward_pct *= vol_factor

        if action == "LONG":
            entry_price = current_price
            exit_price = current_price * (1 + reward_pct)
            stop_loss = current_price * (1 - risk_pct)
            emoji, color = "⬆️", "green"
        elif action == "SHORT":
            entry_price = current_price
            exit_price = current_price * (1 - reward_pct)
            stop_loss = current_price * (1 + risk_pct)
            emoji, color = "⬇️", "red"
        else:  # HOLD
            entry_price = exit_price = stop_loss = current_price
            emoji, color = "⚖️", "yellow"

        trade_amount = min(self.portfolio_value * 0.2,
                           self.portfolio_value * reward_pct)

        self.console.print(
            f"[bold {color}]{emoji} {action}[/] | "
            f"Entry: [cyan]{entry_price:.2f}[/], Exit: [green]{exit_price:.2f}[/], "
            f"Stop: [red]{stop_loss:.2f}[/], Trade Size: [bold]{trade_amount:.2f} USD[/]"
        )

        return entry_price, exit_price, stop_loss, current_price

    # -----------------------------------------------------------------
    def simulate_trade(
        self, coin: str, action: str, entry: float, exit_price: float, stop_loss: float, current_price: float
    ):
        """Simulates trade performance and logs it."""
        self.console.print("\n🎮 [yellow]Simulating trade outcome...[/]")

        if action == "HOLD":
            self.console.print(
                "⚖️ [blue]No trade executed (HOLD decision).[/]")
            return None

        # Simulate random market movement outcome
        outcome = random.choice(["win", "loss"])
        final_price = exit_price if outcome == "win" else stop_loss

        pnl_percent = ((final_price - entry) / entry) * \
            100 if action == "LONG" else ((entry - final_price) / entry) * 100
        pnl_amount = (pnl_percent / 100) * self.portfolio_value * \
            0.2  # assume 20% of portfolio per trade

        self.console.print(
            f"📊 [cyan]{coin}[/]: {action} {outcome.upper()} → "
            f"P/L: [bold {'green' if pnl_percent > 0 else 'red'}]{pnl_percent:.2f}%[/] "
            f"(${pnl_amount:.2f})"
        )

        self.log_trade(coin, action, entry, final_price,
                       pnl_percent, pnl_amount, outcome)
        return pnl_percent, pnl_amount

    # -----------------------------------------------------------------
    def log_trade(self, coin, action, entry, final_price, pnl_percent, pnl_amount, outcome):
        """Logs trade result into CSV."""
        report_file = os.path.join(self.reports_dir, "trade_history.csv")
        headers = ["Date", "Coin", "Action", "Entry",
                   "Exit", "PnL %", "PnL $", "Outcome"]

        file_exists = os.path.isfile(report_file)
        with open(report_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    coin,
                    action,
                    f"{entry:.2f}",
                    f"{final_price:.2f}",
                    f"{pnl_percent:.2f}",
                    f"{pnl_amount:.2f}",
                    outcome,
                ]
            )
        self.console.print(f"🧾 [green]Trade logged to[/] {report_file}")
