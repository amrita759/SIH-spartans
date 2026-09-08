export interface LocationItem {
  id?: number;
  location_id: string;
  location_name: string;
  location_type: 'ATM' | 'CRM' | 'BRANCH';
  bank_name: string;
  latitude: number;
  longitude: number;
  district?: string;
  state?: string;
  pincode?: string;
  population_group?: string;
}

export interface RiskLocation {
  location_id: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  rank: number;
  bank: string;
  location_type: string;
  prediction_id?: string;
  district?: string;
  state?: string;
}
