import yfinance as yf
import numpy as np
from datetime import datetime


class CalculateAgent:
    """
    CalculateAgent is responsible for determining key trade levels such as
    entry price, exit price, and stop loss, based on technical bias and action.
    """

    def __init__(self, portfolio_value: float):
        self.portfolio_value = portfolio_value

    def fetch_price(self, coin: str):
        """
        Fetches the most recent price for the given coin symbol.
        """
        try:
            # Normalize ticker: remove duplicates and ensure proper format
            coin = self._normalize_ticker(coin)
            ticker = f"{coin}-USD"
            data = yf.download(ticker, period="7d",
                               interval="1h", progress=False)

            if data.empty:
                print(f"⚠️ No data found for {ticker}")
                return None

            return float(data["Close"].iloc[-1])
        except Exception as e:
            print(f"⚠️ Failed to fetch price for {coin}: {e}")
            return None

    def _normalize_ticker(self, coin: str) -> str:
        """
        Cleans up the ticker format (e.g. removes duplicate suffixes or invalid endings).
        Examples:
            BTC -> BTC
            BTC-USD -> BTC
            ETHUSDT -> ETH
            ADA-USDT -> ADA
        """
        # If there’s a dash, take the part before it
        if "-" in coin:
            coin = coin.split("-")[0]

        # Remove stablecoin suffixes if they exist
        for suffix in ["USDT", "USD", "TETHER", "BUSD"]:
            if coin.upper().endswith(suffix):
                coin = coin[: -len(suffix)]

        return coin.upper()

    def calculate_prices(self, coin: str, action: str):
        """
        Calculates trade prices based on the action and coin data.
        Returns (entry_price, exit_price, stop_loss, current_price)
        """
        current_price = self.fetch_price(coin)
        if current_price is None or current_price <= 0:
            # Return flat dummy values so code won't break
            return 0, 0, 0, 0

        # Risk/reward assumptions
        risk_pct = 0.03
        reward_pct = 0.05

        if action.upper() == "LONG":
            entry_price = current_price
            stop_loss = current_price * (1 - risk_pct)
            exit_price = current_price * (1 + reward_pct)
        elif action.upper() == "SHORT":
            entry_price = current_price
            stop_loss = current_price * (1 + risk_pct)
            exit_price = current_price * (1 - reward_pct)
        else:
            # HOLD or unknown actions
            entry_price = exit_price = stop_loss = current_price

        # Round for readability
        entry_price = round(entry_price, 2)
        exit_price = round(exit_price, 2)
        stop_loss = round(stop_loss, 2)
        current_price = round(current_price, 2)

        return entry_price, exit_price, stop_loss, current_price

    def calculate(self, coin: str, action: str):
        """
        Backward-compatible alias for calculate_prices().
        Some agents still call `calculate()` — this keeps it working.
        """
        return self.calculate_prices(coin, action)

    def position_size(self, action: str, confidence: float):
        """
        Determines position size based on portfolio value and model confidence.
        """
        # Minimum trade fraction = 10%
        base_fraction = 0.1
        size = self.portfolio_value * (base_fraction + confidence * 0.4)

        return round(size, 2)

    def report(self, coin: str, action: str, entry, exit_price, stop, current):
        """
        Creates a readable text report of the trade.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        report = (
            f"\n📊 TRADE REPORT ({timestamp})"
            f"\n🪙 Coin: {coin}"
            f"\n🎯 Action: {action.upper()}"
            f"\n💰 Entry: {entry}"
            f"\n📈 Exit Target: {exit_price}"
            f"\n🛑 Stop Loss: {stop}"
            f"\n💹 Current Price: {current}\n"
        )
        return report
