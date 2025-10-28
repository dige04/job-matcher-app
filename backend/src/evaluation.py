# backend/src/evaluation.py
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tqdm import tqdm

def evaluate(model, val_loader, device="cpu"):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Validating", leave=False):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            y = batch["labels"].to(device)
            out = model(input_ids, attention_mask)
            preds.append(out["preds"].detach().cpu().numpy())
            labels.append(y.cpu().numpy())
    preds = np.concatenate(preds)
    labels = np.concatenate(labels)
    rmse = np.sqrt(mean_squared_error(labels, preds))
    mae = mean_absolute_error(labels, preds)
    return rmse, mae
