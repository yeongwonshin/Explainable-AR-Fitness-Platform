import { useEffect, useRef, useState } from 'react';
import AROverlay from './AROverlay';
import { detectPoseFromVideo } from '../vision/poseLandmarker';
import type { Landmark, LandmarkView, ViewName } from '../types';

const VIEW_SEQUENCE: ViewName[] = ['front', 'left', 'right', 'back'];
const VIEW_LABELS: Record<ViewName, string> = {
  front: '정면',
  left: '좌측면',
  right: '우측면',
  back: '후면'
};

interface Props {
  onSubmit: (views: LandmarkView[]) => Promise<void>;
  disabled?: boolean;
}

export default function CameraCapture({ onSubmit, disabled }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [currentViewIndex, setCurrentViewIndex] = useState(0);
  const [landmarks, setLandmarks] = useState<Landmark[]>([]);
  const [captured, setCaptured] = useState<LandmarkView[]>([]);
  const [cameraReady, setCameraReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let stream: MediaStream | null = null;
    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 1280 } },
          audio: false
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
          setCameraReady(true);
        }
      } catch (err) {
        setError('카메라 접근에 실패했습니다. HTTPS 또는 localhost에서 실행하세요.');
      }
    }
    start();
    return () => stream?.getTracks().forEach((track) => track.stop());
  }, []);

  useEffect(() => {
    let raf = 0;
    async function loop() {
      if (videoRef.current && cameraReady) {
        try {
          const next = await detectPoseFromVideo(videoRef.current);
          setLandmarks(next);
        } catch {
          // 모델 파일이 아직 없으면 오버레이만 비활성화된다.
        }
      }
      raf = requestAnimationFrame(loop);
    }
    loop();
    return () => cancelAnimationFrame(raf);
  }, [cameraReady]);

  const currentView = VIEW_SEQUENCE[currentViewIndex];

  function captureCurrentView() {
    if (!landmarks.length) {
      setError('랜드마크가 아직 감지되지 않았습니다. 전신이 화면에 보이도록 조정하세요.');
      return;
    }
    setError(null);
    const nextCaptured = [...captured.filter((item) => item.view !== currentView), { view: currentView, landmarks }];
    setCaptured(nextCaptured);
    if (currentViewIndex < VIEW_SEQUENCE.length - 1) {
      setCurrentViewIndex(currentViewIndex + 1);
    }
  }

  async function submit() {
    await onSubmit(captured);
  }

  return (
    <section className="camera-card">
      <div className="camera-frame">
        <video ref={videoRef} playsInline muted className="camera-video" />
        <AROverlay landmarks={landmarks} width={360} height={640} guideText={`${VIEW_LABELS[currentView]} 자세를 촬영하세요`} />
      </div>
      <div className="capture-toolbar">
        <div>
          <strong>{VIEW_LABELS[currentView]}</strong>
          <span>{captured.length}/4 뷰 캡처 완료</span>
        </div>
        <button onClick={captureCurrentView} disabled={disabled || !cameraReady}>현재 뷰 저장</button>
        <button onClick={submit} disabled={disabled || captured.length < 2}>분석 요청</button>
      </div>
      <p className="helper-text">최소 정면+측면 2개 뷰가 있으면 분석할 수 있으며, 4개 뷰를 촬영하면 좌우 비대칭 특징이 더 안정적입니다.</p>
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
