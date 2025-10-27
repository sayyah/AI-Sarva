import torch
import torch.nn.functional as F


class DecisionAgent:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()
        self.labels = ["negative", "neutral", "positive"]

    def analyze(self, text, tech_bias=None, timeframe=None, debug=False):
        """Analyze news text and combine with technical bias."""
        if not text or len(text.strip()) < 30:
            if debug:
                print("⚠️ Skipping empty/short news text")
            return "HOLD", 1.0, "neutral", tech_bias, timeframe

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1)
            conf, pred = torch.max(probs, dim=1)

        sentiment_label = self.labels[pred.item()]
        confidence = conf.item()
        sentiment_bias = 1 if sentiment_label == "positive" else - \
            1 if sentiment_label == "negative" else 0

        final_action = "HOLD"
        combined_conf = confidence * 0.4 + \
            (0.6 if tech_bias in ["BULLISH", "BEARISH"] else 0.3)
        if tech_bias == "BULLISH" and sentiment_bias == 1:
            final_action = "LONG"
            combined_conf *= 1.2
        elif tech_bias == "BEARISH" and sentiment_bias == -1:
            final_action = "SHORT"
            combined_conf *= 1.2
        elif tech_bias == "NEUTRAL":
            final_action = "LONG" if sentiment_bias == 1 else "SHORT" if sentiment_bias == -1 else "HOLD"

        if debug:
            print("\n🧠 DEBUG SENTIMENT ANALYSIS")
            print(
                f"📰 Sentiment: {sentiment_label.upper()} (confidence={confidence:.4f})")
            print(f"📈 Technical Bias: {tech_bias} [{timeframe}]")
            print(
                f"⚙️ Combined Decision: {final_action} (confidence={combined_conf:.4f})")

        return final_action, combined_conf, sentiment_label, tech_bias, timeframe
