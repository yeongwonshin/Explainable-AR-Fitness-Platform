from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, sqrt
from statistics import mean
from typing import Iterable, Mapping

from app.pose import landmark_indices as L

FEATURE_DISPLAY_NAMES = {
    "F1_forward_head": "목 전방 이동",
    "F2_rounded_shoulder": "어깨 말림",
    "F3_shoulder_asymmetry": "좌우 어깨 비대칭",
    "F4_lateral_balance": "좌우 상체 균형",
    "F5_trunk_flexion": "상체 굴곡",
}


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


def _as_point(value: object) -> Point:
    if isinstance(value, Point):
        return value
    if isinstance(value, Mapping):
        return Point(
            x=float(value.get("x", 0.0)),
            y=float(value.get("y", 0.0)),
            z=float(value.get("z", 0.0) or 0.0),
            visibility=float(value.get("visibility", 1.0) or 0.0),
        )
    return Point(
        x=float(getattr(value, "x")),
        y=float(getattr(value, "y")),
        z=float(getattr(value, "z", 0.0) or 0.0),
        visibility=float(getattr(value, "visibility", 1.0) or 0.0),
    )


def normalize_view_name(view: str) -> str:
    mapping = {
        "left": "side_left",
        "right": "side_right",
        "side_left": "side_left",
        "side_right": "side_right",
        "front": "front",
        "back": "back",
    }
    return mapping.get(view, view)


def parse_views(raw_views: Iterable[Mapping]) -> dict[str, list[Point]]:
    parsed: dict[str, list[Point]] = {}
    for item in raw_views:
        view = normalize_view_name(str(item["view"]))
        parsed[view] = [_as_point(p) for p in item.get("landmarks", [])]
    return parsed


def _get(points: list[Point], idx: int, visibility_threshold: float) -> Point | None:
    if idx >= len(points):
        return None
    point = points[idx]
    if point.visibility < visibility_threshold:
        return None
    return point


def _avg(points: list[Point | None]) -> Point | None:
    valid = [p for p in points if p is not None]
    if not valid:
        return None
    return Point(
        x=mean(p.x for p in valid),
        y=mean(p.y for p in valid),
        z=mean(p.z for p in valid),
        visibility=mean(p.visibility for p in valid),
    )


def _dist2(a: Point, b: Point) -> float:
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def _safe_div(value: float, denom: float, eps: float = 1e-6) -> float:
    return value / max(abs(denom), eps)


def _clip01(value: float) -> float:
    return float(max(0.0, min(1.0, value)))


def _shoulder_width(points: list[Point], visibility_threshold: float) -> float | None:
    left = _get(points, L.LEFT_SHOULDER, visibility_threshold)
    right = _get(points, L.RIGHT_SHOULDER, visibility_threshold)
    if left is None or right is None:
        return None
    return max(_dist2(left, right), 1e-6)


def _torso_height(points: list[Point], visibility_threshold: float) -> float | None:
    shoulder = _avg([
        _get(points, L.LEFT_SHOULDER, visibility_threshold),
        _get(points, L.RIGHT_SHOULDER, visibility_threshold),
    ])
    hip = _avg([
        _get(points, L.LEFT_HIP, visibility_threshold),
        _get(points, L.RIGHT_HIP, visibility_threshold),
    ])
    if shoulder is None or hip is None:
        return None
    return max(abs(shoulder.y - hip.y), 1e-6)


def _side_features(points: list[Point], visibility_threshold: float) -> dict[str, float]:
    ear = _avg([_get(points, L.LEFT_EAR, visibility_threshold), _get(points, L.RIGHT_EAR, visibility_threshold)])
    shoulder = _avg([
        _get(points, L.LEFT_SHOULDER, visibility_threshold),
        _get(points, L.RIGHT_SHOULDER, visibility_threshold),
    ])
    hip = _avg([_get(points, L.LEFT_HIP, visibility_threshold), _get(points, L.RIGHT_HIP, visibility_threshold)])
    elbow = _avg([_get(points, L.LEFT_ELBOW, visibility_threshold), _get(points, L.RIGHT_ELBOW, visibility_threshold)])

    if shoulder is None or hip is None:
        return {}

    norm = max(abs(shoulder.y - hip.y), 1e-6)

    f1 = 0.0
    if ear is not None:
        # 측면에서 귀-어깨의 수평 상대 거리. 좌/우 측면 방향 차이를 고려해 절댓값을 사용한다.
        f1 = _clip01(abs(ear.x - shoulder.x) / norm)

    f2 = 0.0
    if elbow is not None:
        # 어깨와 팔꿈치가 몸통 축에서 앞으로 이동한 정도를 어깨 말림 proxy로 사용한다.
        shoulder_forward = abs(shoulder.x - hip.x) / norm
        elbow_forward = abs(elbow.x - shoulder.x) / norm
        f2 = _clip01(0.65 * shoulder_forward + 0.35 * elbow_forward)
    else:
        f2 = _clip01(abs(shoulder.x - hip.x) / norm)

    dx = abs(shoulder.x - hip.x)
    dy = abs(shoulder.y - hip.y)
    angle_from_vertical = degrees(atan2(dx, max(dy, 1e-6)))
    f5 = _clip01(angle_from_vertical / 45.0)

    return {
        "F1_forward_head": f1,
        "F2_rounded_shoulder": f2,
        "F5_trunk_flexion": f5,
    }


