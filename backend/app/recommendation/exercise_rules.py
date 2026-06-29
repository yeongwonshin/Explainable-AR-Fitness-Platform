from __future__ import annotations

from copy import deepcopy

SAFETY_NOTE = (
    "본 추천은 저강도 교정 운동 중심의 연구 프로토타입입니다. 통증, 저림, 어지러움, 수술/질환 이력이 있으면 "
    "운동을 중단하고 전문가와 상담하세요."
)

EXERCISE_RULES = {
    "A": {
        "phase_1_release": [
            {
                "name": "흉근 벽 스트레칭",
                "target": "대흉근/소흉근 이완",
                "guide": "팔꿈치를 벽에 대고 몸통을 천천히 반대 방향으로 회전합니다.",
                "dose": "20~30초 x 2세트",
                "caution": "어깨 앞쪽 통증이 있으면 범위를 줄입니다.",
            },
            {
                "name": "흉추 폼롤러 신전",
                "target": "흉추 신전 가동성",
                "guide": "폼롤러를 등 위쪽에 두고 과도하게 허리를 꺾지 않으며 천천히 젖힙니다.",
                "dose": "6~8회 x 2세트",
                "caution": "목을 과도하게 뒤로 젖히지 않습니다.",
            },
        ],
        "phase_2_activate": [
            {
                "name": "벽 슬라이드",
                "target": "전거근/하부 승모근 활성화",
                "guide": "등과 팔을 벽에 가깝게 유지하며 팔을 천천히 올리고 내립니다.",
                "dose": "8~10회 x 2세트",
                "caution": "갈비뼈가 앞으로 들리지 않게 합니다.",
            },
            {
                "name": "밴드 풀어파트",
                "target": "견갑 후인 근육 활성화",
                "guide": "팔을 어깨 높이에 두고 밴드를 좌우로 벌립니다.",
                "dose": "10~12회 x 2세트",
                "caution": "어깨가 귀 쪽으로 올라가지 않게 합니다.",
            },
        ],
        "phase_3_strengthen": [
            {
                "name": "스캐풀라 푸시업",
                "target": "견갑 안정화",
                "guide": "팔꿈치를 편 상태에서 날개뼈만 모으고 밀어냅니다.",
                "dose": "8~10회 x 2세트",
                "caution": "허리가 꺾이지 않게 복부에 힘을 줍니다.",
            }
        ],
    },
    "B": {
        "phase_1_release": [
            {
                "name": "후두하근 이완",
                "target": "목 뒤쪽 과긴장 완화",
                "guide": "작은 공을 뒤통수 아래에 두고 가볍게 압박합니다.",
                "dose": "30초 x 2세트",
                "caution": "어지러움이나 두통이 생기면 즉시 중단합니다.",
            },
            {
                "name": "상부 승모근 스트레칭",
                "target": "목-어깨 긴장 완화",
                "guide": "한 손으로 의자를 잡고 머리를 반대쪽으로 천천히 기울입니다.",
                "dose": "20초 x 2세트",
                "caution": "팔 저림이 있으면 시행하지 않습니다.",
            },
        ],
        "phase_2_activate": [
            {
                "name": "턱 당기기",
                "target": "심부 경추 굴곡근 활성화",
                "guide": "고개를 숙이지 않고 턱을 수평으로 뒤로 당깁니다.",
                "dose": "5초 유지 x 8회 x 2세트",
                "caution": "목 앞쪽에 과도한 힘이 들어가지 않게 합니다.",
            },
            {
                "name": "견갑 세팅",
                "target": "견갑 안정화",
                "guide": "어깨를 아래와 뒤로 가볍게 정렬한 뒤 호흡을 유지합니다.",
                "dose": "5초 유지 x 8회",
                "caution": "허리를 꺾어 보상하지 않습니다.",
            },
        ],
        "phase_3_strengthen": [
            {
                "name": "월 엔젤",
                "target": "목-흉추-견갑 협응 강화",
                "guide": "벽에 뒤통수와 등을 가깝게 두고 팔을 천천히 올립니다.",
                "dose": "6~8회 x 2세트",
                "caution": "턱이 앞으로 튀어나오지 않게 합니다.",
            }
        ],
    },
    "C": {
        "phase_1_release": [
            {
                "name": "측면 몸통 스트레칭",
                "target": "좌우 몸통 긴장 차이 완화",
                "guide": "한쪽 팔을 머리 위로 올리고 반대쪽으로 천천히 기울입니다.",
                "dose": "20초 x 좌우 2세트",
                "caution": "골반이 한쪽으로 밀리지 않게 합니다.",
            }
        ],
        "phase_2_activate": [
            {
                "name": "데드버그",
                "target": "코어 안정화",
                "guide": "허리를 바닥에 가볍게 유지한 채 반대쪽 팔과 다리를 천천히 내립니다.",
                "dose": "좌우 6~8회 x 2세트",
                "caution": "허리가 뜨면 범위를 줄입니다.",
            },
            {
                "name": "사이드 플랭크 변형",
                "target": "측면 코어 활성화",
                "guide": "무릎을 대고 옆으로 지지하며 몸통을 일직선으로 유지합니다.",
                "dose": "10~20초 x 좌우 2세트",
                "caution": "어깨 통증이 있으면 팔꿈치 위치를 조정합니다.",
            },
        ],
        "phase_3_strengthen": [
            {
                "name": "한팔 밴드 로우",
                "target": "좌우 견갑 조절 강화",
                "guide": "좌우 같은 속도로 밴드를 당기며 몸통 회전을 최소화합니다.",
                "dose": "좌우 8~10회 x 2세트",
                "caution": "몸이 한쪽으로 돌아가지 않게 합니다.",
            }
        ],
    },
    "D": {
        "phase_1_release": [
            {
                "name": "캣카우",
                "target": "척추 굴곡/신전 가동성",
                "guide": "네발기기 자세에서 등을 둥글게 말고 천천히 펴줍니다.",
                "dose": "8~10회 x 2세트",
                "caution": "통증이 없는 범위에서 움직입니다.",
            },
            {
                "name": "흉추 회전 스트레칭",
                "target": "상체 회전 가동성",
                "guide": "옆으로 누워 무릎을 고정하고 가슴을 반대쪽으로 엽니다.",
                "dose": "좌우 6회 x 2세트",
                "caution": "허리로 과도하게 비틀지 않습니다.",
            },
        ],
        "phase_2_activate": [
            {
                "name": "버드독",
                "target": "몸통 안정화",
                "guide": "반대쪽 팔과 다리를 뻗으며 골반이 기울지 않게 유지합니다.",
                "dose": "좌우 6~8회 x 2세트",
                "caution": "허리가 꺾이면 다리 높이를 낮춥니다.",
            }
        ],
        "phase_3_strengthen": [
            {
                "name": "힙힌지 패턴 연습",
                "target": "상체-골반 협응 강화",
                "guide": "막대를 등 뒤에 대고 머리-등-골반 접촉을 유지하며 엉덩이를 뒤로 보냅니다.",
                "dose": "8~10회 x 2세트",
                "caution": "등을 둥글게 말지 않습니다.",
            }
        ],
    },
}


def get_recommendation(body_type: str) -> dict:
    if body_type not in EXERCISE_RULES:
        raise ValueError(f"Unsupported body type: {body_type}")
    result = deepcopy(EXERCISE_RULES[body_type])
    result["safety_note"] = SAFETY_NOTE
    return result
