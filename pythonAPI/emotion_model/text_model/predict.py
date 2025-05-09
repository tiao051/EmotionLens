import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from build import LABELS

def load_model(model_directory):
    model = AutoModelForSequenceClassification.from_pretrained(model_directory)
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    return model, tokenizer

def predict_sentiment(text, model, tokenizer, labels=LABELS):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        pred_index = torch.argmax(probs, dim=1).item()
        predicted_label = labels[pred_index]
    return predicted_label, pred_index