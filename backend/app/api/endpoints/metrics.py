from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.schemas.telemetry import TelemetryResponse, SiteInfo, CellInfo
from backend.app.services.telemetry_service import telemetry_service

router = APIRouter()

@router.get("/metrics/latest", response_model=List[TelemetryResponse])
def get_latest_metrics(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    cell_id: Optional[str] = Query(None, description="Filter by cell ID"),
    limit: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return telemetry_service.get_latest_metrics(db, site_id=site_id, cell_id=cell_id, limit=limit)

@router.get("/metrics/history", response_model=List[TelemetryResponse])
def get_metrics_history(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    cell_id: Optional[str] = Query(None, description="Filter by cell ID"),
    limit: int = Query(60, ge=5, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return telemetry_service.get_metric_history(db, site_id=site_id, cell_id=cell_id, limit=limit, skip=skip)

@router.get("/sites", response_model=List[SiteInfo])
def get_sites(db: Session = Depends(get_db)):
    return telemetry_service.get_sites_summary(db)

@router.get("/cells", response_model=List[CellInfo])
def get_cells(
    site_id: Optional[str] = Query(None, description="Filter cells by site ID"),
    db: Session = Depends(get_db)
):
    return telemetry_service.get_cells_summary(db, site_id=site_id)
