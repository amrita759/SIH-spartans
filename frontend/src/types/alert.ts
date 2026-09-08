export interface Alert {
  id: number;
  alert_id: string;
  case_id: string;
  prediction_id: string;
  location_id: string;
  location_name?: string;
  bank_name?: string;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  rank: number;
  message?: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'UNDER_REVIEW' | 'RESOLVED';
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at?: string;
}