def _frontal_features(points: list[Point], visibility_threshold: float) -> dict[str, float]:
    left_shoulder = _get(points, L.LEFT_SHOULDER, visibility_threshold)
    right_shoulder = _get(points, L.RIGHT_SHOULDER, visibility_threshold)
    left_hip = _get(points, L.LEFT_HIP, visibility_threshold)
    right_hip = _get(points, L.RIGHT_HIP, visibility_threshold)

    if left_shoulder is None or right_shoulder is None:
        return {}

    width = max(_dist2(left_shoulder, right_shoulder), 1e-6)
    f3 = _clip01(abs(left_shoulder.y - right_shoulder.y) / width)

    f4 = 0.0
    if left_hip is not None and right_hip is not None:
        shoulder_mid = _avg([left_shoulder, right_shoulder])
        hip_mid = _avg([left_hip, right_hip])
        assert shoulder_mid is not None and hip_mid is not None
        f4 = _clip01(abs(shoulder_mid.x - hip_mid.x) / width)

    return {
        "F3_shoulder_asymmetry": f3,
        "F4_lateral_balance": f4,
    }


def estimate_quality(views: dict[str, list[Point]], visibility_threshold: float = 0.5) -> dict[str, float | int | str]:
    total = sum(len(v) for v in views.values())
    visible = sum(1 for view in views.values() for p in view if p.visibility >= visibility_threshold)
    ratio = visible / total if total else 0.0
    present_views = ",".join(sorted(views.keys())) if views else "none"
    return {
        "view_count": len(views),
        "landmark_count": total,
        "visible_landmark_ratio": round(ratio, 4),
        "present_views": present_views,
    }


def extract_body_features(
    views: dict[str, list[Point]],
    visibility_threshold: float = 0.5,
) -> tuple[dict[str, float], dict[str, float | int | str]]:
    """Extract F1~F5 features from MediaPipe pose landmarks.

    The feature definitions follow the paper-level prototype: they are posture proxies
    normalized by torso height or shoulder width, not clinical measurements.
    """
    side_values: dict[str, list[float]] = {
        "F1_forward_head": [],
        "F2_rounded_shoulder": [],
        "F5_trunk_flexion": [],
    }
    frontal_values: dict[str, list[float]] = {
        "F3_shoulder_asymmetry": [],
        "F4_lateral_balance": [],
    }

    for side in ("side_left", "side_right"):
        if side in views:
            computed = _side_features(views[side], visibility_threshold)
            for key in side_values:
                if key in computed:
                    side_values[key].append(computed[key])

    for frontal in ("front", "back"):
        if frontal in views:
            computed = _frontal_features(views[frontal], visibility_threshold)
            for key in frontal_values:
                if key in computed:
                    frontal_values[key].append(computed[key])

    features = {
        "F1_forward_head": max(side_values["F1_forward_head"] or [0.0]),
        "F2_rounded_shoulder": max(side_values["F2_rounded_shoulder"] or [0.0]),
        "F3_shoulder_asymmetry": mean(frontal_values["F3_shoulder_asymmetry"] or [0.0]),
        "F4_lateral_balance": mean(frontal_values["F4_lateral_balance"] or [0.0]),
        "F5_trunk_flexion": max(side_values["F5_trunk_flexion"] or [0.0]),
    }
    return {k: round(float(v), 6) for k, v in features.items()}, estimate_quality(views, visibility_threshold)
