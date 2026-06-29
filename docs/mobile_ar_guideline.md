# 모바일 AR 화면 설계 가이드

## 화면 흐름

1. 사용자 안내: 정면, 좌측면, 우측면, 후면 촬영 순서 표시
2. 촬영 보조: 수평선, 거리 안내, 전신 프레임 가이드 표시
3. 관절 인식: MediaPipe landmark skeleton 표시
4. 분석 결과: 체형 유형, F1~F5 특징값, 주요 기여 특징 표시
5. 운동 추천: Release-Activate-Strengthen 단계별 카드 표시
6. 운동 수행: 목표 관절선, 주의 문구, 반복/세트 가이드 오버레이

## AR 오버레이 원칙

- 진단 문구 대신 “특징이 상대적으로 크게 나타남”과 같은 연구 프로토타입 표현 사용
- 통증, 어지러움, 저림이 있으면 운동 중단 문구 표시
- 랜드마크 visibility가 낮을 경우 결과 신뢰도 낮음 표시
- 사진/영상은 기본적으로 서버에 저장하지 않음

## 향후 네이티브 확장

- Android: CameraX + MediaPipe Tasks + ARCore Sceneform 또는 Filament
- iOS: AVFoundation + MediaPipe Tasks + ARKit
- Cross-platform: Flutter Camera + CustomPainter 또는 React Native Vision Camera
