# backend/src/phobert_finetune_utils.py
import os
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
import numpy as np
import pandas as pd
from transformers import PhobertTokenizer, RobertaModel, get_scheduler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tqdm import tqdm

# =============================
# Dataset class
# =============================
class JobDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=256, with_labels=True):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.with_labels = with_labels

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text = str(self.df.loc[idx, "input_text"])
        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        if self.with_labels:
            label = self.df.loc[idx, "salary_target_log1p"]
            item["labels"] = torch.tensor(label, dtype=torch.float32)
        return item

# =============================
# Model definition
# =============================
class PhoBERTRegressor(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.roberta = base_model
        hidden_size = self.roberta.config.hidden_size
        self.dropout = nn.Dropout(0.2)
        self.regressor = nn.Linear(hidden_size, 1)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0]  # CLS token
        pooled = self.dropout(pooled)
        preds = self.regressor(pooled).squeeze(-1)

        loss = None
        if labels is not None:
            loss_fn = nn.MSELoss()
            loss = loss_fn(preds, labels)
        return {"loss": loss, "preds": preds}

# =============================
# Training function
# =============================
def train_phobert(
    artifact_dir,
    model_dir,
    tokenizer_dir=None,
    device=None,
    batch_size=8,
    epochs=3,
    lr=2e-5,
    max_len=256
):
    """
    Recreates the training loop from the notebook. Saves best model to artifact_dir/'phobert_best.pt'.
    artifact_dir should be a pathlib.Path or string path where train/val/test CSVs exist.
    model_dir: path to base PhoBERT model (local huggingface-format)
    tokenizer_dir: optional tokenizer path (if None we use model_dir)
    """
    artifact_dir = Path(artifact_dir)
    tokenizer_dir = tokenizer_dir or model_dir
    DEVICE = device or ("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = PhobertTokenizer.from_pretrained(tokenizer_dir)
    base_model = RobertaModel.from_pretrained(model_dir)

    train = pd.read_csv(artifact_dir / "train.csv")
    val = pd.read_csv(artifact_dir / "val.csv")
    test = pd.read_csv(artifact_dir / "test.csv")

    train_ds = JobDataset(train, tokenizer, max_len=max_len)
    val_ds = JobDataset(val, tokenizer, max_len=max_len)
    test_ds = JobDataset(test, tokenizer, max_len=max_len)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    model = PhoBERTRegressor(base_model).to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=lr)
    total_steps = len(train_loader) * epochs
    scheduler = get_scheduler(
        "linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=total_steps
    )

    best_rmse = float("inf")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            out = model(input_ids, attention_mask, labels)
            loss = out["loss"]
            loss.backward()
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()

        rmse, mae = evaluate(model, val_loader, device=DEVICE)
        print(f"Epoch {epoch+1}: Train Loss={total_loss/len(train_loader):.4f} | Val RMSE={rmse:.4f}, MAE={mae:.4f}")

        if rmse < best_rmse:
            best_rmse = rmse
            torch.save(model.state_dict(), artifact_dir / "phobert_best.pt")
            print("✅ Saved best model.")

    # after training, load best and test
    model.load_state_dict(torch.load(artifact_dir / "phobert_best.pt"))
    model.to(DEVICE)
    model.eval()

    test_preds, test_labels = [], []
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Testing"):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            y = batch["labels"].to(DEVICE)
            out = model(input_ids, attention_mask)
            test_preds.append(out["preds"].detach().cpu().numpy())
            test_labels.append(y.cpu().numpy())

    test_preds = np.concatenate(test_preds)
    test_labels = np.concatenate(test_labels)

    rmse = np.sqrt(mean_squared_error(test_labels, test_preds))
    mae = mean_absolute_error(test_labels, test_preds)
    print(f"\n📊 Final Test RMSE: {rmse:.4f} | MAE: {mae:.4f}")

    # Optional: convert predictions back to VND and save
    test_df = test.copy()
    test_df["predicted_salary_log1p"] = test_preds
    test_df["predicted_salary_vnd"] = np.expm1(test_df["predicted_salary_log1p"])
    test_df.to_csv(artifact_dir / "test_with_predictions.csv", index=False)
    print("Saved predictions to:", artifact_dir / "test_with_predictions.csv")

    return artifact_dir / "phobert_best.pt"
