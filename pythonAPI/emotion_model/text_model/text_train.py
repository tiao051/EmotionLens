import argparse
from transformers import Trainer, TrainingArguments, EarlyStoppingCallback, TFAutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import tensorflow as tf

from emotion_model.text_model.text_build import load_and_prepare_data

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average="weighted")
    return {"accuracy": acc, "f1": f1}

def train_text_model():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="distilbert-base-uncased")
    parser.add_argument("--learning_rate", type=float, default=1e-5)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--early_stopping_patience", type=int, default=2)
    parser.add_argument("--save_path", type=str, default="/content/drive/MyDrive/distilbert_emotion_model.keras")
    parser.add_argument("--csv_path", type=str, default="/content/drive/MyDrive/text_dataset/Data.csv")
    args, _ = parser.parse_known_args()

    model, tokenizer, train_dataset, test_dataset, label2id, id2label = load_and_prepare_data(args.csv_path, args.model_name)

    training_args = TrainingArguments(
        output_dir="./results",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir="./logs",
        logging_strategy="steps",
        logging_steps=100,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=args.early_stopping_patience)]
    )

    print("🚀 Training...")
    trainer.train()

    print("📦 Converting to TensorFlow & saving to:", args.save_path)
    tf_model = TFAutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        from_pt=True,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )
    tf_model.save(args.save_path, save_format="keras")
    print("✅ Saved:", args.save_path)
