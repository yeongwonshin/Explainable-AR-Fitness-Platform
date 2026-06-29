import type { AnalyzeResponse, LandmarkView } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function analyzeLandmarks(views: LandmarkView[], userId = 'mobile-user'): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze/landmarks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, views })
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Analysis failed: ${response.status} ${errorBody}`);
  }
  return response.json();
}
