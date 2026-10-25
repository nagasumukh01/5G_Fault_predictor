export interface TelemetryMetric {
  id: number;
  timestamp: string;
  site_id: string;
  cell_id: string;
  component_id: string;
  rsrp_dbm: number;
  rsrq_db: number;
  sinr_db: number;
  latency_ms: number;
  packet_loss_pct: number;
  throughput_mbps: number;
  connected_users: number;
  prb_utilization_pct: number;
  cpu_utilization_pct: number;
  memory_utilization_pct: number;
  availability_pct: number;
  fault_type: string;
  fault_severity: string;
  fault_active: boolean;
  future_fault_within_horizon: boolean;
  is_simulated: boolean;
}

export interface PredictionRecord {
  id: number;
  timestamp: string;
  site_id: string;
  cell_id: string;
  component_id: string;
  fault_probability: number;
  predicted_fault: boolean;
  fault_type: string;
  confidence: number;
  anomaly_score: number;
  is_anomaly: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  top_contributing_features: Record<string, number>;
  lead_time_minutes: number;
  horizon_steps: number;
  model_version: string;
}

export interface AlertRecord {
  id: number;
  alert_id: string;
  timestamp: string;
  updated_at: string;
  site_id: string;
  cell_id: string;
  component_id: string;
  severity: 'WARNING' | 'CRITICAL';
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  fault_type: string;
  message: string;
  risk_score: number;
  anomaly_score: number;
  metrics_snapshot: Record<string, any>;
  top_features: string[];
  recommended_actions: string[];
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolution_notes?: string;
  resolved_at?: string;
}

export interface SiteInfo {
  site_id: string;
  cell_count: number;
  cells: string[];
  status: string;
}

export interface CellInfo {
  site_id: string;
  cell_id: string;
  components: string[];
  status: string;
  latest_rsrp?: number;
  latest_sinr?: number;
  latest_throughput?: number;
}

export interface SimulatorStatus {
  is_running: boolean;
  active_scenarios: Array<{
    scenario_id: string;
    scenario_type: string;
    target_site: string;
    target_cell: string;
    target_component: string;
    duration_seconds: number;
    elapsed_seconds: number;
    severity: string;
  }>;
  total_metrics_emitted: number;
  current_tick_interval: number;
  sites: string[];
  cells: string[];
  components: string[];
}

export interface ModelMetrics {
  model_name: string;
  dataset_summary: {
    total_samples: number;
    train_samples: number;
    test_samples: number;
    fault_prevalence_train_pct?: number;
    fault_prevalence_test_pct?: number;
    split_strategy: string;
  };
  evaluation_metrics: {
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    false_positive_rate: number;
    missed_fault_rate: number;
    lead_time_minutes: number;
    inference_latency_ms: number;
    training_time_seconds: number;
  };
  confusion_matrix: number[][];
  baseline_comparison: Record<string, any>;
  feature_importances: Record<string, number>;
}
