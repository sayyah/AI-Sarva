import torch
import torch.nn.functional as F


class DecisionAgent:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()  # set BERT to inference mode

        # sentiment labels
        self.labels = ["negative", "neutral", "positive"]

    def analyze(self, text, tech_bias=None, timeframe=None, debug=False):
        """
        Analyze news text and combine with technical analysis to make a decision.
        Returns: action, confidence, sentiment_label, tech_bias, timeframe
        """
        if not text or len(text.strip()) < 30:
            if debug:
                print("⚠️ Skipping empty/short news text")
            return "HOLD", 1.0, "neutral", tech_bias, timeframe

        # Tokenize the input
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

        # 🧩 Determine news-based sentiment direction
        sentiment_bias = 0
        if sentiment_label == "positive":
            sentiment_bias = +1
        elif sentiment_label == "negative":
            sentiment_bias = -1

        # 🧮 Combine with technical bias
        final_action = "HOLD"
        if tech_bias == "BULLISH":
            if sentiment_bias == 1:
                final_action = "LONG"
            elif sentiment_bias == -1:
                final_action = "HOLD"  # conflicting signals
        elif tech_bias == "BEARISH":
            if sentiment_bias == -1:
                final_action = "SHORT"
            elif sentiment_bias == 1:
                final_action = "HOLD"
        elif tech_bias == "NEUTRAL":
            # rely mainly on news
            final_action = "LONG" if sentiment_bias == 1 else "SHORT" if sentiment_bias == -1 else "HOLD"

        if debug:
            print("\n🧠 DEBUG SENTIMENT ANALYSIS")
            print(
                f"📰 Sentiment: {sentiment_label.upper()} (confidence={confidence:.4f})")
            print(f"📈 Technical Bias: {tech_bias} [{timeframe}]")
            print(f"⚙️  Combined Decision: {final_action}")

        return final_action, confidence, sentiment_label, tech_bias, timeframe
