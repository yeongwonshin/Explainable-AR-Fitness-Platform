export type ViewName = 'front' | 'left' | 'right' | 'back';

export interface Landmark {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export interface LandmarkView {
  view: ViewName;
  landmarks: Landmark[];
}

export interface FeatureContribution {
  feature: string;
  display_name: string;
  contribution: number;
  value: number;
  direction: 'increase' | 'decrease' | 'neutral';
}

export interface ExerciseItem {
  name: string;
  target: string;
  guide: string;
  dose: string;
  caution: string;
}

export interface AnalyzeResponse {
  user_id?: string;
  features: Record<string, number>;
  feature_quality: Record<string, number | string>;
  body_type: 'A' | 'B' | 'C' | 'D';
  body_type_name: string;
  probabilities: Record<string, number>;
  explanations: {
    method: string;
    top_features: FeatureContribution[];
    natural_language: string;
  };
  recommendations: {
    phase_1_release: ExerciseItem[];
    phase_2_activate: ExerciseItem[];
    phase_3_strengthen: ExerciseItem[];
    safety_note: string;
  };
}
