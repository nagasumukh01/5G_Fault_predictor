import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PredictionBase(BaseModel):
    site_id: str
    cell_id: str
    component_id: str
    fault_probability: float
    predicted_fault: bool
    fault_type: str
    confidence: float
    anomaly_score: float
    is_anomaly: bool
    risk_level: str
    risk_score: float
    top_contributing_features: Dict[str, float] = {}
    lead_time_minutes: float = 15.0
    horizon_steps: int = 15
    model_version: str = "v1.0-rf-iforest"

class PredictionResponse(PredictionBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class RunPredictionRequest(BaseModel):
    site_id: Optional[str] = None
    cell_id: Optional[str] = None
    component_id: Optional[str] = None
    telemetry_data: Optional[Dict[str, Any]] = None

class RunPredictionResponse(BaseModel):
    status: str
    prediction: PredictionResponse
    message: str
