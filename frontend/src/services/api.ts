import axios from 'axios';
import {
  TelemetryMetric,
  PredictionRecord,
  AlertRecord,
  SiteInfo,
  CellInfo,
  SimulatorStatus,
  ModelMetrics
} from '../types';

const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_URL) || '';
const API_V1 = `${API_BASE_URL}/api/v1`;

const client = axios.create({
  baseURL: API_V1,
  timeout: 10000,
});

export const api = {
  // Health
  getHealth: async () => {
    const res = await axios.get(`${API_BASE_URL}/health`);
    return res.data;
  },

  // Telemetry Metrics
  getLatestMetrics: async (siteId?: string, cellId?: string, limit = 15): Promise<TelemetryMetric[]> => {
    const params: Record<string, any> = { limit };
    if (siteId && siteId !== 'ALL') params.site_id = siteId;
    if (cellId && cellId !== 'ALL') params.cell_id = cellId;
    const res = await client.get('/metrics/latest', { params });
    return res.data;
  },

  getMetricHistory: async (siteId?: string, cellId?: string, limit = 60): Promise<TelemetryMetric[]> => {
    const params: Record<string, any> = { limit };
    if (siteId && siteId !== 'ALL') params.site_id = siteId;
    if (cellId && cellId !== 'ALL') params.cell_id = cellId;
    const res = await client.get('/metrics/history', { params });
    return res.data;
  },

  getSites: async (): Promise<SiteInfo[]> => {
    const res = await client.get('/sites');
    return res.data;
  },

  getCells: async (siteId?: string): Promise<CellInfo[]> => {
    const params: Record<string, any> = {};
    if (siteId && siteId !== 'ALL') params.site_id = siteId;
    const res = await client.get('/cells', { params });
    return res.data;
  },

  // Predictions
  getLatestPredictions: async (siteId?: string, cellId?: string, limit = 20): Promise<PredictionRecord[]> => {
    const params: Record<string, any> = { limit };
    if (siteId && siteId !== 'ALL') params.site_id = siteId;
    if (cellId && cellId !== 'ALL') params.cell_id = cellId;
    const res = await client.get('/predictions/latest', { params });
    return res.data;
  },

  getPredictionHistory: async (siteId?: string, cellId?: string, limit = 80): Promise<PredictionRecord[]> => {
    const params: Record<string, any> = { limit };
    if (siteId && siteId !== 'ALL') params.site_id = siteId;
    if (cellId && cellId !== 'ALL') params.cell_id = cellId;
    const res = await client.get('/predictions/history', { params });
    return res.data;
  },

  runPrediction: async (data?: { site_id?: string; cell_id?: string; component_id?: string; telemetry_data?: any }) => {
    const res = await client.post('/predictions/run', data || {});
    return res.data;
  },

  // Alerts
  getAlerts: async (filters?: { status?: string; severity?: string; site_id?: string; cell_id?: string; limit?: number }): Promise<AlertRecord[]> => {
    const params: Record<string, any> = { limit: filters?.limit || 50 };
    if (filters?.status && filters.status !== 'ALL') params.status = filters.status;
    if (filters?.severity && filters.severity !== 'ALL') params.severity = filters.severity;
    if (filters?.site_id && filters.site_id !== 'ALL') params.site_id = filters.site_id;
    if (filters?.cell_id && filters.cell_id !== 'ALL') params.cell_id = filters.cell_id;
    const res = await client.get('/alerts', { params });
    return res.data;
  },

  getAlertById: async (alertId: string): Promise<AlertRecord> => {
    const res = await client.get(`/alerts/${alertId}`);
    return res.data;
  },

  acknowledgeAlert: async (alertId: string, operatorName = 'NOC Engineer', notes?: string): Promise<AlertRecord> => {
    const res = await client.post(`/alerts/${alertId}/acknowledge`, { operator_name: operatorName, notes });
    return res.data;
  },

  resolveAlert: async (alertId: string, operatorName = 'NOC Engineer', resolutionNotes = 'Mitigation executed'): Promise<AlertRecord> => {
    const res = await client.post(`/alerts/${alertId}/resolve`, {
      operator_name: operatorName,
      resolution_notes: resolutionNotes
    });
    return res.data;
  },

  // Models
  getModelStatus: async () => {
    const res = await client.get('/models/status');
    return res.data;
  },

  getModelMetrics: async (): Promise<ModelMetrics> => {
    const res = await client.get('/models/metrics');
    return res.data;
  },

  // Simulator
  getSimulatorStatus: async (): Promise<SimulatorStatus> => {
    const res = await client.get('/simulator/status');
    return res.data;
  },

  startSimulator: async () => {
    const res = await client.post('/simulator/start');
    return res.data;
  },

  stopSimulator: async () => {
    const res = await client.post('/simulator/stop');
    return res.data;
  },

  triggerScenario: async (scenario: {
    scenario_type: string;
    target_site: string;
    target_cell: string;
    target_component: string;
    duration_seconds: number;
    severity: string;
  }) => {
    const res = await client.post('/simulator/scenario', scenario);
    return res.data;
  }
};
