from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


class ClassifyRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_not_be_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith(("http://", "https://")):
            v = "http://" + v
        return v


class FeatureDetail(BaseModel):
    url_length: int
    domain_length: int
    num_dots: int
    num_hyphens: int
    num_subdomains: int
    has_ip: bool
    has_at: bool
    has_https: bool
    is_shortener: bool
    suspicious_tld: bool
    has_brand_keyword: bool
    path_depth: int
    has_query: bool
    num_special_chars: int
    has_double_slash: bool


class ClassifyResponse(BaseModel):
    url: str
    prediction: str           # "phishing" or "legitimate"
    is_phishing: bool
    confidence: float         # 0.0 – 1.0
    risk_score: int           # 0 – 100
    top_reasons: list[str]
    features: FeatureDetail


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
