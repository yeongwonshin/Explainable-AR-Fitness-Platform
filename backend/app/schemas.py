from typing import Literal, Optional
from pydantic import BaseModel, Field

BodyType = Literal["A", "B", "C", "D"]
ViewName = Literal["front", "back", "left", "right", "side_left", "side_right"]


class Landmark(BaseModel):
    x: float = Field(..., ge=-5.0, le=5.0)
    y: float = Field(..., ge=-5.0, le=5.0)
    z: Optional[float] = Field(default=0.0, ge=-5.0, le=5.0)
    visibility: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)


class LandmarkView(BaseModel):
    view: ViewName
    landmarks: list[Landmark]


class LandmarkAnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    views: list[LandmarkView]


class FeatureVector(BaseModel):
    F1_forward_head: float = Field(..., ge=0.0)
    F2_rounded_shoulder: float = Field(..., ge=0.0)
    F3_shoulder_asymmetry: float = Field(..., ge=0.0)
    F4_lateral_balance: float = Field(..., ge=0.0)
    F5_trunk_flexion: float = Field(..., ge=0.0)


class FeatureAnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    features: FeatureVector


class FeatureContribution(BaseModel):
    feature: str
    display_name: str
    contribution: float
    value: float
    direction: Literal["increase", "decrease", "neutral"] = "neutral"


class Explanation(BaseModel):
    method: str
    top_features: list[FeatureContribution]
    natural_language: str


class ExerciseItem(BaseModel):
    name: str
    target: str
    guide: str
    dose: str
    caution: str


class Recommendation(BaseModel):
    phase_1_release: list[ExerciseItem]
    phase_2_activate: list[ExerciseItem]
    phase_3_strengthen: list[ExerciseItem]
    safety_note: str


class AnalyzeResponse(BaseModel):
    user_id: Optional[str]
    features: dict[str, float]
    feature_quality: dict[str, float | int | str]
    body_type: BodyType
    body_type_name: str
    probabilities: dict[str, float]
    explanations: Explanation
    recommendations: Recommendation
