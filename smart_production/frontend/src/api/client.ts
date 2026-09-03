import axios from 'axios';

const configuredApiUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export const api = axios.create({
  // Local development uses Vite's /api proxy. Production must provide the
  // deployed FastAPI origin through VITE_API_URL.
  baseURL: `${configuredApiUrl}/api`,
});

export interface Machine {
  id: number;
  machine_code: string;
  display_name: string;
  machine_type: string | null;
  location: string | null;
  installed_at: string;
}

export interface SensorReading {
  id: number;
  machine_id: number;
  timestamp: string;
  temperature: number;
  pressure: number;
  operating_time: number;
  output_rate: number;
  fault_flag: boolean;
  fault_type: string;
  ml_risk_score: number;
}

export interface Alert {
  id: number;
  machine_id: number;
  created_at: string;
  severity: 'r' | 'o' | 'g';
  message: string;
  acknowledged: boolean;
}

export interface KPISummary {
  oee: number;
  production_today: number;
  downtime_hours_today: number;
  machine_health_pct: number;
  active_alarms: number;
  quality_rate: number;
  energy_kwh_today: number;
}

export interface PredictionResponse {
  risk_score: number;
  risk_label: 'low' | 'medium' | 'high';
  predicted_fault_type: string | null;
}

export const getMachines = () => api.get<Machine[]>('/machines/').then(r => r.data);
export const getReadings = (params?: { machine_id?: number; limit?: number }) =>
  api.get<SensorReading[]>('/sensor-readings/', { params }).then(r => r.data);
export const getAlerts = (unacknowledgedOnly = false) =>
  api.get<Alert[]>('/alerts/', { params: { unacknowledged_only: unacknowledgedOnly } }).then(r => r.data);
export const acknowledgeAlert = (id: number) =>
  api.post<Alert>(`/alerts/${id}/acknowledge`).then(r => r.data);
export const getKPIs = () => api.get<KPISummary>('/dashboard/kpis').then(r => r.data);
export const predictRisk = (features: {
  temperature: number; pressure: number; operating_time: number; output_rate: number;
}) => api.post<PredictionResponse>('/predict/', features).then(r => r.data);
