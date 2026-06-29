from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.explain.shap_service import ExplanationService
from app.pose.feature_extractor import extract_body_features, parse_views
from app.profiling.labeler import BODY_TYPE_NAMES
from app.profiling.model_service import BodyProfileModelService
from app.recommendation.exercise_rules import get_recommendation
from app.schemas import AnalyzeResponse, FeatureAnalyzeRequest, LandmarkAnalyzeRequest

router = APIRouter(prefix="/api/v1")
settings = get_settings()
model_service = BodyProfileModelService(settings.model_dir)
explanation_service = ExplanationService(model_service)


def _compose_response(user_id: str | None, features: dict, feature_quality: dict) -> AnalyzeResponse:
    prediction = model_service.predict(features)
    body_type = prediction["body_type"]
    explanation = explanation_service.explain(features, body_type)
    recommendations = get_recommendation(body_type)
    return AnalyzeResponse(
        user_id=user_id,
        features=features,
        feature_quality=feature_quality,
        body_type=body_type,
        body_type_name=prediction["body_type_name"],
        probabilities=prediction["probabilities"],
        explanations=explanation,
        recommendations=recommendations,
    )


@router.post("/analyze/landmarks", response_model=AnalyzeResponse)
def analyze_landmarks(payload: LandmarkAnalyzeRequest) -> AnalyzeResponse:
    raw_views = [item.model_dump() for item in payload.views]
    views = parse_views(raw_views)
    features, quality = extract_body_features(views, visibility_threshold=settings.visibility_threshold)
    if quality["landmark_count"] == 0:
        raise HTTPException(status_code=422, detail="landmarks are empty")
    return _compose_response(payload.user_id, features, quality)


@router.post("/analyze/features", response_model=AnalyzeResponse)
def analyze_features(payload: FeatureAnalyzeRequest) -> AnalyzeResponse:
    features = payload.features.model_dump()
    quality = {
        "view_count": 0,
        "landmark_count": 0,
        "visible_landmark_ratio": 1.0,
        "present_views": "features-only",
    }
    return _compose_response(payload.user_id, features, quality)


@router.get("/exercises/{body_type}")
def exercises(body_type: str) -> dict:
    body_type = body_type.upper()
    if body_type not in BODY_TYPE_NAMES:
        raise HTTPException(status_code=404, detail="body_type must be one of A, B, C, D")
    return {
        "body_type": body_type,
        "body_type_name": BODY_TYPE_NAMES[body_type],
        "recommendations": get_recommendation(body_type),
    }


@router.get("/body-types")
def body_types() -> dict:
    return BODY_TYPE_NAMES
