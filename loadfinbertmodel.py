# loadfinbertmodel.py
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def load_finbert():
    """Load FinBERT model and tokenizer from local path"""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # project root
    model_path = os.path.join(base_dir, "model", "FinBERT")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model


# Load them once when the module is imported
tokenizer, model = load_finbert()
