import torch
import torch.nn.functional as F


class DecisionAgent:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def analyze(self, text):
        """
        Analyze sentiment of the news and convert it to a trading action.
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)
            sentiment = torch.argmax(probs).item()
            confidence = float(torch.max(probs))

        label_map = {0: "SHORT", 1: "HOLD", 2: "LONG"}
        action = label_map.get(sentiment, "HOLD")

        return action, confidence
