import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, accuracy_score,
)
from train import load_dataset, build_features, URL_COL, LABEL_COL, DATASET_PATH, PRECOMPUTED_COLS
from sklearn.model_selection import train_test_split

MODEL_PATH     = os.path.join(os.path.dirname(__file__), "phishing_model.pkl")
FEAT_COLS_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")


def print_confusion_matrix(cm):
    tn, fp, fn, tp = cm.ravel()
    print("\nConfusion Matrix:")
    print(f"                  Predicted")
    print(f"                  Legit    Phishing")
    print(f"Actual  Legit   [ {tn:>6}    {fp:>6} ]")
    print(f"        Phishing[ {fn:>6}    {tp:>6} ]")
    print(f"\n  True Negatives  (correct legit)              : {tn:,}")
    print(f"  False Positives (legit flagged as phishing)  : {fp:,}")
    print(f"  False Negatives (phishing missed)            : {fn:,}")
    print(f"  True Positives  (phishing caught)            : {tp:,}")
    print(f"\n  False Positive Rate : {fp / (fp + tn):.2%}")
    print(f"  False Negative Rate : {fn / (fn + tp):.2%}")


def build_single_url_row(url: str, feature_columns: list) -> pd.DataFrame:
    """
    Build a single aligned feature row for a URL at evaluation time.
    Mirrors exactly what classifier.py does at runtime.
    """
    from features import extract_features

    url_feats = extract_features(url)

    # Start with zeros for all precomputed cols
    row = {col: 0 for col in PRECOMPUTED_COLS}

    # Override every precomputed col we can derive from the URL string
    row["URLLength"]                    = len(url)
    row["DomainLength"]                 = len(url.split("/")[2]) if "//" in url else 0
    row["IsDomainIP"]                   = int(url_feats["has_ip"])
    row["TLDLength"]                    = len(url.split(".")[-1].split("/")[0])
    row["NoOfSubDomain"]                = url_feats["num_subdomains"]
    row["HasObfuscation"]               = int(url_feats["has_at"] or url_feats["has_double_slash"])
    row["NoOfObfuscatedChar"]           = int(url_feats["has_at"]) + int(url_feats["has_double_slash"])
    row["NoOfLettersInURL"]             = sum(c.isalpha() for c in url)
    row["LetterRatioInURL"]             = round(sum(c.isalpha() for c in url) / max(len(url), 1), 4)
    row["NoOfDegitsInURL"]              = sum(c.isdigit() for c in url)
    row["DegitRatioInURL"]              = round(sum(c.isdigit() for c in url) / max(len(url), 1), 4)
    row["NoOfEqualsInURL"]              = url.count("=")
    row["NoOfQMarkInURL"]               = url.count("?")
    row["NoOfAmpersandInURL"]           = url.count("&")
    row["NoOfOtherSpecialCharsInURL"]   = sum(url.count(c) for c in ["%", "@", "!", "$"])
    row["SpacialCharRatioInURL"]        = round(
        sum(url.count(c) for c in ["%", "@", "!", "$", "=", "&", "?"]) / max(len(url), 1), 4
    )
    row["IsHTTPS"]                      = int(url_feats["has_https"])  # ← critical

    # Add url_ prefixed features
    for k, v in url_feats.items():
        row[f"url_{k}"] = v

    return pd.DataFrame([row]).reindex(columns=feature_columns, fill_value=0)


def test_sample_urls(model, feature_columns):
    samples = [
        ("https://www.google.com",                         "legitimate"),
        ("https://www.paypal.com/signin",                  "legitimate"),
        ("http://paypa1-secure.xyz/login",                 "phishing"),
        ("http://192.168.1.1/update-account",              "phishing"),
        ("http://bit.ly/3xKj92",                           "shortener (uncertain)"),
        ("https://amazon.com/orders",                      "legitimate"),
        ("http://amazon-account-verify.tk/login?user=you", "phishing"),
        ("https://www.bdo.com.ph/personal",                "legitimate"),
        ("http://gcash-reward-claim.xyz/verify",           "phishing"),
        ("http://sss.gov.ph.verify-account.tk/login",      "phishing"),
    ]

    print("\nSample URL predictions:")
    print(f"{'URL':<52} {'Expected':<22} {'Predicted':<12} {'Confidence'}")
    print("-" * 105)

    for url, expected in samples:
        df_row = build_single_url_row(url, feature_columns)
        prob   = model.predict_proba(df_row)[0][1]
        pred   = "phishing" if prob >= 0.5 else "legitimate"
        conf   = f"{max(prob, 1 - prob):.1%}"
        match  = "✓" if (pred == expected or expected == "shortener (uncertain)") else "✗"
        print(f"{url[:50]:<52} {expected:<22} {pred:<12} {conf} {match}")


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        print("Run train.py first.")
        sys.exit(1)

    if not os.path.exists(FEAT_COLS_PATH):
        print(f"ERROR: feature_columns.pkl not found at {FEAT_COLS_PATH}")
        print("Run train.py first.")
        sys.exit(1)

    model           = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEAT_COLS_PATH)
    print(f"Model loaded — {len(feature_columns)} features")

    if not os.path.exists(DATASET_PATH):
        print("Dataset not found — running sample URL predictions only.")
        test_sample_urls(model, feature_columns)
        return

    df = load_dataset(DATASET_PATH)
    X  = build_features(df)
    y  = df[LABEL_COL].values

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print(f"\nTest set size : {len(X_test):,} samples")
    print(f"Accuracy      : {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC       : {roc_auc_score(y_test, y_prob):.4f}")
    print()
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))

    cm = confusion_matrix(y_test, y_pred)
    print_confusion_matrix(cm)
    test_sample_urls(model, feature_columns)


if __name__ == "__main__":
    main()