import type { AnalyzeResponse, ExerciseItem } from '../types';

function ExerciseList({ title, items }: { title: string; items: ExerciseItem[] }) {
  return (
    <div className="exercise-phase">
      <h4>{title}</h4>
      {items.map((item) => (
        <article key={item.name} className="exercise-card">
          <strong>{item.name}</strong>
          <p>{item.target}</p>
          <p>{item.guide}</p>
          <small>{item.dose} · 주의: {item.caution}</small>
        </article>
      ))}
    </div>
  );
}

export default function ResultPanel({ result }: { result: AnalyzeResponse | null }) {
  if (!result) {
    return <aside className="result-panel empty">분석 결과가 여기에 표시됩니다.</aside>;
  }

  const probabilityRows = Object.entries(result.probabilities).sort((a, b) => b[1] - a[1]);
  const featureRows = Object.entries(result.features);

  return (
    <aside className="result-panel">
      <div className="result-header">
        <span className="badge">유형 {result.body_type}</span>
        <h2>{result.body_type_name}</h2>
        <p>{result.explanations.natural_language}</p>
      </div>

      <section>
        <h3>특징값 F1~F5</h3>
        <div className="metric-grid">
          {featureRows.map(([name, value]) => (
            <div className="metric" key={name}>
              <span>{name}</span>
              <strong>{value.toFixed(3)}</strong>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3>유형별 점수/확률</h3>
        {probabilityRows.map(([label, p]) => (
          <div className="bar-row" key={label}>
            <span>{label}</span>
            <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.round(p * 100)}%` }} /></div>
            <strong>{Math.round(p * 100)}%</strong>
          </div>
        ))}
      </section>

      <section>
        <h3>주요 기여 특징</h3>
        {result.explanations.top_features.map((item) => (
          <div className="contribution" key={item.feature}>
            <strong>{item.display_name}</strong>
            <span>기여도 {item.contribution.toFixed(3)} · 값 {item.value.toFixed(3)}</span>
          </div>
        ))}
      </section>

      <section>
        <h3>추천 운동</h3>
        <ExerciseList title="Phase 1 · Release" items={result.recommendations.phase_1_release} />
        <ExerciseList title="Phase 2 · Activate" items={result.recommendations.phase_2_activate} />
        <ExerciseList title="Phase 3 · Strengthen" items={result.recommendations.phase_3_strengthen} />
        <p className="safety-note">{result.recommendations.safety_note}</p>
      </section>
    </aside>
  );
}
