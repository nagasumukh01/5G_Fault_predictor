import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ScenarioTriggerRequest(BaseModel):
    scenario_type: str = "radio_degradation"
    # Supported:
    # 1. radio_degradation
    # 2. cell_congestion
    # 3. packet_loss_instability
    # 4. increased_latency
    # 5. throughput_degradation
    # 6. cpu_memory_saturation
    # 7. backhaul_interruption
    # 8. service_availability_degradation
    target_site: str = "SITE-01"
    target_cell: str = "CELL-01"
    target_component: str = "gNodeB-CU"
    duration_seconds: int = 45
    severity: str = "CRITICAL" # LOW, MEDIUM, HIGH, CRITICAL

class ScenarioResponse(BaseModel):
    status: str
    scenario_id: str
    scenario_type: str
    target_site: str
    target_cell: str
    target_component: str
    duration_seconds: int
    severity: str
    message: str

class SimulatorStatusResponse(BaseModel):
    is_running: bool
    active_scenarios: List[Dict[str, Any]]
    total_metrics_emitted: int
    current_tick_interval: float
    sites: List[str]
    cells: List[str]
    components: List[str]

class ModelStatusResponse(BaseModel):
    is_trained: bool
    model_version: str
    primary_model: str
    baseline_model: str
    anomaly_detector: str
    last_trained_timestamp: Optional[str] = None
    artifacts_path: str
    features_count: int

class ModelMetricsResponse(BaseModel):
    model_name: str
    dataset_summary: Dict[str, Any]
    evaluation_metrics: Dict[str, Any]
    confusion_matrix: List[List[int]]
    baseline_comparison: Dict[str, Any]
    feature_importances: Dict[str, float]
