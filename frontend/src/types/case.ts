export interface LastKnownActivity {
  timestamp: string;
  channel: string;
  amount: number;
  recipient_account_id?: string;
  latitude: number;
  longitude: number;
}

export interface Case {
  id: number;
  case_id: string;
  case_status: 'NEW' | 'ANALYZING' | 'PREDICTION_READY' | 'UNDER_REVIEW' | 'MONITORED' | 'RESOLVED';
  fraud_type: string;
  fraud_amount: number;
  complaint_time?: string;
  prediction_time?: string;
  prediction_window_hours: number;
  prediction_status: 'PENDING' | 'COMPLETED';
  state: string;
  district: string;
  victim_latitude?: number;
  victim_longitude?: number;
  last_activity_channel?: string;
  last_activity_amount?: number;
  last_activity_latitude?: number;
  last_activity_longitude?: number;
  latest_prediction_id?: string;
  risk_level?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  created_at?: string;
  updated_at?: string;
}
