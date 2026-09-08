import axios from 'axios';
import { Case } from '../types/case';
import { PredictionResult, ExplanationDetail, ModelInfo, ComplaintParseResponse, OutcomeCreate, OutcomeResponse } from '../types/prediction';
import { LocationItem, RiskLocation } from '../types/location';
import { Alert } from '../types/alert';
import { AnalyticsSummary } from '../types/analytics';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-User-Role': 'LEA_OFFICER'
  },
  timeout: 30000
});

export const api = {
  // Health
  async getHealth() {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Model Info & Benchmarks
  async getModelInfo(): Promise<ModelInfo> {
    const res = await apiClient.get<ModelInfo>('/model/info');
    return res.data;
  },

  // Cases
  async getCases(status?: string): Promise<Case[]> {
    const params = status ? { status } : {};
    const res = await apiClient.get<Case[]>('/cases', { params });
    return res.data;
  },

  async getCase(caseId: string): Promise<Case> {
    const res = await apiClient.get<Case>(`/cases/${encodeURIComponent(caseId)}`);
    return res.data;
  },

  // Predictions
  async runPrediction(
    caseId: string,
    topK: number = 10,
    predictionTime?: string,
    predictionWindowHours: number = 6
  ): Promise<PredictionResult> {
    const payload = {
      case_id: caseId,
      prediction_time: predictionTime,
      prediction_window_hours: predictionWindowHours,
      top_k: topK
    };
    const res = await apiClient.post<PredictionResult>('/predictions', payload);
    return res.data;
  },

  async getPrediction(predictionId: string): Promise<PredictionResult> {
    const res = await apiClient.get<PredictionResult>(`/predictions/${encodeURIComponent(predictionId)}`);
    return res.data;
  },

  async getExplanation(predictionId: string, locationId?: string): Promise<ExplanationDetail> {
    const params = locationId ? { location_id: locationId } : {};
    const res = await apiClient.get<ExplanationDetail>(`/predictions/${encodeURIComponent(predictionId)}/explanation`, { params });
    return res.data;
  },

  // Locations & GIS
  async getLocations(params?: {
    state?: string;
    district?: string;
    bank?: string;
    location_type?: string;
    limit?: number;
  }): Promise<LocationItem[]> {
    const res = await apiClient.get<LocationItem[]>('/locations', { params });
    return res.data;
  },

  async getRiskLocations(params?: {
    state?: string;
    district?: string;
    bank?: string;
    risk_level?: string;
    location_type?: string;
    prediction_id?: string;
    limit?: number;
  }): Promise<{ status: string; count: number; locations: RiskLocation[] }> {
    const res = await apiClient.get<{ status: string; count: number; locations: RiskLocation[] }>('/risk-locations', { params });
    return res.data;
  },

  // Alerts
  async getAlerts(status?: string): Promise<Alert[]> {
    const params = status ? { status } : {};
    const res = await apiClient.get<Alert[]>('/alerts', { params });
    return res.data;
  },

  async acknowledgeAlert(alertId: string, officerName: string = 'LEA_OFFICER_01'): Promise<Alert> {
    const res = await apiClient.post<Alert>(`/alerts/${encodeURIComponent(alertId)}/acknowledge`, {
      acknowledged_by: officerName
    });
    return res.data;
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsSummary> {
    const res = await apiClient.get<AnalyticsSummary>('/analytics/summary');
    return res.data;
  },

  // NLP Intake & Closed-Loop Outcome Tracking
  async parseComplaint(complaintText: string, complaintId?: string): Promise<ComplaintParseResponse> {
    const res = await apiClient.post<ComplaintParseResponse>('/cases/parse-complaint', {
      complaint_text: complaintText,
      complaint_id: complaintId
    });
    return res.data;
  },

  async createCase(caseData: Partial<Case>): Promise<Case> {
    const res = await apiClient.post<Case>('/cases', caseData);
    return res.data;
  },

  async recordOutcome(outcomeData: OutcomeCreate): Promise<OutcomeResponse> {
    const res = await apiClient.post<OutcomeResponse>('/predictions/outcome', outcomeData);
    return res.data;
  },

  async dispatchPatrol(caseId: string, payload: {
    patrol_unit: string;
    target_location_id: string;
    directives?: string;
  }): Promise<{ status: string; message: string; case: Case; dispatched_unit: string; target_location_id: string; dispatch_timestamp: string }> {
    const res = await apiClient.post(`/cases/${encodeURIComponent(caseId)}/dispatch`, payload);
    return res.data;
  }
};
