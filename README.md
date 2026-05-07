# 🎣 Phishing URL Classifier

A machine learning-powered web app that classifies URLs as **safe** or **phishing**. Paste any URL and get back a risk score, threat label, confidence level, and a breakdown of which features triggered the classification.

**Stack:** Python · XGBoost · FastAPI · React · Docker

---

## Project Structure

```
phishing-classifier/
├── README.md
├── .gitignore
├── docker-compose.yml           # runs api + (optional) frontend together
│
├── model/                       # ML pipeline — run this first
│   ├── requirements.txt
│   ├── features.py              # URL feature extractor (12 indicators)
│   ├── train.py                 # loads dataset, trains XGBoost, saves model
│   ├── evaluate.py              # prints metrics + confusion matrix
│   └── phishing_model.pkl       # saved model (generated after training)
│
├── api/                         # FastAPI backend
│   ├── requirements.txt
│   ├── main.py                  # app entry point, routes
│   ├── classifier.py            # loads model, runs prediction + SHAP
│   ├── schemas.py               # Pydantic request/response models
│   └── Dockerfile
│
└── client/                      # React frontend
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── Dockerfile
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

## Prerequisites

- [Python](https://python.org) 3.10 or higher — check with `python --version`
- [Node.js](https://nodejs.org) v18 or higher — check with `node -v`
- [Git](https://git-scm.com) — check with `git --version`
- [Docker](https://docker.com) (optional, for containerized run)

---

## Dataset

This project uses the **PhiUSIIL Phishing URL Dataset** (235,795 URLs, 56 features).

1. Download from: https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
2. Rename the file to `phishing.csv`
3. Place it at `model/phishing.csv`

The dataset has a `URL` column and a `label` column (1 = phishing, 0 = legitimate) plus 50 pre-computed features covering URL structure, page content, and domain properties. `train.py` uses all of them combined with our own URL-extracted features for maximum accuracy.

---

## How to Build This Step by Step

Each milestone has its own commit so your Git history shows real progress.

---

### Step 1 — Create the repo on GitHub first

1. Go to [github.com](https://github.com) → New repository
2. Name it `phishing-classifier`
3. Do NOT initialize with README or .gitignore
4. Click Create repository

---

### Step 2 — Set up local project + first commit

Unzip the project files, open a terminal inside `phishing-classifier/`, then:

Create `.gitignore` in the root:

```
__pycache__/
*.pyc
*.pkl
*.egg-info/
.env
*/.env
node_modules/
*/node_modules/
client/dist/
.DS_Store
*.log
model/phishing.csv
venv/
.venv/
```

> Note: `*.pkl` is in .gitignore because model files can be large. `phishing.csv` is excluded because datasets shouldn't be committed — document where to get it in the README instead.

Initialize and push:

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/phishing-classifier.git
git branch -M main
git add README.md .gitignore docker-compose.yml
git commit -m "init: project scaffold, README, and docker-compose"
git push -u origin main
```

---

### Step 3 — Build the feature extractor

This is the core of the ML pipeline. The feature extractor turns a raw URL string into a numerical vector the model can learn from.

Files to add: `model/features.py` and `model/requirements.txt`

Install dependencies:

```bash
cd model
pip install -r requirements.txt
```

Test the extractor manually in Python:

```python
from features import extract_features
print(extract_features("http://paypa1-secure.xyz/login"))
```

You should see a dictionary of 15+ numerical features.

Commit:

```bash
cd ..
git add model/features.py model/requirements.txt
git commit -m "feat(model): URL feature extractor with 15 phishing indicators"
git push
```

---

### Step 4 — Train the model

Files to add: `model/train.py` and `model/evaluate.py`

Make sure your dataset is at `model/phishing.csv`, then:

```bash
cd model
python train.py
```

This will:
- Load and clean the dataset
- Extract features from all URLs
- Train an XGBoost classifier
- Save the model to `model/phishing_model.pkl`
- Print accuracy, precision, recall, F1, and ROC-AUC

Expected output: ~95–97% accuracy. Then run evaluation:

```bash
python evaluate.py
```

This prints a full confusion matrix and per-class metrics.

Commit:

```bash
cd ..
git add model/train.py model/evaluate.py
git commit -m "feat(model): XGBoost training pipeline on PhiUSIIL dataset, ~97% accuracy"
git push
```

> Do NOT commit `phishing_model.pkl`, `feature_columns.pkl`, or `phishing.csv` — they are gitignored. In a real deployment you'd store model files in S3 or a model registry.

---

