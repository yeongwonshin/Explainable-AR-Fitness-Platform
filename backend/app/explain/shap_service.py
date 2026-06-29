from __future__ import annotations

from typing import Mapping

import numpy as np

from app.pose.feature_extractor import FEATURE_DISPLAY_NAMES
from app.profiling.labeler import rule_scores
from app.profiling.model_service import FEATURE_ORDER, BodyProfileModelService


class ExplanationService:
    def __init__(self, model_service: BodyProfileModelService):
        self.model_service = model_service

    def explain(self, features: Mapping[str, float], body_type: str) -> dict:
        if self.model_service.model_available:
            shap_result = self._try_shap(features, body_type)
            if shap_result:
                return shap_result
        return self._rule_based_explanation(features, body_type)

    def _try_shap(self, features: Mapping[str, float], body_type: str) -> dict | None:
        try:
            import shap

            model = self.model_service.model
            x = np.array([[float(features.get(name, 0.0)) for name in FEATURE_ORDER]], dtype=float)
            explainer = shap.TreeExplainer(model)
            values = explainer.shap_values(x)

            if isinstance(values, list):
                class_index = {v: int(k) for k, v in self.model_service.label_encoder.items()}.get(body_type, 0)
                contribution_values = values[class_index][0]
            else:
                arr = np.asarray(values)
                if arr.ndim == 3:
                    class_index = {v: int(k) for k, v in self.model_service.label_encoder.items()}.get(body_type, 0)
                    contribution_values = arr[0, :, class_index]
                else:
                    contribution_values = arr[0]

            top = self._format_contributions(features, contribution_values)
            return {
                "method": "shap.TreeExplainer",
                "top_features": top,
                "natural_language": self._natural_language(top, body_type),
            }
        except Exception:
            return None

    def _rule_based_explanation(self, features: Mapping[str, float], body_type: str) -> dict:
        f = {k: float(features.get(k, 0.0)) for k in FEATURE_ORDER}
        if body_type == "A":
            contributions = [0.15 * f["F1_forward_head"], 1.0 * f["F2_rounded_shoulder"], 0.0, 0.0, 0.10 * f["F5_trunk_flexion"]]
        elif body_type == "B":
            contributions = [1.0 * f["F1_forward_head"], 0.12 * f["F2_rounded_shoulder"], 0.0, 0.0, 0.15 * f["F5_trunk_flexion"]]
        elif body_type == "C":
            contributions = [0.0, 0.0, 0.75 * f["F3_shoulder_asymmetry"], 0.75 * f["F4_lateral_balance"], 0.0]
        else:
            contributions = [0.15 * f["F1_forward_head"], 0.15 * f["F2_rounded_shoulder"], 0.0, 0.0, 1.0 * f["F5_trunk_flexion"]]
        top = self._format_contributions(features, contributions)
        return {
            "method": "dominant-feature-rule-contribution",
            "top_features": top,
            "natural_language": self._natural_language(top, body_type),
        }

    def _format_contributions(self, features: Mapping[str, float], contributions) -> list[dict]:
        rows = []
        for name, contribution in zip(FEATURE_ORDER, contributions):
            c = float(contribution)
            rows.append({
                "feature": name,
                "display_name": FEATURE_DISPLAY_NAMES.get(name, name),
                "contribution": round(abs(c), 6),
                "value": round(float(features.get(name, 0.0)), 6),
                "direction": "increase" if c > 0 else "decrease" if c < 0 else "neutral",
            })
        return sorted(rows, key=lambda r: r["contribution"], reverse=True)[:3]

    def _natural_language(self, top_features: list[dict], body_type: str) -> str:
        if not top_features:
            return "분석 가능한 특징 기여도가 충분하지 않습니다."
        first = top_features[0]
        second = top_features[1] if len(top_features) > 1 else None
        sentence = f"{first['display_name']} 특징이 유형 {body_type} 판정에 가장 크게 기여했습니다."
        if second and second["contribution"] > 0:
            sentence += f" 다음으로 {second['display_name']} 특징의 영향이 확인되었습니다."
        sentence += " 이 설명은 연구 프로토타입의 특징 기반 판정 근거이며, 의학적 진단으로 해석해서는 안 됩니다."
        return sentence
