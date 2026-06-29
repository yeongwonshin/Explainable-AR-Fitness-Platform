from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import numpy as np

from app.profiling.labeler import BODY_TYPE_NAMES, normalize_scores, relabel_by_dominant_pattern, rule_scores

FEATURE_ORDER = [
    "F1_forward_head",
    "F2_rounded_shoulder",
    "F3_shoulder_asymmetry",
    "F4_lateral_balance",
    "F5_trunk_flexion",
]


class BodyProfileModelService:
    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.label_encoder: dict[str, str] = {"0": "A", "1": "B", "2": "C", "3": "D"}
        self._load_model_if_available()

    @property
    def model_available(self) -> bool:
        return self.model is not None

    def _load_model_if_available(self) -> None:
        model_path = self.model_dir / "body_profile_xgb.json"
        encoder_path = self.model_dir / "label_encoder.json"
        if not model_path.exists():
            return
        try:
            from xgboost import XGBClassifier

            model = XGBClassifier()
            model.load_model(str(model_path))
            self.model = model
            if encoder_path.exists():
                self.label_encoder = json.loads(encoder_path.read_text(encoding="utf-8"))
        except Exception:
            # 운영 환경에서는 로깅 시스템으로 전달한다. 연구 프로토타입에서는 규칙 기반으로 안전하게 폴백한다.
            self.model = None

    def _to_array(self, features: Mapping[str, float]) -> np.ndarray:
        return np.array([[float(features.get(name, 0.0)) for name in FEATURE_ORDER]], dtype=float)

    def predict(self, features: Mapping[str, float]) -> dict:
        if self.model_available:
            x = self._to_array(features)
            prob = self.model.predict_proba(x)[0]
            classes = [self.label_encoder.get(str(i), str(i)) for i in range(len(prob))]
            probabilities = {label: round(float(p), 6) for label, p in zip(classes, prob)}
            body_type = max(probabilities.items(), key=lambda kv: kv[1])[0]
            return {
                "body_type": body_type,
                "body_type_name": BODY_TYPE_NAMES[body_type],
                "probabilities": probabilities,
                "method": "xgboost",
            }

        scores = rule_scores(features)
        probabilities = normalize_scores(scores)
        body_type = relabel_by_dominant_pattern(features)
        return {
            "body_type": body_type,
            "body_type_name": BODY_TYPE_NAMES[body_type],
            "probabilities": probabilities,
            "method": "dominant-feature-rule",
        }
