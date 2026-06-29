# API 명세

## `GET /health`

서버 상태 확인.

```json
{"status":"ok","service":"explainable-ar-fitness-platform"}
```

## `POST /api/v1/analyze/landmarks`

뷰별 MediaPipe 랜드마크를 입력받아 체형 분석을 수행한다.

### Request

```json
{
  "user_id": "demo-user",
  "views": [
    {"view": "front", "landmarks": [{"x": 0.1, "y": 0.2, "z": 0.0, "visibility": 0.9}]},
    {"view": "left", "landmarks": []},
    {"view": "right", "landmarks": []},
    {"view": "back", "landmarks": []}
  ]
}
```

### Response

```json
{
  "features": {"F1_forward_head": 0.42},
  "body_type": "B",
  "body_type_name": "목 전방 돌출 우세형",
  "probabilities": {"A": 0.12, "B": 0.71, "C": 0.08, "D": 0.09},
  "explanations": {
    "top_features": [
      {"feature": "F1_forward_head", "contribution": 0.42, "direction": "increase"}
    ],
    "natural_language": "목 전방 이동 특징이 체형 판정에 가장 크게 기여했습니다."
  },
  "recommendations": {
    "phase_1_release": [],
    "phase_2_activate": [],
    "phase_3_strengthen": []
  }
}
```

## `POST /api/v1/analyze/features`

이미 계산된 F1~F5 값을 입력받아 체형 유형과 추천 운동을 반환한다.

## `GET /api/v1/exercises/{body_type}`

유형 A, B, C, D에 해당하는 운동 추천 규칙을 반환한다.
