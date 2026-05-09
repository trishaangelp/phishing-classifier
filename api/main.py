from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from schemas import ClassifyRequest, ClassifyResponse, HealthResponse
import classifier as clf


@asynccontextmanager
async def lifespan(app: FastAPI):
    clf.load_model()
    yield


app = FastAPI(
    title="Phishing URL Classifier",
    description="ML-powered API to detect phishing URLs using XGBoost + SHAP explainability.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return {
        "status": "ok",
        "model_loaded": clf._model is not None,
    }


@app.post("/classify", response_model=ClassifyResponse, tags=["Classifier"])
def classify(request: ClassifyRequest):
    """
    Classify a URL as phishing or legitimate.

    Returns a risk score (0–100), confidence, prediction label,
    human-readable reasons, and raw feature values.
    """
    try:
        result = clf.classify(request.url)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@app.get("/", tags=["System"])
def root():
    return {
        "message": "🎣 Phishing URL Classifier API",
        "docs": "/docs",
        "classify": "POST /classify",
    }
