from __future__ import annotations

from pathlib import Path
from typing import Any


class MediaPipePoseAdapter:
    """Optional server-side MediaPipe adapter.

    The main platform path extracts landmarks in the mobile frontend to reduce server load.
    This adapter is provided for batch processing and dataset conversion scripts.
    Install `mediapipe` and provide a `.task` model path to enable it.
    """

    def __init__(self, model_path: str | Path):
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
        except Exception as exc:  # pragma: no cover - optional dependency path
            raise RuntimeError("mediapipe is required for server-side pose extraction") from exc

        self._mp_python = python
        self._vision = vision
        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
        )
        self._detector = vision.PoseLandmarker.create_from_options(options)

    def detect_image(self, image_path: str | Path) -> list[dict[str, float]]:
        import mediapipe as mp  # pragma: no cover

        image = mp.Image.create_from_file(str(image_path))
        result = self._detector.detect(image)
        if not result.pose_landmarks:
            return []
        landmarks = result.pose_landmarks[0]
        return [
            {
                "x": float(lm.x),
                "y": float(lm.y),
                "z": float(lm.z),
                "visibility": float(getattr(lm, "visibility", 1.0)),
            }
            for lm in landmarks
        ]
