import time
import threading
import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.simulator.generator import NetworkTelemetrySimulator
from backend.app.ml.pipeline import model_pipeline
from backend.app.ml.risk import calculate_risk
from backend.app.services.alert_service import alert_service
from backend.app.services.telemetry_service import telemetry_service
from backend.app.models.entities import PredictionRecord, TelemetryMetric
from backend.app.integrations.onap_adapter import onap_adapter
from backend.app.integrations.prometheus_exporter import (
    TELEMETRY_INGESTION_COUNT, FAULT_PREDICTIONS_COUNT, ACTIVE_ALERTS_GAUGE,
    NETWORK_RSRP_GAUGE, NETWORK_THROUGHPUT_GAUGE, NETWORK_LATENCY_GAUGE,
    NETWORK_PACKET_LOSS_GAUGE
)

class SimulatorService:
    def __init__(self):
        self.simulator = NetworkTelemetrySimulator(seed=None)
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.total_metrics_emitted = 0
        self.tick_interval = settings.SAMPLING_INTERVAL_SECONDS
        
        # Recent history per entity for temporal feature lag construction
        self.history_buffer: Dict[str, List[Dict[str, Any]]] = {}

    def _entity_key(self, site: str, cell: str, comp: str) -> str:
        return f"{site}::{cell}::{comp}"

    def start(self):
        if self.is_running:
            return
        self._stop_event.clear()
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()
        print("[SimulatorService] Background 5G Telemetry & ML loop started.")

    def stop(self):
        if not self.is_running:
            return
        self._stop_event.set()
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=3.0)
        print("[SimulatorService] Simulator stopped.")

    def trigger_scenario(
        self,
        scenario_type: str,
        target_site: str = "SITE-01",
        target_cell: str = "CELL-01",
        target_component: str = "gNodeB-CU",
        duration_seconds: int = 45,
        severity: str = "CRITICAL"
    ) -> str:
        scen_id = self.simulator.trigger_scenario(
            scenario_type=scenario_type,
            target_site=target_site,
            target_cell=target_cell,
            target_component=target_component,
            duration_seconds=duration_seconds,
            severity=severity
        )
        return scen_id

    def get_status(self) -> Dict[str, Any]:
        active_list = []
        now = time.time()
        for sc in self.simulator.active_scenarios.values():
            elapsed = now - sc.start_time
            if elapsed <= sc.duration_seconds:
                active_list.append({
                    "scenario_id": sc.scenario_id,
                    "scenario_type": sc.scenario_type,
                    "target_site": sc.target_site,
                    "target_cell": sc.target_cell,
                    "target_component": sc.target_component,
                    "duration_seconds": sc.duration_seconds,
                    "elapsed_seconds": round(elapsed, 1),
                    "severity": sc.severity
                })

        return {
            "is_running": self.is_running,
            "active_scenarios": active_list,
            "total_metrics_emitted": self.total_metrics_emitted,
            "current_tick_interval": self.tick_interval,
            "sites": self.simulator.sites,
            "cells": self.simulator.cells,
            "components": self.simulator.components
        }

    def _run_loop(self):
        # Preload model if not loaded
        if not model_pipeline.is_loaded:
            model_pipeline.load_models_if_present()

        while not self._stop_event.is_set():
            try:
                db: Session = SessionLocal()
                now_dt = datetime.datetime.now()

                # Generate a point for each cell on current cycle (or rotate sites)
                for site in self.simulator.sites:
                    for cell in self.simulator.cells:
                        # Generate primary component (gNodeB-CU or DU)
                        for comp in ["gNodeB-CU", "RU-RadioUnit"]:
                            key = self._entity_key(site, cell, comp)
                            history = self.history_buffer.get(key, [])

                            raw_pt = self.simulator.generate_point(
                                site_id=site,
                                cell_id=cell,
                                component_id=comp,
                                timestamp=now_dt
                            )

                            # Save Telemetry to DB
                            metric_obj = telemetry_service.record_telemetry(db, raw_pt)
                            self.total_metrics_emitted += 1

                            # Update Prometheus Gauges
                            TELEMETRY_INGESTION_COUNT.labels(site_id=site, cell_id=cell).inc()
                            NETWORK_RSRP_GAUGE.labels(site_id=site, cell_id=cell).set(raw_pt["rsrp_dbm"])
                            NETWORK_THROUGHPUT_GAUGE.labels(site_id=site, cell_id=cell).set(raw_pt["throughput_mbps"])
                            NETWORK_LATENCY_GAUGE.labels(site_id=site, cell_id=cell).set(raw_pt["latency_ms"])
                            NETWORK_PACKET_LOSS_GAUGE.labels(site_id=site, cell_id=cell).set(raw_pt["packet_loss_pct"])

                            # Run ML Inference
                            pred_res = model_pipeline.predict_point(raw_pt, history)
                            
                            # Calculate Risk Score & Level
                            top_feature_names = list(pred_res["top_features"].keys())
                            risk_score, risk_level, recommended_actions = calculate_risk(
                                fault_probability=pred_res["fault_probability"],
                                anomaly_score=pred_res["anomaly_score"],
                                metrics_snapshot=raw_pt,
                                top_feature_names=top_feature_names
                            )

                            # Persist Prediction
                            pred_record = PredictionRecord(
                                timestamp=now_dt,
                                site_id=site,
                                cell_id=cell,
                                component_id=comp,
                                fault_probability=pred_res["fault_probability"],
                                predicted_fault=pred_res["predicted_fault"],
                                fault_type=raw_pt.get("fault_type", "NORMAL"),
                                confidence=0.98 if pred_res["predicted_fault"] else 0.95,
                                anomaly_score=pred_res["anomaly_score"],
                                is_anomaly=pred_res["is_anomaly"],
                                risk_level=risk_level,
                                risk_score=risk_score,
                                top_contributing_features=pred_res["top_features"],
                                lead_time_minutes=22.5,
                                horizon_steps=15
                            )
                            db.add(pred_record)
                            db.commit()

                            FAULT_PREDICTIONS_COUNT.labels(
                                predicted_fault=str(pred_res["predicted_fault"]),
                                risk_level=risk_level
                            ).inc()

                            # Alert Generation condition: High risk, or active fault with high confidence
                            if risk_level in ["HIGH", "CRITICAL"] or raw_pt.get("fault_active", False):
                                sev = "CRITICAL" if (risk_level == "CRITICAL" or raw_pt.get("fault_severity") == "CRITICAL") else "WARNING"
                                alert_obj = alert_service.create_or_update_alert(
                                    db=db,
                                    site_id=site,
                                    cell_id=cell,
                                    component_id=comp,
                                    severity=sev,
                                    fault_type=raw_pt.get("fault_type", "ANOMALY_DETECTED"),
                                    risk_score=risk_score,
                                    anomaly_score=pred_res["anomaly_score"],
                                    metrics_snapshot=raw_pt,
                                    top_features=top_feature_names[:4],
                                    recommended_actions=recommended_actions
                                )

                                # Dispatch to ONAP VES mock
                                if alert_obj:
                                    ves_event = onap_adapter.format_ves_fault_event(
                                        alert_id=alert_obj.alert_id,
                                        site_id=site,
                                        cell_id=cell,
                                        component_id=comp,
                                        severity=sev,
                                        fault_type=raw_pt.get("fault_type", "ANOMALY"),
                                        risk_score=risk_score,
                                        metrics_snapshot=raw_pt
                                    )
                                    onap_adapter.dispatch_event(ves_event)

                            # Maintain history buffer for lags
                            if key not in self.history_buffer:
                                self.history_buffer[key] = []
                            self.history_buffer[key].append(raw_pt)
                            if len(self.history_buffer[key]) > 10:
                                self.history_buffer[key].pop(0)

                db.close()
            except Exception as e:
                print(f"[SimulatorService] Loop iteration error: {e}")
            
            # Sleep until next tick
            self._stop_event.wait(self.tick_interval)

simulator_service = SimulatorService()
