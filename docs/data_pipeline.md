# 데이터 및 학습 파이프라인

## 1. 원천 데이터

논문에서는 Kaggle Posture Keypoint Detection 데이터셋을 활용하여 초기 검증을 수행하였다. 본 플랫폼은 공개 데이터셋을 직접 포함하지 않고, 사용자가 원 라이선스에 따라 다운로드한 데이터를 `data/raw/`에 배치하는 구조를 따른다.

## 2. 특징 추출

입력 랜드마크에서 다음 특징을 추출한다.

- `F1_forward_head`: 측면 귀-어깨 상대 거리 기반 목 전방 이동
- `F2_rounded_shoulder`: 어깨/팔 관절 위치 기반 어깨 말림
- `F3_shoulder_asymmetry`: 정면 또는 후면 좌우 어깨 높이 차
- `F4_lateral_balance`: 중심축 대비 상체 좌우 기울기
- `F5_trunk_flexion`: 측면 어깨-골반 축과 수직축 사이의 상체 굴곡

## 3. 재라벨링

논문 기준과 동일하게 특징 우세 패턴으로 4개 유형을 구성한다.

- A: 어깨 말림 우세형
- B: 목 전방 돌출 우세형
- C: 좌우 비대칭 동반형
- D: 전반적 상체 굴곡형

`backend/app/profiling/labeler.py`는 모델 학습 전 특징 벡터를 규칙 기반으로 라벨링할 때 사용된다.

## 4. 학습

```bash
cd backend
python scripts/train_xgboost.py --input ../data/processed/features.csv --output-dir models
```

모델 파일은 다음 위치에 저장된다.

```text
backend/models/body_profile_xgb.json
backend/models/label_encoder.json
backend/models/feature_summary.json
```

## 5. 설명 가능성

모델이 존재하고 `shap` 패키지가 설치되어 있으면 `TreeExplainer`로 샘플별 특징 기여도를 계산한다. 모델 또는 SHAP이 없을 때는 규칙 기반 점수 기여도를 대체 설명으로 반환한다.
