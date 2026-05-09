import os
import sys
import joblib
import numpy as np
import pandas as pd
import shap

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "model"))
from features import extract_features

MODEL_PATH     = os.path.join(os.path.dirname(__file__), "phishing_model.pkl")
FEAT_COLS_PATH = os.path.join(os.path.dirname(__file__), "feature_columns.pkl")

FEATURE_LABELS = {
    "url_suspicious_tld":     "Suspicious top-level domain (.xyz, .tk, .ml, etc.)",
    "url_has_at":             "@ symbol in URL (classic phishing trick)",
    "url_has_ip":             "IP address used instead of domain name",
    "url_has_double_slash":   "Double slash redirect trick in path",
    "url_has_brand_keyword":  "Brand name found in suspicious domain",
    "url_num_hyphens":        "Hyphens in domain name",
    "url_num_subdomains":     "Multiple subdomains",
    "url_num_dots":           "Excessive dots in URL",
    "url_url_length":         "Unusually long URL",
    "url_path_depth":         "Deep URL path structure",
    "url_num_special_chars":  "Excessive special characters",
    "url_has_query":          "Query string parameters present",
    "url_is_shortener":       "URL shortener used",
    "url_domain_length":      "Unusually long domain name",
}

_model = None
_explainer = None
_feature_columns = None


def load_model():
    global _model, _explainer, _feature_columns

    for path, name in [(MODEL_PATH, "model"), (FEAT_COLS_PATH, "feature_columns")]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{name} not found at {path}. "
                "Run model/train.py and copy both .pkl files to api/."
            )

    _model = joblib.load(MODEL_PATH)
    _feature_columns = joblib.load(FEAT_COLS_PATH)
    _explainer = shap.TreeExplainer(_model)
    print(f"Model loaded: {len(_feature_columns)} features")


def build_runtime_features(url: str) -> pd.DataFrame:
    """
    Extract URL features and align to the exact column order
    the model was trained on.
    """
    url_feats = extract_features(url)

    # Prefix with url_ to match training column names
    row = {f"url_{k}": v for k, v in url_feats.items()}

    # Align to exact column order from training
    df = pd.DataFrame([row])
    df = df.reindex(columns=_feature_columns, fill_value=0)
    return df, url_feats


def get_top_reasons(
    feature_row: pd.DataFrame,
    shap_values: np.ndarray,
    is_phishing: bool,
) -> list[str]:
    reasons = []

    # Handle different SHAP output shapes
    if isinstance(shap_values, list) and len(shap_values) == 2:
        vals = shap_values[1][0]
    elif hasattr(shap_values, 'ndim') and shap_values.ndim == 3:
        vals = shap_values[0, :, 1]
    elif hasattr(shap_values, 'ndim') and shap_values.ndim == 2:
        vals = shap_values[0]
    else:
        vals = np.array(shap_values).flatten()

    feat_shap = sorted(
        zip(_feature_columns, vals, feature_row.iloc[0].values),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    seen = set()
    for feat_name, shap_val, feat_val in feat_shap:
        if len(reasons) >= 3:
            break
        pushes_phishing = shap_val > 0
        if pushes_phishing != is_phishing:
            continue
        label = FEATURE_LABELS.get(feat_name)
        if not label or label in seen:
            continue
        if feat_val:
            reasons.append(label)
            seen.add(label)

    if not reasons:
        reasons.append(
            "URL structure matches known phishing patterns"
            if is_phishing else "URL structure appears legitimate"
        )
    return reasons


def classify(url: str) -> dict:
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    feature_row, url_feats = build_runtime_features(url)

    prob_phishing = float(_model.predict_proba(feature_row)[0][1])
    is_phishing   = prob_phishing >= 0.5
    confidence    = prob_phishing if is_phishing else (1 - prob_phishing)
    risk_score    = round(prob_phishing * 100)

    shap_values  = _explainer.shap_values(feature_row)
    top_reasons  = get_top_reasons(
        feature_row, np.array(shap_values), is_phishing
    )

    bool_fields = {
        "has_ip", "has_at", "has_https", "is_shortener",
        "suspicious_tld", "has_brand_keyword", "has_query", "has_double_slash",
    }
    feature_detail = {
        k: bool(v) if k in bool_fields else int(v)
        for k, v in url_feats.items()
    }

    return {
        "url":         url,
        "prediction":  "phishing" if is_phishing else "legitimate",
        "is_phishing": is_phishing,
        "confidence":  round(confidence, 4),
        "risk_score":  risk_score,
        "top_reasons": top_reasons,
        "features":    feature_detail,
    }