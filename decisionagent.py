import torch
import numpy as np


class DecisionAgent:
    def __init__(self, model, tokenizer, chart_agent=None, debug=False):
        self.model = model
        self.tokenizer = tokenizer
        self.chart_agent = chart_agent
        self.debug = debug

    def analyze(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(
            outputs.logits, dim=-1).detach().numpy()[0]
        labels = ["negative", "neutral", "positive"]
        sentiment = labels[np.argmax(probs)]
        confidence = float(np.max(probs))

        # Map sentiment to action
        sentiment_action = "LONG" if sentiment == "positive" else "SHORT" if sentiment == "negative" else "HOLD"

        # Add chart analysis
        tech_bias, timeframe = self.chart_agent.analyze_chart(
        ) if self.chart_agent else ("NEUTRAL", "N/A")

        # Combine both signals
        final_action = self.combine_signals(sentiment_action, tech_bias)

        if self.debug:
            print(
                f"📰 News sentiment: {sentiment.upper()} ({confidence:.3f}) → {sentiment_action}")
            print(f"📊 Technical bias ({timeframe}): {tech_bias}")
            print(f"🎯 Combined action: {final_action}")

        return final_action, confidence, sentiment, tech_bias, timeframe

    def combine_signals(self, sentiment_action, tech_bias):
        if tech_bias == "NEUTRAL":
            return sentiment_action
        if sentiment_action == "HOLD":
            return "HOLD"
        if sentiment_action == "LONG" and tech_bias == "BULLISH":
            return "LONG"
        if sentiment_action == "SHORT" and tech_bias == "BEARISH":
            return "SHORT"
        return "HOLD"
