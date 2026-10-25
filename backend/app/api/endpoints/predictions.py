import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.models.entities import PredictionRecord, TelemetryMetric
from backend.app.schemas.prediction import PredictionResponse, RunPredictionRequest, RunPredictionResponse
from backend.app.ml.pipeline import model_pipeline
from backend.app.ml.risk import calculate_risk

router = APIRouter()

@router.get("/predictions/latest", response_model=List[PredictionResponse])
def get_latest_predictions(
    site_id: Optional[str] = Query(None),
    cell_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(PredictionRecord)
    if site_id and site_id.upper() != "ALL":
        q = q.filter(PredictionRecord.site_id == site_id)
    if cell_id and cell_id.upper() != "ALL":
        q = q.filter(PredictionRecord.cell_id == cell_id)
    return q.order_by(desc(PredictionRecord.timestamp)).limit(limit).all()

@router.get("/predictions/history", response_model=List[PredictionResponse])
def get_predictions_history(
    site_id: Optional[str] = Query(None),
    cell_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=5, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(PredictionRecord)
    if site_id and site_id.upper() != "ALL":
        q = q.filter(PredictionRecord.site_id == site_id)
    if cell_id and cell_id.upper() != "ALL":
        q = q.filter(PredictionRecord.cell_id == cell_id)
    records = q.order_by(desc(PredictionRecord.timestamp)).offset(skip).limit(limit).all()
    return list(reversed(records))

@router.post("/predictions/run", response_model=RunPredictionResponse)
def run_ad_hoc_prediction(
    req: RunPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Execute on-demand model inference on latest database point or user-supplied custom telemetry.
    """
    site_id = req.site_id or "SITE-01"
    cell_id = req.cell_id or "CELL-01"
    component_id = req.component_id or "gNodeB-CU"

    if req.telemetry_data:
        raw_point = req.telemetry_data
        raw_point.setdefault("site_id", site_id)
        raw_point.setdefault("cell_id", cell_id)
        raw_point.setdefault("component_id", component_id)
    else:
        # Fetch latest point from DB
        latest_m = (
            db.query(TelemetryMetric)
            .filter(TelemetryMetric.site_id == site_id, TelemetryMetric.cell_id == cell_id)
            .order_by(desc(TelemetryMetric.timestamp))
            .first()
        )
        if latest_m:
            raw_point = {
                "site_id": latest_m.site_id,
                "cell_id": latest_m.cell_id,
                "component_id": latest_m.component_id,
                "rsrp_dbm": latest_m.rsrp_dbm,
                "rsrq_db": latest_m.rsrq_db,
                "sinr_db": latest_m.sinr_db,
                "latency_ms": latest_m.latency_ms,
                "packet_loss_pct": latest_m.packet_loss_pct,
                "throughput_mbps": latest_m.throughput_mbps,
                "connected_users": latest_m.connected_users,
                "prb_utilization_pct": latest_m.prb_utilization_pct,
                "cpu_utilization_pct": latest_m.cpu_utilization_pct,
                "memory_utilization_pct": latest_m.memory_utilization_pct,
                "availability_pct": latest_m.availability_pct,
                "fault_type": latest_m.fault_type
            }
        else:
            raw_point = {
                "site_id": site_id,
                "cell_id": cell_id,
                "component_id": component_id,
                "rsrp_dbm": -82.0,
                "rsrq_db": -9.0,
                "sinr_db": 22.0,
                "latency_ms": 11.5,
                "packet_loss_pct": 0.05,
                "throughput_mbps": 560.0,
                "connected_users": 85,
                "prb_utilization_pct": 38.0,
                "cpu_utilization_pct": 42.0,
                "memory_utilization_pct": 48.0,
                "availability_pct": 99.98,
                "fault_type": "NORMAL"
            }

    pred_res = model_pipeline.predict_point(raw_point)
    risk_score, risk_level, _ = calculate_risk(
        fault_probability=pred_res["fault_probability"],
        anomaly_score=pred_res["anomaly_score"],
        metrics_snapshot=raw_point,
        top_feature_names=list(pred_res["top_features"].keys())
    )

    pred_rec = PredictionRecord(
        timestamp=datetime.datetime.now(),
        site_id=site_id,
        cell_id=cell_id,
        component_id=component_id,
        fault_probability=pred_res["fault_probability"],
        predicted_fault=pred_res["predicted_fault"],
        fault_type=raw_point.get("fault_type", "NORMAL"),
        confidence=0.98 if pred_res["predicted_fault"] else 0.95,
        anomaly_score=pred_res["anomaly_score"],
        is_anomaly=pred_res["is_anomaly"],
        risk_level=risk_level,
        risk_score=risk_score,
        top_contributing_features=pred_res["top_features"],
        lead_time_minutes=22.5,
        horizon_steps=15
    )
    db.add(pred_rec)
    db.commit()
    db.refresh(pred_rec)

    return RunPredictionResponse(
        status="SUCCESS",
        prediction=pred_rec,
        message=f"Prediction executed: Fault Prob={pred_res['fault_probability']:.2f}, Risk={risk_level}"
    )
