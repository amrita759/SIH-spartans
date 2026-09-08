export interface ExplanationFactor {
  feature: string;
  contribution: number;
  impact: string; // "INCREASES_RISK" | "DECREASES_RISK"
  description: string;
}

export interface RankedLocation {
  rank: number;
  location_id: string;
  location_name: string;
  location_type: 'ATM' | 'CRM' | 'BRANCH';
  bank_name: string;
  latitude: number;
  longitude: number;
  district: string;
  state: string;
  model_score: number;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  top_factors: ExplanationFactor[];
}

export interface PredictionResult {
  prediction_id: string;
  case_id: string;
  prediction_time: string;
  prediction_window_hours: number;
  model_version: string;
  total_candidates_scored: number;
  urgency_level?: string;
  remaining_hours?: number;
  locations: RankedLocation[];
}

export interface ComplaintParseResponse {
  complaint_id: string;
  detected_fraud_type: string;
  detected_channel: string;
  detected_amount: number;
  detected_state: string;
  detected_district: string;
  detected_bank?: string;
  key_entities: string[];
  suggested_latitude: number;
  suggested_longitude: number;
  raw_text: string;
}

export interface OutcomeCreate {
  case_id: string;
  prediction_id: string;
  actual_location_id: string;
  actual_withdrawal_time?: string;
  withdrawal_occurred?: boolean;
  apprehended?: boolean;
  notes?: string;
}

export interface OutcomeResponse {
  status: string;
  message: string;
  outcome_id: string;
  case_id: string;
  prediction_id: string;
  actual_location_id: string;
  rank_of_actual?: number;
  in_top_3: boolean;
  in_top_5: boolean;
  in_top_10: boolean;
  lead_time_hours?: number;
  prediction_risk_score?: number;
}

export interface ExplanationDetail {
  prediction_id: string;
  location_id: string;
  risk_score: number;
  risk_level: string;
  top_factors: {
    feature: string;
    impact: number;
    direction: string;
    description: string;
  }[];
}

export interface ModelInfo {
  model_name: string;
  model_version: string;
  prediction_horizon_hours: number;
  supported_windows: number[];
  total_features: number;
  feature_names: string[];
  created_at: string;
  metrics_summary: {
    pr_auc: number;
    roc_auc: number;
    hit_at_1: number;
    hit_at_3: number;
    hit_at_5: number;
    hit_at_10: number;
    mrr: number;
    evaluated_cashout_cases: number;
  };
}
