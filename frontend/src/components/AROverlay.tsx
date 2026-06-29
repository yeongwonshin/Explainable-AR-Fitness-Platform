import { useEffect, useRef } from 'react';
import type { Landmark } from '../types';

const EDGES: Array<[number, number]> = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26]
];

interface Props {
  landmarks: Landmark[];
  width: number;
  height: number;
  guideText?: string;
}

export default function AROverlay({ landmarks, width, height, guideText }: Props) {
  const ref = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);
    ctx.lineWidth = 3;
    ctx.strokeStyle = 'rgba(56,189,248,0.95)';
    ctx.fillStyle = 'rgba(16,185,129,0.95)';

    for (const [a, b] of EDGES) {
      const p1 = landmarks[a];
      const p2 = landmarks[b];
      if (!p1 || !p2 || (p1.visibility ?? 1) < 0.5 || (p2.visibility ?? 1) < 0.5) continue;
      ctx.beginPath();
      ctx.moveTo(p1.x * width, p1.y * height);
      ctx.lineTo(p2.x * width, p2.y * height);
      ctx.stroke();
    }

    for (const p of landmarks) {
      if (!p || (p.visibility ?? 1) < 0.5) continue;
      ctx.beginPath();
      ctx.arc(p.x * width, p.y * height, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.strokeStyle = 'rgba(255,255,255,0.75)';
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.stroke();
    ctx.setLineDash([]);
  }, [landmarks, width, height]);

  return (
    <>
      <canvas ref={ref} width={width} height={height} className="ar-canvas" />
      {guideText && <div className="ar-guide">{guideText}</div>}
    </>
  );
}
