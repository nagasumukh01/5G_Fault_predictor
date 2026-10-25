from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.schemas.alert import AlertResponse, AlertAcknowledgeRequest, AlertResolveRequest
from backend.app.services.alert_service import alert_service

router = APIRouter()

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, ACKNOWLEDGED, RESOLVED, or ALL"),
    severity: Optional[str] = Query(None, description="Filter by severity: WARNING, CRITICAL, or ALL"),
    site_id: Optional[str] = Query(None),
    cell_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return alert_service.get_alerts(
        db, status=status, severity=severity, site_id=site_id, cell_id=cell_id, limit=limit, skip=skip
    )

@router.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(
    alert_id: str,
    db: Session = Depends(get_db)
):
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert

@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    body: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    alert = alert_service.acknowledge_alert(
        db, alert_id=alert_id, operator_name=body.operator_name, notes=body.notes
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert

@router.post("/alerts/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    body: AlertResolveRequest,
    db: Session = Depends(get_db)
):
    alert = alert_service.resolve_alert(
        db, alert_id=alert_id, operator_name=body.operator_name, resolution_notes=body.resolution_notes
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert
