# backend/src/feature_engineering.py
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def build_input_text(row):
    parts = []
    for c in ['job_title','description','requirement','benefit','industry','position_level']:
        if row.get(c):
            parts.append(str(row[c]))
    return ' \n '.join(parts)

def add_features_and_targets(df_combined):
    """
    Reproduce the notebook's feature engineering:
    - Build 'input_text'
    - Build salary_target and salary_target_log1p columns
    """
    df_combined = df_combined.copy()
    df_combined['input_text'] = df_combined.apply(build_input_text, axis=1)
    df_combined['salary_target'] = df_combined['salary_mean_vnd']
    df_combined['salary_target_log1p'] = df_combined['salary_target'].apply(lambda x: np.log1p(x) if pd.notna(x) else None)
    return df_combined

def create_splits(labeled_df, artifact_dir, random_state=42):
    """
    Create train/val/test splits exactly as in the notebook:
    train, temp (30% holdout), val/test = half/half of temp.
    Writes CSVs to artifact_dir paths (train.csv, val.csv, test.csv)
    """
    train, temp = train_test_split(labeled_df, test_size=0.3, random_state=random_state)
    val, test = train_test_split(temp, test_size=0.5, random_state=random_state)
    # Save
    train.to_csv(artifact_dir / 'train.csv', index=False)
    val.to_csv(artifact_dir / 'val.csv', index=False)
    test.to_csv(artifact_dir / 'test.csv', index=False)
    return train, val, test
