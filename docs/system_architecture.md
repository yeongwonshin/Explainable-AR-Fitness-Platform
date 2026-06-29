# 시스템 아키텍처 문서

## 목표

논문에서 제안한 모바일 AR 기반 개인화 운동 추천 시스템을 다음 네 개 계층으로 플랫폼화한다.

1. **Sensing Layer**: 스마트폰 카메라와 MediaPipe Pose 기반 관절 좌표 추출
2. **Profiling Layer**: F1~F5 체형 특징 추출 및 체형 유형 분류
3. **Explanation & Recommendation Layer**: SHAP 기반 판정 근거와 단계별 운동 추천
4. **AR Coaching Layer**: 사용자의 화면 위에 체형 분석 결과와 운동 안내를 오버레이

## 백엔드 모듈

```text
backend/app
├── main.py                         # FastAPI 엔트리포인트
├── api/routes.py                   # REST API 라우팅
├── pose/feature_extractor.py       # F1~F5 특징 계산
├── pose/mediapipe_adapter.py       # 이미지 -> landmark 확장 어댑터
├── profiling/model_service.py      # XGBoost 또는 규칙 기반 체형 판정
├── explain/shap_service.py         # SHAP 설명/대체 중요도 계산
└── recommendation/exercise_rules.py# 운동 추천 규칙
```

## 프론트엔드 모듈

```text
frontend/src
├── App.tsx                         # 전체 화면 흐름
├── components/CameraCapture.tsx    # 카메라 입력 및 뷰별 캡처
├── components/AROverlay.tsx        # 랜드마크/체형 특징 오버레이
├── components/ResultPanel.tsx      # 분석 결과 및 운동 추천 표시
├── services/api.ts                 # 백엔드 통신
└── vision/poseLandmarker.ts        # MediaPipe Tasks Vision 래퍼
```

## 데이터 흐름

1. 사용자가 `front`, `left`, `right`, `back` 자세를 캡처한다.
2. 프론트엔드가 각 뷰에서 Pose Landmarker를 실행하여 33개 랜드마크를 얻는다.
3. 백엔드가 관절 visibility 기준으로 필터링한다.
4. F1~F5 특징 벡터를 계산한다.
5. XGBoost 모델이 있으면 모델 기반 분류를 수행한다.
6. 모델이 없으면 논문에서 설명한 특징 우세 패턴 규칙으로 분류한다.
7. SHAP 사용 가능 시 샘플별 기여도를 계산한다.
8. 체형 유형에 대응되는 Release-Activate-Strengthen 운동을 추천한다.
9. 프론트엔드가 결과와 운동 가이드를 AR 형태로 오버레이한다.

## 확장 포인트

- Native mobile: `frontend`를 React Native 또는 Flutter로 대체 가능
- ARCore/ARKit: 현재는 웹 캔버스 오버레이이며, 추후 네이티브 AR 앵커로 확장 가능
- 데이터 수집: 자체 사용자 데이터셋을 `data/raw`에 적재 후 `train_xgboost.py`로 학습
- 안전성: 운동 추천 전 문진, 통증 여부, 운동 금기 조건 필터 추가 필요