### Step 5 — Build the FastAPI backend

Files to add: `api/main.py`, `api/classifier.py`, `api/schemas.py`, `api/requirements.txt`, `api/Dockerfile`

Copy the trained model files into the api folder:

```bash
cp model/phishing_model.pkl api/phishing_model.pkl
cp model/feature_columns.pkl api/feature_columns.pkl
```

Install and run:

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test it at `http://localhost:8000/docs` — FastAPI auto-generates interactive API docs. Try the `/classify` endpoint with a test URL.

Commit:

```bash
cd ..
git add api/main.py api/classifier.py api/schemas.py api/requirements.txt api/Dockerfile
git commit -m "feat(api): FastAPI classify endpoint with SHAP feature explanations"
git push
```

---

### Step 6 — Build the React frontend

Files to add: everything in `client/`

```bash
cd client
npm install
```

Create `client/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Run it:

```bash
npm run dev
```

Open `http://localhost:5173` — you should see the classifier UI. Paste a URL and test it end to end.

Commit:

```bash
cd ..
git add client/
git commit -m "feat(client): URL input, risk score card, feature breakdown UI"
git push
```

---

### Step 7 — Docker + final test

Make sure Docker is running, then from the project root:

```bash
docker-compose up --build
```

This starts both the API (port 8000) and frontend (port 5173) together. Test the full stack one more time.

Commit:

```bash
git add api/Dockerfile client/Dockerfile docker-compose.yml
git commit -m "chore: dockerize api and client, docker-compose for local dev"
git push
```

---

### Step 8 — Deploy (optional but recommended)

#### API → Render
1. Push to GitHub (done)
2. Go to Render → New Web Service → connect your repo
3. Set root directory to `api`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy

#### Frontend → Vercel
1. Go to Vercel → New Project → import your repo
2. Set root directory to `client`
3. Set environment variable: `VITE_API_URL` = your Render API URL
4. Deploy

Once deployed, update `client/.env` to point to the live API and redeploy.

Final commit:

```bash
git add .
git commit -m "chore: final check, deployed to Render + Vercel"
git push
```

---

## Daily Workflow

```bash
# terminal 1 — run api
cd api && uvicorn main:app --reload --port 8000

# terminal 2 — run frontend
cd client && npm run dev

# or run both with docker
docker-compose up
```

---

## API Reference

### `POST /classify`

Classifies a URL as phishing or legitimate.

**Request:**
```json
{ "url": "http://paypa1-secure.xyz/login" }
```

**Response:**
```json
{
  "url": "http://paypa1-secure.xyz/login",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_score": 94,
  "is_phishing": true,
  "top_reasons": [
    "Suspicious TLD (.xyz)",
    "High brand similarity score to known domain",
    "No HTTPS"
  ],
  "features": {
    "url_length": 34,
    "num_dots": 2,
    "has_https": false,
    "suspicious_tld": true,
    ...
  }
}
```

### `GET /health`
Returns API status.

### `GET /docs`
Auto-generated interactive API documentation (FastAPI Swagger UI).

---

## Key Concepts to Know

### Why XGBoost?
XGBoost (Extreme Gradient Boosting) is a tree-based ensemble model. It's fast to train, handles tabular feature data extremely well, and gives you feature importance scores out of the box — which is why it's the go-to for structured ML tasks like this.

### What is SHAP?
SHAP (SHapley Additive exPlanations) is a model explainability library. For each prediction, it tells you exactly which features pushed the score toward phishing and by how much. This is what powers the `top_reasons` in the API response — not just "it's phishing" but *why*.

### Why not just check a blocklist?
Blocklists only catch known phishing URLs. ML catches *new* ones based on structural patterns — a URL that was registered 2 hours ago and mimics PayPal's domain will be caught by the model even if it's not in any blocklist yet.

### Limitations
- The model is trained on a static dataset — it won't automatically learn new patterns without retraining
- Very short or generic URLs (e.g. `bit.ly/abc123`) are hard to classify without resolving the redirect
- Domain age via WHOIS can be slow — it's optional in this implementation

---

## Features Roadmap

- [x] URL feature extraction (15 indicators)
- [x] XGBoost classifier with ~96% accuracy
- [x] SHAP explainability
- [x] FastAPI REST endpoint
- [x] React UI with risk score + breakdown
- [x] Docker containerization
- [ ] Bulk CSV upload — classify many URLs at once
- [ ] Browser extension
- [ ] VirusTotal API cross-validation
- [ ] Retraining pipeline with new phishing data
- [ ] Historical results stored in PostgreSQL
