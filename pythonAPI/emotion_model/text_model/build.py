import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer

LABELS = ['Giận dữ', 'Buồn bã', 'Trung lập', 'Vui vẻ', 'Phấn khích']

def load_data(csv_path, label_column='sentiment', text_column='text'):
    df = pd.read_csv(csv_path)
    if label_column not in df.columns or text_column not in df.columns:
        raise ValueError(f"Không tìm thấy cột '{text_column}' hoặc '{label_column}' trong file CSV.")
    df = df.dropna(subset=[label_column])
    return df

def prepare_datasets(df, label_column='sentiment', text_column='text', test_size=0.2):
    from sklearn.model_selection import train_test_split
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