# loadfinbertmodel.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification


def load_finbert():
    """Load FinBERT model and tokenizer from local path"""
    model_path = r"G:\AI Projects\Sarva\model\GPTNeo"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model


# Load them once when the module is imported
tokenizer, model = load_finbert()
