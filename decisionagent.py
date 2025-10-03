# decisionagent.py
import torch


class DecisionAgent:
    def __init__(self, model, tokenizer, portfolio_value=1000):
        self.model = model
        self.tokenizer = tokenizer
        self.portfolio_value = portfolio_value

    def analyze(self, text):
        """
        Analyze sentiment of the given text and return trading decision.
        """
        # Use tokenizer correctly
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze()
        label_id = torch.argmax(probs).item()

        sentiment = ["negative", "neutral", "positive"][label_id]
        confidence = probs[label_id].item()

        action = "HOLD"
        if sentiment == "positive":
            action = "LONG"
        elif sentiment == "negative":
            action = "SHORT"

        amount = round(self.portfolio_value * confidence, 2)

        return {
            "sentiment": sentiment,
            "action": action,
            "amount": amount,
            "confidence": round(confidence, 2)
        }
