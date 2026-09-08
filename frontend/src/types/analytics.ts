export interface AnalyticsSummary {
  kpis: {
    total_cases: number;
    active_cases: number;
    total_predictions: number;
    total_alerts: number;
    new_alerts: number;
    mean_lead_time_hours: number;
  };
  risk_distribution: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  predictions_by_state: { state: string; count: number }[];
  predictions_by_district: { district: string; count: number }[];
  risk_by_bank: { bank: string; count: number; avg_risk: number }[];
  location_type_distribution: { type: string; count: number }[];
  model_performance: {
    pr_auc: number;
    roc_auc: number;
    hit_at_1: number;
    hit_at_3: number;
    hit_at_5: number;
    hit_at_10: number;
    mrr: number;
    evaluated_cashout_cases: number;
  };
  model_metadata: {
    model_name: string;
    model_version: string;
    prediction_horizon_hours: number;
    total_features: number;
  };
}
