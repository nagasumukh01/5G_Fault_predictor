import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.app.models.entities import TelemetryMetric, PredictionRecord
from backend.app.schemas.telemetry import TelemetryCreate

class TelemetryService:
    @staticmethod
    def record_telemetry(db: Session, data: Dict[str, Any]) -> TelemetryMetric:
        metric = TelemetryMetric(
            timestamp=data.get("timestamp") or datetime.datetime.now(),
            site_id=data["site_id"],
            cell_id=data["cell_id"],
            component_id=data["component_id"],
            rsrp_dbm=data["rsrp_dbm"],
            rsrq_db=data["rsrq_db"],
            sinr_db=data["sinr_db"],
            latency_ms=data["latency_ms"],
            packet_loss_pct=data["packet_loss_pct"],
            throughput_mbps=data["throughput_mbps"],
            connected_users=data["connected_users"],
            prb_utilization_pct=data["prb_utilization_pct"],
            cpu_utilization_pct=data["cpu_utilization_pct"],
            memory_utilization_pct=data["memory_utilization_pct"],
            availability_pct=data["availability_pct"],
            fault_type=data.get("fault_type", "NORMAL"),
            fault_severity=data.get("fault_severity", "NONE"),
            fault_active=data.get("fault_active", False),
            future_fault_within_horizon=data.get("future_fault_within_horizon", False),
            is_simulated=data.get("is_simulated", True)
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def get_latest_metrics(
        db: Session,
        site_id: Optional[str] = None,
        cell_id: Optional[str] = None,
        limit: int = 15
    ) -> List[TelemetryMetric]:
        q = db.query(TelemetryMetric)
        if site_id and site_id.upper() != "ALL":
            q = q.filter(TelemetryMetric.site_id == site_id)
        if cell_id and cell_id.upper() != "ALL":
            q = q.filter(TelemetryMetric.cell_id == cell_id)
        return q.order_by(desc(TelemetryMetric.timestamp)).limit(limit).all()

    @staticmethod
    def get_metric_history(
        db: Session,
        site_id: Optional[str] = None,
        cell_id: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[TelemetryMetric]:
        q = db.query(TelemetryMetric)
        if site_id and site_id.upper() != "ALL":
            q = q.filter(TelemetryMetric.site_id == site_id)
        if cell_id and cell_id.upper() != "ALL":
            q = q.filter(TelemetryMetric.cell_id == cell_id)
        # Return chronological for chart plotting
        records = q.order_by(desc(TelemetryMetric.timestamp)).offset(skip).limit(limit).all()
        return list(reversed(records))

    @staticmethod
    def get_sites_summary(db: Session) -> List[Dict[str, Any]]:
        # Distinct sites
        sites = db.query(TelemetryMetric.site_id).distinct().all()
        sites_list = [s[0] for s in sites] if sites else ["SITE-01", "SITE-02", "SITE-03"]
        
        result = []
        for s in sites_list:
            cells = db.query(TelemetryMetric.cell_id).filter(TelemetryMetric.site_id == s).distinct().all()
            cells_list = [c[0] for c in cells] if cells else ["CELL-01", "CELL-02"]
            
            # Check latest health
            latest = db.query(TelemetryMetric).filter(TelemetryMetric.site_id == s).order_by(desc(TelemetryMetric.timestamp)).first()
            status = "DEGRADED" if (latest and latest.fault_active) else "HEALTHY"
            
            result.append({
                "site_id": s,
                "cell_count": len(cells_list),
                "cells": cells_list,
                "status": status
            })
        return result

    @staticmethod
    def get_cells_summary(db: Session, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        q = db.query(TelemetryMetric.site_id, TelemetryMetric.cell_id).distinct()
        if site_id and site_id.upper() != "ALL":
            q = q.filter(TelemetryMetric.site_id == site_id)
        
        pairs = q.all()
        if not pairs:
            pairs = [("SITE-01", "CELL-01"), ("SITE-01", "CELL-02"), ("SITE-02", "CELL-01")]

        result = []
        for s, c in pairs:
            comps = db.query(TelemetryMetric.component_id).filter(
                TelemetryMetric.site_id == s, TelemetryMetric.cell_id == c
            ).distinct().all()
            comp_list = [comp[0] for comp in comps] if comps else ["gNodeB-CU", "RU-RadioUnit"]
            
            latest = db.query(TelemetryMetric).filter(
                TelemetryMetric.site_id == s, TelemetryMetric.cell_id == c
            ).order_by(desc(TelemetryMetric.timestamp)).first()

            status = "CRITICAL" if (latest and latest.fault_severity == "CRITICAL") else (
                "WARNING" if (latest and latest.fault_active) else "NOMINAL"
            )

            result.append({
                "site_id": s,
                "cell_id": c,
                "components": comp_list,
                "status": status,
                "latest_rsrp": latest.rsrp_dbm if latest else -82.0,
                "latest_sinr": latest.sinr_db if latest else 21.0,
                "latest_throughput": latest.throughput_mbps if latest else 540.0
            })
        return result

telemetry_service = TelemetryService()
