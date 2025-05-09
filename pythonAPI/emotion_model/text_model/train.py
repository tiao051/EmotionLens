from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments
import evaluate
from build import compute_metrics, LABELS

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

if __name__ == "__main__":
    from build import load_data, prepare_datasets, tokenize_datasets
    csv_path = "FinalData.csv"
    save_dir = "./sentiment_distilbert_full_data"
    df = load_data(csv_path)
    train_ds, test_ds = prepare_datasets(df)
    train_ds, test_ds, tokenizer = tokenize_datasets(train_ds, test_ds)
    trainer = train_model(train_ds, test_ds, tokenizer)
    save_model(trainer, save_dir)