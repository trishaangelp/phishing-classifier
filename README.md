# 🎣 Phishing URL Classifier

A machine learning-powered web app that analyzes URLs and classifies them as **safe** or **phishing**. Paste any URL and get back a risk score, confidence level, threat indicators, and a full breakdown of the 14 features that drove the classification.

🔗 **Live app:** https://phishing-classifier-tau.vercel.app/

---

## Motivation

I built this project at the intersection of my four main areas: **data engineering, AI, full stack development, and cybersecurity.**

The data engineering side covers the training pipeline — ingesting 450,000+ URLs, extracting 14 structural features from raw URL strings, and building a clean dataset the model can learn from. The AI side is the XGBoost classifier with SHAP explainability, turning URL patterns into interpretable predictions. The full stack side is the FastAPI backend and React frontend that make the model usable by anyone. And cybersecurity is the whole reason it exists.

During my internship I worked on phishing-related tasks — analyzing suspicious links and understanding how threat actors craft URLs to deceive users — and that experience directly inspired this project. The Philippines has seen a dramatic rise in phishing incidents. According to the Cybercrime Investigation and Coordinating Center (CICC), cybercrime complaints tripled in 2024, with phishing and online fraud among the top categories. GCash, BDO, and Maya users lost nearly ₱198 million to cybercrime that year alone. Phishing via malicious URLs is now the fastest-growing digital threat in the country. Building something that could detect these links — even imperfectly — felt like a meaningful way to apply everything I was learning across all four areas at once.

---

## What It Does

- Paste any URL into the input field
- The app extracts 14 structural features from the URL (length, subdomains, suspicious TLDs, special characters, brand keywords, etc.)
- An XGBoost model trained on 450,000+ labeled URLs predicts whether it's phishing or legitimate
- Returns a **risk score (0–100)**, prediction label, confidence percentage, and human-readable threat indicators powered by SHAP explainability
- Expandable feature breakdown table shows every signal the model used

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| ML Model | XGBoost | Gradient boosting classifier |
| Explainability | SHAP | Explains which features drove each prediction |
| Feature Extraction | Python + tldextract | Parses URL structure into 14 numeric features |
| Backend | FastAPI | REST API with auto-generated docs at `/docs` |
| Frontend | React + Vite | UI with dark terminal aesthetic |
| Model Training | pandas + scikit-learn | Data pipeline and evaluation |
| API Hosting | Render | Free tier Python web service |
| Frontend Hosting | Vercel | Static site deployment |

---

## Project Structure

```
phishing-classifier/
├── README.md
├── .gitignore
│
├── model/                       # ML pipeline
│   ├── requirements.txt
│   ├── features.py              # URL feature extractor (14 indicators)
│   ├── train.py                 # loads dataset, trains XGBoost, saves model
│   └── evaluate.py              # confusion matrix + sample URL predictions
│
├── api/                         # FastAPI backend
│   ├── requirements.txt
│   ├── .python-version          # pins Python 3.11 for deployment
│   ├── main.py                  # app entry point, CORS, routes
│   ├── classifier.py            # loads model, runs prediction + SHAP
│   ├── schemas.py               # Pydantic request/response models
│   ├── phishing_model.pkl       # trained XGBoost model
│   ├── feature_columns.pkl      # feature column order from training
│   └── Dockerfile
│
└── client/                      # React frontend
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── api/
        │   └── axios.js
        └── components/
            ├── URLInput.jsx
            ├── ResultCard.jsx
            └── FeatureBreakdown.jsx
```

---

## How I Built It

### 1. Feature Engineering
The core of the classifier is `model/features.py` — a URL parser that extracts 14 structural signals from a raw URL string without ever visiting the page. Features include URL length, number of subdomains, presence of IP addresses, suspicious TLDs (`.xyz`, `.tk`, `.ml`), brand keywords in the domain, special characters, and more. These are the same signals a security analyst would look for when reviewing a suspicious link.

### 2. Model Training
I trained an XGBoost gradient boosting classifier on the **Mendeley URL Dataset** — 450,176 URLs sourced from PhishTank (real phishing submissions) and Majestic Million (verified legitimate domains). After cleaning and feature extraction the model achieved **95.3% accuracy** and a **0.97 ROC-AUC** on the held-out test set. SHAP (SHapley Additive exPlanations) is used at inference time to generate human-readable reasons for each prediction.

### 3. REST API
The trained model is served via FastAPI. The `/classify` endpoint accepts a URL, runs it through the same feature extraction pipeline, loads the prediction from the model, and returns a structured JSON response with the risk score, label, confidence, SHAP-derived reasons, and raw feature values. FastAPI auto-generates interactive API documentation at `/docs`.

### 4. Frontend
The React frontend was built with a dark terminal aesthetic — IBM Plex Mono, green-on-black, scan line effect — intentionally designed to feel like a security tool rather than a generic web app. It features a command-line style URL input, an animated risk score circle that color-codes from green to red, a threat indicators list, and a collapsible feature breakdown table.

---

## Model Performance

| Metric | Score |
|---|---|
| Accuracy | 95.3% |
| Precision | 97.2% |
| Recall | 82.0% |
| F1 Score | 88.9% |
| ROC-AUC | 97.1% |

Tested on 90,036 held-out samples from the Mendeley URL Dataset.

---

## API Reference

### `POST /classify`

**Request:**
```json
{ "url": "http://gcash-reward-claim.xyz/verify" }
```

**Response:**
```json
{
  "url": "http://gcash-reward-claim.xyz/verify",
  "prediction": "phishing",
  "is_phishing": true,
  "confidence": 0.9998,
  "risk_score": 100,
  "top_reasons": [
    "Suspicious top-level domain (.xyz, .tk, .ml, etc.)",
    "Multiple subdomains",
    "Unusually long URL"
  ],
  "features": { ... }
}
```

### `GET /health`
Returns API status and whether the model is loaded.

### `GET /docs`
Auto-generated interactive API documentation (FastAPI Swagger UI).

---

## Limitations

- **Dataset is not Philippines-specific.** The model was trained on a global dataset (Mendeley URL Dataset sourced from PhishTank and Majestic Million). Philippine phishing campaigns often impersonate local brands like GCash, BDO, Maya, SSS, and PhilPost — and while the model catches many of these based on URL structure, there may be inaccuracies on PH-specific links that don't match global phishing patterns. A PH-specific dataset would significantly improve local accuracy.
- **URL-only analysis.** The model only looks at the URL string — it does not visit the page, check certificates, or analyze page content. A sophisticated phishing site hosted on a legitimate-looking domain may slip through.
- **Static model.** The model is trained once on a fixed dataset. It does not automatically learn new phishing patterns over time without retraining.
- **Free tier cold starts.** The API is hosted on Render's free tier, which spins down after inactivity. The first request after idle time may take 30–60 seconds to respond.

---

## Dataset

**Mendeley URL Dataset** — 450,176 URLs  
- 345,738 legitimate (sourced from Majestic Million)  
- 104,438 phishing (sourced from PhishTank)  
- Available at: https://data.mendeley.com/datasets/vfszbj9b36/1

---

## Features Roadmap

- [x] URL feature extraction (14 indicators)
- [x] XGBoost classifier, 95.3% accuracy
- [x] SHAP explainability
- [x] FastAPI REST endpoint with auto-docs
- [x] React UI with risk score + breakdown
- [x] Deployed on Render + Vercel
- [ ] Philippines-specific dataset
- [ ] Bulk CSV upload
- [ ] Browser extension
- [ ] VirusTotal API cross-validation
- [ ] Retraining pipeline