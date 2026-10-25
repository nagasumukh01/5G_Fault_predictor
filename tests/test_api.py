import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "Team Dynamites" in data["team"]

def test_prometheus_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "fiveg_" in res.text

def test_get_metrics_endpoints(client):
    res = client.get("/api/v1/metrics/latest?limit=5")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_sites_and_cells(client):
    res_sites = client.get("/api/v1/sites")
    assert res_sites.status_code == 200
    assert len(res_sites.json()) > 0

    res_cells = client.get("/api/v1/cells")
    assert res_cells.status_code == 200
    assert len(res_cells.json()) > 0

def test_model_status_and_metrics(client):
    res_status = client.get("/api/v1/models/status")
    assert res_status.status_code == 200
    assert res_status.json()["is_trained"] is True

    res_metrics = client.get("/api/v1/models/metrics")
    assert res_metrics.status_code == 200
    data = res_metrics.json()
    assert "evaluation_metrics" in data
    assert data["evaluation_metrics"]["precision"] > 0.90

def test_simulator_scenario_trigger(client):
    payload = {
        "scenario_type": "cell_congestion",
        "target_site": "SITE-01",
        "target_cell": "CELL-01",
        "target_component": "gNodeB-CU",
        "duration_seconds": 30,
        "severity": "CRITICAL"
    }
    res = client.post("/api/v1/simulator/scenario", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ACTIVE"
