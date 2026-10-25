import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import AlertRecord
from backend.app.core.config import settings

class AlertService:
    @staticmethod
    def create_or_update_alert(
        db: Session,
        site_id: str,
        cell_id: str,
        component_id: str,
        severity: str,
        fault_type: str,
        risk_score: float,
        anomaly_score: float,
        metrics_snapshot: Dict[str, Any],
        top_features: List[str],
        recommended_actions: List[str]
    ) -> Optional[AlertRecord]:
        now = datetime.datetime.now()

        # Check for existing active or acknowledged alert for this target (deduplication & cooldown)
        existing = (
            db.query(AlertRecord)
            .filter(
                AlertRecord.site_id == site_id,
                AlertRecord.cell_id == cell_id,
                AlertRecord.component_id == component_id,
                AlertRecord.status.in_(["ACTIVE", "ACKNOWLEDGED"])
            )
            .order_by(AlertRecord.timestamp.desc())
            .first()
        )

        if existing:
            # Check cooldown: if updated recently, update in-place without flooding new alerts
            time_since_update = (now - existing.updated_at).total_seconds()
            if time_since_update < settings.ALERT_COOLDOWN_SECONDS:
                existing.updated_at = now
                existing.risk_score = risk_score
                existing.anomaly_score = anomaly_score
                existing.metrics_snapshot = metrics_snapshot
                db.commit()
                db.refresh(existing)
                return existing

        # Create new alert
        alert_id = f"ALT-{site_id}-{cell_id}-{int(now.timestamp())}"
        message = (
            f"Imminent/Active {fault_type.replace('_', ' ').title()} predicted on {site_id}/{cell_id} "
            f"({component_id}). Risk score: {risk_score:.2f}, Anomaly: {anomaly_score:.2f}"
        )

        new_alert = AlertRecord(
            alert_id=alert_id,
            timestamp=now,
            updated_at=now,
            site_id=site_id,
            cell_id=cell_id,
            component_id=component_id,
            severity=severity,
            status="ACTIVE",
            fault_type=fault_type,
            message=message,
            risk_score=risk_score,
            anomaly_score=anomaly_score,
            metrics_snapshot=metrics_snapshot,
            top_features=top_features,
            recommended_actions=recommended_actions
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        return new_alert

    @staticmethod
    def get_alerts(
        db: Session,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        site_id: Optional[str] = None,
        cell_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[AlertRecord]:
        q = db.query(AlertRecord)
        if status and status.upper() != "ALL":
            q = q.filter(AlertRecord.status == status.upper())
        if severity and severity.upper() != "ALL":
            q = q.filter(AlertRecord.severity == severity.upper())
        if site_id and site_id.upper() != "ALL":
            q = q.filter(AlertRecord.site_id == site_id)
        if cell_id and cell_id.upper() != "ALL":
            q = q.filter(AlertRecord.cell_id == cell_id)
        return q.order_by(AlertRecord.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: str) -> Optional[AlertRecord]:
        return db.query(AlertRecord).filter(
            (AlertRecord.alert_id == alert_id) | (AlertRecord.id == int(alert_id) if alert_id.isdigit() else False)
        ).first()

    @staticmethod
    def acknowledge_alert(
        db: Session,
        alert_id: str,
        operator_name: str = "NOC Engineer",
        notes: Optional[str] = None
    ) -> Optional[AlertRecord]:
        alert = AlertService.get_alert_by_id(db, alert_id)
        if not alert:
            return None
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_by = operator_name
        alert.acknowledged_at = datetime.datetime.now()
        alert.updated_at = datetime.datetime.now()
        if notes:
            alert.resolution_notes = f"[ACK: {notes}]"
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def resolve_alert(
        db: Session,
        alert_id: str,
        operator_name: str = "NOC Engineer",
        resolution_notes: str = "Resolved via mitigation action"
    ) -> Optional[AlertRecord]:
        alert = AlertService.get_alert_by_id(db, alert_id)
        if not alert:
            return None
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.datetime.now()
        alert.updated_at = datetime.datetime.now()
        existing_notes = alert.resolution_notes or ""
        alert.resolution_notes = f"{existing_notes} [RESOLVED by {operator_name}: {resolution_notes}]".strip()
        db.commit()
        db.refresh(alert)
        return alert

alert_service = AlertService()
