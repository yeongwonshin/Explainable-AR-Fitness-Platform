import { FilesetResolver, PoseLandmarker } from '@mediapipe/tasks-vision';
import type { Landmark } from '../types';

let landmarkerPromise: Promise<PoseLandmarker> | undefined;

export async function getPoseLandmarker(): Promise<PoseLandmarker> {
  if (!landmarkerPromise) {
    landmarkerPromise = createPoseLandmarker();
  }
  return landmarkerPromise;
}

async function createPoseLandmarker(): Promise<PoseLandmarker> {
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
  );
  return PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: '/models/pose_landmarker_lite.task',
      delegate: 'GPU'
    },
    runningMode: 'VIDEO',
    numPoses: 1
  });
}

export async function detectPoseFromVideo(video: HTMLVideoElement): Promise<Landmark[]> {
  const landmarker = await getPoseLandmarker();
  const result = landmarker.detectForVideo(video, performance.now());
  const landmarks = result.landmarks?.[0] ?? [];
  return landmarks.map((lm) => ({
    x: lm.x,
    y: lm.y,
    z: lm.z,
    visibility: lm.visibility ?? 1
  }));
}
