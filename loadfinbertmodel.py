from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


def load_finbert():
    model_path = r"G:\AI Projects\Sarva\model\FinBERT"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return model, tokenizer
