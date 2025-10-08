import yfinance as yf


class CalculateAgent:
    def calculate(self, action, confidence, portfolio, coin):
        try:
            ticker = f"{coin}-USD"
            data = yf.download(ticker, period="1d", interval="1h")
            if data.empty:
                raise ValueError(f"No market data for {ticker}")

            current_price = float(data["Close"].iloc[-1])

            # Cap confidence to avoid overconfidence (e.g., 1.0)
            confidence = min(confidence, 0.999)

            # If HOLD, skip trade details
            if action == "HOLD":
                return {
                    "action": action,
                    "confidence": round(confidence, 4),
                    "amount": 0.0,
                    "entry_price": None,
                    "exit_price": None,
                    "stop_loss": None,
                    "current_price": round(current_price, 2),
                    "note": "Holding position, no trade executed."
                }

            trade_amount = portfolio * confidence / 5
            entry_price = current_price
            stop_loss = current_price * (0.97 if action == "LONG" else 1.03)
            exit_price = current_price * (1.05 if action == "LONG" else 0.95)

            return {
                "action": action,
                "confidence": round(confidence, 4),
                "amount": round(trade_amount, 2),
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "stop_loss": round(stop_loss, 2),
                "current_price": round(current_price, 2),
            }

        except Exception as e:
            print(f"⚠️ Calculation failed for {coin}: {e}")
            return None
