import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AlertBase(BaseModel):
    alert_id: str
    site_id: str
    cell_id: str
    component_id: str
    severity: str
    status: str
    fault_type: str
    message: str
    risk_score: float
    anomaly_score: float
    metrics_snapshot: Dict[str, Any] = {}
    top_features: List[str] = []
    recommended_actions: List[str] = []
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime.datetime] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime.datetime] = None

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    operator_name: str = "NOC Engineer"
    notes: Optional[str] = "Incident acknowledged and under triage"

class AlertResolveRequest(BaseModel):
    operator_name: str = "NOC Engineer"
    resolution_notes: str = "Remediation applied. Metrics returned to nominal envelope."

class AlertFilter(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    site_id: Optional[str] = None
    cell_id: Optional[str] = None
