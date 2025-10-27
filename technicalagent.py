# technicalagent.py
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta


class TechnicalAgent:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def sanitize_ticker(self, coin: str) -> str:
        """
        Normalize coin name to Yahoo Finance compatible ticker (e.g., BTC → BTC-USD)
        If the coin already contains '-', sanitize it to prevent double suffixes.
        """
        coin = coin.strip().upper()

        # remove any invalid double suffixes like BTC-USD-USD
        if "-" in coin:
            parts = coin.split("-")
            base = parts[0]
            if len(parts) > 1 and parts[1] != "USD":
                return f"{base}-USD"
            return f"{base}-USD"

        # Normal mapping
        if coin.endswith("USDT"):
            coin = coin.replace("USDT", "")
        elif coin.endswith("USD"):
            coin = coin.replace("USD", "")

        return f"{coin}-USD"

    def analyze(self, coin: str, timeframe: str = "4h"):
        ticker = self.sanitize_ticker(coin)
        period = "30d" if "h" in timeframe else "180d"

        if self.debug:
            print(
                f"\n📊 Performing technical analysis for {ticker} ({timeframe})...")

        try:
            data = yf.download(
                ticker, period=period, interval=timeframe, progress=False
            )
        except Exception as e:
            print(f"⚠️ Failed to fetch data for {ticker}: {e}")
            return "UNKNOWN", 0, timeframe, "No data"

        if data.empty:
            print(f"⚠️ No data found for {ticker} {timeframe}")
            return "UNKNOWN", 0, timeframe, "No data"

        # Compute indicators safely
        try:
            data["MA20"] = data["Close"].rolling(window=20).mean()
            data["MA50"] = data["Close"].rolling(window=50).mean()

            # RSI
            delta = data["Close"].diff()
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = pd.Series(gain.flatten()).rolling(14).mean()
            avg_loss = pd.Series(loss.flatten()).rolling(14).mean()
            rs = avg_gain / avg_loss
            data["RSI"] = 100 - (100 / (1 + rs))

            # MACD
            macd = ta.macd(data["Close"], fast=12, slow=26, signal=9)
            if macd is not None:
                data["MACD"] = macd["MACD_12_26_9"]
                data["Signal"] = macd["MACDs_12_26_9"]
            else:
                data["MACD"] = np.nan
                data["Signal"] = np.nan

        except Exception as e:
            print(f"⚠️ Indicator computation failed for {ticker}: {e}")
            return "UNKNOWN", 0, timeframe, "Indicator failure"

        latest = data.tail(1)
        close = float(latest["Close"].iloc[0])
        ma20 = float(latest["MA20"].iloc[0])
        ma50 = float(latest["MA50"].iloc[0])
        rsi = float(latest["RSI"].iloc[0])
        macd_val = float(latest["MACD"].iloc[0])
        signal = float(latest["Signal"].iloc[0])

        if self.debug:
            print(f"🔹 Close: {close}")
            print(f"🔹 MA20: {ma20}")
            print(f"🔹 MA50: {ma50}")
            print(f"🔹 RSI: {rsi}")
            print(f"🔹 MACD: {macd_val}, Signal: {signal}")

        # Interpretation
        reason = []
        bias = "NEUTRAL"
        strength = 0.1

        if ma20 > ma50:
            bias = "BULLISH"
            reason.append("MA20 > MA50 (uptrend)")
        elif ma20 < ma50:
            bias = "BEARISH"
            reason.append("MA20 < MA50 (downtrend)")

        if rsi > 70:
            reason.append("RSI > 70 (overbought)")
        elif rsi < 30:
            reason.append("RSI < 30 (oversold)")

        if macd_val > signal:
            reason.append("MACD > Signal (bullish momentum)")
        else:
            reason.append("MACD < Signal (momentum falling)")

        if self.debug:
            print(
                f"✅ Technical bias: {bias} (strength={strength:.2f}) using {timeframe}")
            print(f"📘 Reason: {'; '.join(reason)}")

        return bias, strength, timeframe, "; ".join(reason)
