import argparse
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from newscollector import NewsCollector
from calculations import calculate_trade
from urls import URLS


class DecisionAgent:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def analyze(self, text):
        inputs = self.tokenizer(text, truncation=True,
                                max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence, predicted_class = torch.max(probs, dim=1)
        label = "LONG" if predicted_class.item() == 1 else "SHORT"
        return label, confidence.item()


class MainAgent:
    def __init__(self, coin_name, portfolio_value):
        self.coin_name = coin_name
        self.portfolio_value = portfolio_value
        self.news_collector = NewsCollector(debug=True)

        print("🔍 Loading BERT model...")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased", num_labels=2)
        self.decision_agent = DecisionAgent(self.model, self.tokenizer)

    def run(self):
        urls = URLS.get(self.coin_name.upper(), [])
        if not urls:
            print(f"⚠️ No URLs found for {self.coin_name}")
            return

        print(f"🔎 Collecting {len(urls)} URLs for {self.coin_name}...\n")
        results = []

        for url in urls:
            text = self.news_collector.extract_text(url)
            if not text:
                continue

            action, confidence = self.decision_agent.analyze(text)
            trade = calculate_trade(
                action, confidence, self.portfolio_value, self.coin_name)

            results.append({
                "url": url,
                "decision": {
                    "action": action,
                    "confidence": confidence,
                    **trade
                }
            })

        print("\n✅ Final Results:")
        for r in results:
            print(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--coin", type=str, default="BNB")
    parser.add_argument("--portfolio", type=float, default=2000)
    args = parser.parse_args()

    agent = MainAgent(coin_name=args.coin, portfolio_value=args.portfolio)
    agent.run()
