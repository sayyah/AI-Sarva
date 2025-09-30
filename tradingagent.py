# tradingagent.py

import torch
from loadfinbertmodel import load_finbert


class TradingAgent:
    def __init__(self):
        self.tokenizer, self.model = load_finbert()
        self.labels = ["positive", "negative", "neutral"]

    def analyze_sentiment(self, text):
        inputs = self.tokenizer(text, return_tensors="pt",
                                truncation=True, max_length=512)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        sentiment = self.labels[probs.argmax()]
        confidence = float(probs.max())
        return sentiment, confidence

    def trading_decision(self, text, portfolio_value=1000):
        sentiment, confidence = self.analyze_sentiment(text)

        if sentiment == "positive":
            action = "LONG"
        elif sentiment == "negative":
            action = "SHORT"
        else:
            return {"action": "NO_TRADE", "amount": 0, "confidence": confidence}

        # Scale allocation: confidence * 20% max
        allocation = confidence * 0.2
        trade_amount = round(portfolio_value * allocation, 2)

        return {"action": action, "amount": trade_amount, "confidence": round(confidence, 2)}
