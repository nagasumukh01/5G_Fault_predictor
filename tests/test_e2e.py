import pytest
import time
from fastapi.testclient import TestClient
from backend.app.main import app

def test_full_e2e_flow():
    with TestClient(app) as client:
        # 1. Health check
        h_res = client.get("/health")
        assert h_res.status_code == 200

        # 2. Inject fault scenario
        scen_res = client.post("/api/v1/simulator/scenario", json={
            "scenario_type": "radio_degradation",
            "target_site": "SITE-01",
            "target_cell": "CELL-01",
            "target_component": "gNodeB-CU",
            "duration_seconds": 45,
            "severity": "CRITICAL"
        })
        assert scen_res.status_code == 200
        scen_data = scen_res.json()
        assert scen_data["status"] == "ACTIVE"

        # 3. Trigger ad-hoc prediction on the degraded condition
        pred_res = client.post("/api/v1/predictions/run", json={
            "site_id": "SITE-01",
            "cell_id": "CELL-01",
            "component_id": "gNodeB-CU",
            "telemetry_data": {
                "rsrp_dbm": -128.0,
                "rsrq_db": -18.5,
                "sinr_db": -4.2,
                "latency_ms": 65.0,
                "packet_loss_pct": 5.5,
                "throughput_mbps": 45.0,
                "connected_users": 65,
                "prb_utilization_pct": 45.0,
                "cpu_utilization_pct": 55.0,
                "memory_utilization_pct": 50.0,
                "availability_pct": 98.0,
                "fault_type": "radio_degradation"
            }
        })
        assert pred_res.status_code == 200
        pred_data = pred_res.json()
        assert pred_data["status"] == "SUCCESS"
        assert pred_data["prediction"]["fault_probability"] > 0.40

        # 4. Fetch alerts
        alerts_res = client.get("/api/v1/alerts")
        assert alerts_res.status_code == 200
        alerts = alerts_res.json()

        # If an active alert exists, test acknowledge and resolve
        if alerts:
            target_alert = alerts[0]
            alert_id = target_alert["alert_id"]

            if target_alert["status"] == "ACTIVE":
                ack_res = client.post(f"/api/v1/alerts/{alert_id}/acknowledge", json={
                    "operator_name": "E2E Automated Tester",
                    "notes": "Acknowledged in test"
                })
                assert ack_res.status_code == 200
                assert ack_res.json()["status"] == "ACKNOWLEDGED"

            resolve_res = client.post(f"/api/v1/alerts/{alert_id}/resolve", json={
                "operator_name": "E2E Automated Tester",
                "resolution_notes": "Antenna azimuth calibrated successfully"
            })
            assert resolve_res.status_code == 200
            assert resolve_res.json()["status"] == "RESOLVED"
