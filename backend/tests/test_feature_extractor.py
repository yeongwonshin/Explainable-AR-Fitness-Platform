from app.pose.feature_extractor import extract_body_features, parse_views


def lm(x, y, v=1.0):
    return {"x": x, "y": y, "z": 0, "visibility": v}


def make_landmarks():
    points = [lm(0, 0, 0.0) for _ in range(33)]
    points[7] = lm(0.56, 0.20)
    points[8] = lm(0.56, 0.20)
    points[11] = lm(0.50, 0.32)
    points[12] = lm(0.52, 0.32)
    points[13] = lm(0.58, 0.44)
    points[14] = lm(0.58, 0.44)
    points[23] = lm(0.50, 0.70)
    points[24] = lm(0.52, 0.70)
    return points


def test_extract_features_from_side_and_front():
    front = make_landmarks()
    front[11] = lm(0.42, 0.30)
    front[12] = lm(0.58, 0.34)
    front[23] = lm(0.45, 0.70)
    front[24] = lm(0.55, 0.70)

    views = parse_views([
        {"view": "front", "landmarks": front},
        {"view": "left", "landmarks": make_landmarks()},
    ])
    features, quality = extract_body_features(views)

    assert quality["view_count"] == 2
    assert features["F1_forward_head"] > 0
    assert features["F3_shoulder_asymmetry"] > 0
    assert set(features) == {
        "F1_forward_head",
        "F2_rounded_shoulder",
        "F3_shoulder_asymmetry",
        "F4_lateral_balance",
        "F5_trunk_flexion",
    }
