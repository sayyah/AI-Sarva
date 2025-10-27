from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os


def load_finbert(local_path=r"G:\AI Projects\Sarva\model\FinBERT"):
    try:
        if os.path.exists(local_path):
            tokenizer = AutoTokenizer.from_pretrained(local_path)
            model = AutoModelForSequenceClassification.from_pretrained(
                local_path)
            print("✅ Loaded FinBERT from local path.")
        else:
            print("⚠️ Local path not found. Loading from Hugging Face.")
            tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            model = AutoModelForSequenceClassification.from_pretrained(
                "ProsusAI/finbert")
        return model, tokenizer
    except Exception as e:
        raise ValueError(f"Failed to load FinBERT: {e}")
