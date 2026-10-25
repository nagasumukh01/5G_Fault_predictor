import time
import uuid
import datetime
from typing import Dict, Any, Optional

class ONAPVESAdapter:
    """
    ONAP Virtual Event Streaming (VES) Adapter Mock.
    Translates 5G telemetry anomalies and ML predictions into 3GPP-standard VES Fault Events
    suitable for ingestion by ONAP DCAE (Data Collection, Analytics, and Events).
    """
    def __init__(self, ves_endpoint_url: Optional[str] = None):
        self.ves_endpoint_url = ves_endpoint_url or "http://localhost:8080/eventListener/v7"
        self.published_events_history = []

    def format_ves_fault_event(
        self,
        alert_id: str,
        site_id: str,
        cell_id: str,
        component_id: str,
        severity: str,
        fault_type: str,
        risk_score: float,
        metrics_snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Builds standard ONAP VES 7.2 commonEventHeader + faultFields structure.
        """
        now = datetime.datetime.utcnow()
        epoch_ms = int(now.timestamp() * 1000)

        ves_severity = "CRITICAL" if severity == "CRITICAL" else "WARNING"
        source_name = f"{site_id}_{cell_id}_{component_id}"

        event = {
            "event": {
                "commonEventHeader": {
                    "version": "4.1",
                    "vesEventListenerVersion": "7.2.1",
                    "domain": "fault",
                    "eventId": f"VES_{alert_id}_{uuid.uuid4().hex[:6]}",
                    "eventName": f"Fault_{component_id}_{fault_type}",
                    "sourceName": source_name,
                    "reportingEntityName": "Team-Dynamites-AI-Predictor",
                    "priority": "High" if ves_severity == "CRITICAL" else "Medium",
                    "startEpochMicrosec": epoch_ms * 1000,
                    "lastEpochMicrosec": epoch_ms * 1000,
                    "sequence": len(self.published_events_history) + 1
                },
                "faultFields": {
                    "faultFieldsVersion": "4.0",
                    "alarmCondition": fault_type.upper(),
                    "eventSeverity": ves_severity,
                    "eventSourceType": "5G-RAN-Core",
                    "specificProblem": f"AI predicted imminent {fault_type} failure with risk score {risk_score:.2f}",
                    "alarmInterfaceA": component_id,
                    "alarmAdditionalInformation": {
                        "predicted_risk_score": str(risk_score),
                        "rsrp_dbm": str(metrics_snapshot.get("rsrp_dbm", "N/A")),
                        "latency_ms": str(metrics_snapshot.get("latency_ms", "N/A")),
                        "packet_loss_pct": str(metrics_snapshot.get("packet_loss_pct", "N/A")),
                        "ai_engine": "RandomForest + IsolationForest v1.0"
                    }
                }
            }
        }
        return event

    def dispatch_event(self, ves_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        In local mock mode, safely stores the event in memory buffer without network crash.
        """
        self.published_events_history.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": ves_event
        })
        if len(self.published_events_history) > 100:
            self.published_events_history.pop(0)

        return {
            "status": "DISPATCHED_MOCK",
            "ves_endpoint": self.ves_endpoint_url,
            "event_id": ves_event["event"]["commonEventHeader"]["eventId"]
        }

onap_adapter = ONAPVESAdapter()
