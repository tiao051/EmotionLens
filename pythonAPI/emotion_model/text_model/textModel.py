import os
import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import evaluate
import torch
import torch.nn.functional as F

LABELS = ['Giận dữ', 'Buồn bã', 'Trung lập', 'Vui vẻ', 'Phấn khích']

def load_data(csv_path, label_column='sentiment', text_column='text'):
    df = pd.read_csv(csv_path)
    if label_column not in df.columns or text_column not in df.columns:
        raise ValueError(f"Không tìm thấy cột '{text_column}' hoặc '{label_column}' trong file CSV.")
    df = df.dropna(subset=[label_column])
    return df

def prepare_datasets(df, label_column='sentiment', text_column='text', test_size=0.2):
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        df[text_column], df[label_column], test_size=test_size, random_state=42
    )
    train_labels = train_labels.astype(int)
    test_labels = test_labels.astype(int)
    train_ds = Dataset.from_pandas(pd.DataFrame({"text": train_texts, "label": train_labels}))
    test_ds = Dataset.from_pandas(pd.DataFrame({"text": test_texts, "label": test_labels}))
    return train_ds, test_ds

def tokenize_datasets(train_ds, test_ds, model_name="distilbert-base-uncased"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_ds = train_ds.map(lambda x: tokenizer(x['text'], truncation=True, padding="max_length", max_length=128), batched=True)
    test_ds = test_ds.map(lambda x: tokenizer(x['text'], truncation=True, padding="max_length", max_length=128), batched=True)
    return train_ds, test_ds, tokenizer

def compute_metrics(p):
    accuracy = evaluate.load("accuracy")
    f1 = evaluate.load("f1")
    preds = p.predictions.argmax(axis=-1)
    return {
        "accuracy": accuracy.compute(predictions=preds, references=p.label_ids)["accuracy"],
        "f1": f1.compute(predictions=preds, references=p.label_ids, average="macro")["f1"]
    }

def train_model(train_ds, test_ds, tokenizer, model_name="distilbert-base-uncased", num_labels=5, output_dir="./results", epochs=3):
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    args = TrainingArguments(
        output_dir=output_dir,
        eval_accumulation_steps=1,
        num_train_epochs=epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )
    trainer.train()
    return trainer

def save_model(trainer, save_directory):
    trainer.model.save_pretrained(save_directory)
    trainer.tokenizer.save_pretrained(save_directory)

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

if __name__ == "__main__":
    # Example usage:
    # 1. Train and save model
    # csv_path = "FinalData.csv"
    # save_dir = "./sentiment_distilbert_full_data"
    # df = load_data(csv_path)
    # train_ds, test_ds = prepare_datasets(df)
    # train_ds, test_ds, tokenizer = tokenize_datasets(train_ds, test_ds)
    # trainer = train_model(train_ds, test_ds, tokenizer)
    # save_model(trainer, save_dir)

    # 2. Load and predict
    model_directory = "./sentiment_distilbert_full_data"
    model, tokenizer = load_model(model_directory)
    test_text = "happy"
    label, idx = predict_sentiment(test_text, model, tokenizer)
    print(f"Input: {test_text}\nPredicted: {label} (Index: {idx})")