from __future__ import annotations

from typing import Mapping

BODY_TYPE_NAMES = {
    "A": "어깨 말림 우세형",
    "B": "목 전방 돌출 우세형",
    "C": "좌우 비대칭 동반형",
    "D": "전반적 상체 굴곡형",
}


def rule_scores(features: Mapping[str, float]) -> dict[str, float]:
    f1 = float(features.get("F1_forward_head", 0.0))
    f2 = float(features.get("F2_rounded_shoulder", 0.0))
    f3 = float(features.get("F3_shoulder_asymmetry", 0.0))
    f4 = float(features.get("F4_lateral_balance", 0.0))
    f5 = float(features.get("F5_trunk_flexion", 0.0))
    return {
        "A": 1.00 * f2 + 0.15 * f1 + 0.10 * f5,
        "B": 1.00 * f1 + 0.12 * f2 + 0.15 * f5,
        "C": 0.75 * f3 + 0.75 * f4,
        "D": 1.00 * f5 + 0.15 * f1 + 0.15 * f2,
    }


def normalize_scores(scores: Mapping[str, float]) -> dict[str, float]:
    clipped = {k: max(0.0, float(v)) for k, v in scores.items()}
    total = sum(clipped.values())
    if total <= 1e-9:
        return {k: 0.25 for k in ("A", "B", "C", "D")}
    return {k: round(v / total, 6) for k, v in clipped.items()}


def relabel_by_dominant_pattern(features: Mapping[str, float]) -> str:
    scores = rule_scores(features)
    return max(scores.items(), key=lambda kv: kv[1])[0]
