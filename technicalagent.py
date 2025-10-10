# technicalagent.py
import yfinance as yf
import pandas as pd
import numpy as np
from database import Database


class TechnicalAgent:
    def __init__(self):
        self.db = Database()

    def analyze(self, coin_name, timeframe="4h"):
        ticker = f"{coin_name.upper()}-USD"
        print(f"📊 Performing technical analysis for {ticker} ({timeframe})...")

        if timeframe in ["1h", "4h"]:
            period = "30d"
        elif timeframe in ["1d", "1wk"]:
            period = "180d"
        else:
            period = "90d"

        try:
            data = yf.download(ticker, period=period,
                               interval=timeframe, progress=False)
        except Exception as e:
            print(f"⚠️ Failed to download data for {ticker}: {e}")
            return "UNKNOWN", 0.0, timeframe, "Download error"

        if data.empty:
            print(f"⚠️ No data found for {coin_name} {timeframe}")
            return "UNKNOWN", 0.0, timeframe, "No market data available"

        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        delta = data["Close"].diff()
        gain = np.where(delta > 0, delta, 0).flatten()
        loss = np.where(delta < 0, -delta, 0).flatten()
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        ema12 = data["Close"].ewm(span=12, adjust=False).mean()
        ema26 = data["Close"].ewm(span=26, adjust=False).mean()
        data["MACD"] = ema12 - ema26
        data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

        latest = data.iloc[-1]
        close = float(latest["Close"])
        ma20 = float(latest["MA20"])
        ma50 = float(latest["MA50"])
        rsi = float(latest["RSI"])
        macd = float(latest["MACD"])
        signal = float(latest["Signal"])

        print(f"🔹 Close: {close:.2f}")
        print(f"🔹 MA20: {ma20:.2f}")
        print(f"🔹 MA50: {ma50:.2f}")
        print(f"🔹 RSI: {rsi:.2f}")
        print(f"🔹 MACD: {macd:.4f}, Signal: {signal:.4f}")

        bias = "NEUTRAL"
        strength = 0.1
        reasons = []

        if ma20 > ma50:
            bias = "BULLISH"
            reasons.append("MA20 > MA50 (uptrend)")
        elif ma20 < ma50:
            bias = "BEARISH"
            reasons.append("MA20 < MA50 (downtrend)")

        if rsi > 70:
            bias = "BEARISH"
            reasons.append("RSI > 70 (overbought)")
        elif rsi < 30:
            bias = "BULLISH"
            reasons.append("RSI < 30 (oversold)")

        if macd > signal:
            reasons.append("MACD > Signal (momentum rising)")
        elif macd < signal:
            reasons.append("MACD < Signal (momentum falling)")

        reason_text = "; ".join(reasons)
        print(
            f"✅ Technical bias: {bias} (strength={strength:.2f}) using {timeframe}")
        print(f"📘 Reason: {reason_text}")

        # 🔹 Save to DB
        self.db.save_technical(coin_name.upper(), timeframe,
                               bias, strength, reason_text)

        return bias, strength, timeframe, reason_text
