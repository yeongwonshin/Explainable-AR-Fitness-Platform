import { useState } from 'react';
import CameraCapture from './components/CameraCapture';
import ResultPanel from './components/ResultPanel';
import { analyzeLandmarks } from './services/api';
import type { AnalyzeResponse, LandmarkView } from './types';

export default function App() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(views: LandmarkView[]) {
    setLoading(true);
    setError(null);
    try {
      const response = await analyzeLandmarks(views);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : '분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Explainable Body Profiling · Mobile AR</p>
          <h1>설명 가능한 체형 분석 기반 AR 운동 코칭</h1>
          <p>스마트폰 카메라로 자세를 촬영하고 F1~F5 체형 특징, 판정 근거, 단계별 운동 추천을 확인합니다.</p>
        </div>
      </header>

      <div className="layout">
        <CameraCapture onSubmit={handleAnalyze} disabled={loading} />
        <ResultPanel result={result} />
      </div>

      {loading && <div className="toast">분석 중입니다...</div>}
      {error && <div className="toast error">{error}</div>}
    </main>
  );
}
