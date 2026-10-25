import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class TelemetryBase(BaseModel):
    timestamp: Optional[datetime.datetime] = None
    site_id: str
    cell_id: str
    component_id: str
    rsrp_dbm: float
    rsrq_db: float
    sinr_db: float
    latency_ms: float
    packet_loss_pct: float
    throughput_mbps: float
    connected_users: int
    prb_utilization_pct: float
    cpu_utilization_pct: float
    memory_utilization_pct: float
    availability_pct: float
    fault_type: Optional[str] = "NORMAL"
    fault_severity: Optional[str] = "NONE"
    fault_active: Optional[bool] = False
    future_fault_within_horizon: Optional[bool] = False
    is_simulated: Optional[bool] = True

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryResponse(TelemetryBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class MetricHistoryResponse(BaseModel):
    total: int
    site_id: Optional[str] = None
    cell_id: Optional[str] = None
    metrics: List[TelemetryResponse]

class SiteInfo(BaseModel):
    site_id: str
    cell_count: int
    cells: List[str]
    status: str

class CellInfo(BaseModel):
    site_id: str
    cell_id: str
    components: List[str]
    status: str
    latest_rsrp: Optional[float] = None
    latest_sinr: Optional[float] = None
    latest_throughput: Optional[float] = None
