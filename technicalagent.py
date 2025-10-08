import yfinance as yf
import pandas as pd
import numpy as np


class TechnicalAgent:
    def __init__(self):
        pass

    def analyze(self, coin_symbol: str, timeframe: str = "4h"):
        """
        Perform simple technical analysis on the given coin using Yahoo Finance data.
        Returns: (bias, strength, timeframe)
        """
        print(
            f"📊 Performing technical analysis for {coin_symbol} ({timeframe})...")

        ticker = f"{coin_symbol}-USD"

        # Choose interval & period based on timeframe
        if timeframe == "1h":
            interval = "1h"
            period = "7d"
        elif timeframe == "4h":
            interval = "4h"
            period = "30d"
        elif timeframe == "1d":
            interval = "1d"
            period = "180d"
        else:
            interval = "4h"
            period = "30d"

        try:
            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
        except Exception as e:
            print(f"⚠️ Failed to load chart data: {e}")
            return "NEUTRAL", 0.0, timeframe

        if data.empty:
            print("⚠️ No chart data found.")
            return "NEUTRAL", 0.0, timeframe

        # Calculate indicators
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()
        data["RSI"] = self.calculate_rsi(data["Close"])
        data["MACD"], data["Signal"] = self.calculate_macd(data["Close"])

        # Ensure indicators are not NaN for latest row
        data = data.dropna()
        if data.empty:
            print("⚠️ Not enough data for technical indicators.")
            return "NEUTRAL", 0.0, timeframe

        latest = data.iloc[-1]

        bias, strength = self.interpret_indicators(latest)
        print(
            f"✅ Technical bias: {bias} (strength={strength:.2f}) using {timeframe}")
        return bias, strength, timeframe

    # --------------------------
    # Helper Functions
    # --------------------------
    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, series, fast=12, slow=26, signal=9):
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    def interpret_indicators(self, latest):
        """
        Decide bullish / bearish / neutral bias based on last candle indicators.
        """
        close = float(latest["Close"].iloc[0]) if hasattr(
            latest["Close"], "iloc") else float(latest["Close"])
        ma20 = float(latest["MA20"].iloc[0]) if hasattr(
            latest["MA20"], "iloc") else float(latest["MA20"])
        ma50 = float(latest["MA50"].iloc[0]) if hasattr(
            latest["MA50"], "iloc") else float(latest["MA50"])
        rsi = float(latest["RSI"].iloc[0]) if hasattr(
            latest["RSI"], "iloc") else float(latest["RSI"])
        macd = float(latest["MACD"].iloc[0]) if hasattr(
            latest["MACD"], "iloc") else float(latest["MACD"])
        signal = float(latest["Signal"].iloc[0]) if hasattr(
            latest["Signal"], "iloc") else float(latest["Signal"])

        bias = "NEUTRAL"
        strength = 0.0

        # Trend via MA cross
        if ma20 > ma50:
            bias = "BULLISH"
            strength += 0.4
        elif ma20 < ma50:
            bias = "BEARISH"
            strength += 0.4

        # RSI
        if rsi < 30:
            bias = "BULLISH"
            strength += 0.3
        elif rsi > 70:
            bias = "BEARISH"
            strength += 0.3

        # MACD
        if macd > signal:
            strength += 0.3
        else:
            strength -= 0.3

        strength = max(0.0, min(1.0, abs(strength)))
        return bias, strength
