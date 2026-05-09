import os
import sys
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
)
from features import extract_features

# --- Config ---
DATASET_PATH   = os.path.join(os.path.dirname(__file__), "phishing.csv")
MODEL_PATH     = os.path.join(os.path.dirname(__file__), "phishing_model.pkl")
FEAT_COLS_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")

URL_COL   = "url"
LABEL_COL = "type"   # 0 = phishing, 1 = legitimate

# Pre-computed numeric columns from the PhiUSIIL dataset.
# Excludes: FILENAME, URL, Domain, TLD, Title (non-numeric / free text)
PRECOMPUTED_COLS = []


def load_dataset(path: str) -> pd.DataFrame:
    print(f"Loading dataset from {path}...")
    df = pd.read_csv(path)
    print(f"  Rows  : {len(df):,}")
    print(f"  Cols  : {len(df.columns)}")

    missing = [c for c in [URL_COL, LABEL_COL] + PRECOMPUTED_COLS if c not in df.columns]
    if missing:
        print(f"\nERROR: Missing expected columns: {missing}")
        print("Make sure you're using PhiUSIIL_Phishing_URL_Dataset.csv")
        sys.exit(1)

    df = df.dropna(subset=[URL_COL, LABEL_COL])
    df[URL_COL]   = df[URL_COL].astype(str)
    df[LABEL_COL] = (df[LABEL_COL] == "phishing").astype(int)

    print(f"  Phishing   : {df[LABEL_COL].sum():,} ({df[LABEL_COL].mean():.1%})")
    print(f"  Legitimate : {(df[LABEL_COL] == 0).sum():,}")
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine two feature sets:
      1. Pre-computed columns from the dataset (page-level signals)
      2. URL-extracted features from features.py (URL structure signals)
    Duplicate columns (e.g. both have URL length) are kept from the
    pre-computed set and prefixed with 'url_' in the extracted set.
    """
    print("\nBuilding feature matrix...")

    # --- Pre-computed features ---
    precomp = df[PRECOMPUTED_COLS].copy()
    # Fill any NaNs with column median (rare but safe)
    precomp = precomp.fillna(precomp.median())
    print(f"  Pre-computed features : {len(PRECOMPUTED_COLS)}")

    # --- URL-extracted features ---
    print("  Extracting URL features (this may take a minute for 235k rows)...")
    url_feats = df[URL_COL].apply(extract_features).apply(pd.Series)
    # Prefix to avoid collision with pre-computed columns
    url_feats.columns = [f"url_{c}" for c in url_feats.columns]
    print(f"  URL-extracted features : {len(url_feats.columns)}")

    # --- Combine ---
    combined = pd.concat(
    [precomp.reset_index(drop=True), url_feats.reset_index(drop=True)],
    axis=1,
    )
    # Drop HTTPS features — misleading in this dataset (all legit URLs happen to be HTTPS)
    combined = combined.drop(columns=["url_has_https"], errors="ignore")
    print(f"  Total features         : {len(combined.columns)}")
    return combined


def train(X_train: pd.DataFrame, y_train: np.ndarray) -> XGBClassifier:
    print("\nTraining XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=400,
        max_depth=7,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, verbose=False)
    return model


def evaluate(model: XGBClassifier, X_test: pd.DataFrame, y_test: np.ndarray):
    print("\n--- Evaluation Results ---")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print(f"  Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision : {precision_score(y_test, y_pred):.4f}")
    print(f"  Recall    : {recall_score(y_test, y_pred):.4f}")
    print(f"  F1 Score  : {f1_score(y_test, y_pred):.4f}")
    print(f"  ROC-AUC   : {roc_auc_score(y_test, y_prob):.4f}")
    print()
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))

    # Top 10 most important features
    feat_imp = sorted(
        zip(X_test.columns, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    print("Top 10 most important features:")
    for name, score in feat_imp[:10]:
        print(f"  {name:<40} {score:.4f}")


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Rename PhiUSIIL_Phishing_URL_Dataset.csv to phishing.csv")
        print("and place it in the model/ folder.")
        sys.exit(1)

    df = load_dataset(DATASET_PATH)
    X  = build_features(df)
    y  = df[LABEL_COL].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain : {len(X_train):,} samples")
    print(f"Test  : {len(X_test):,} samples")

    model = train(X_train, y_train)
    evaluate(model, X_test, y_test)

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved       → {MODEL_PATH}")

    # Save feature column order — the API needs this to align columns at runtime
    joblib.dump(list(X.columns), FEAT_COLS_PATH)
    print(f"Feature cols saved → {FEAT_COLS_PATH}")

    print("\nNext steps:")
    print("  cp model/phishing_model.pkl api/phishing_model.pkl")
    print("  cp model/feature_columns.pkl api/feature_columns.pkl")


if __name__ == "__main__":
    main()
