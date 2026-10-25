import pytest
from backend.app.ml.risk import calculate_risk

def test_risk_scoring_nominal():
    prob = 0.05
    anomaly = 0.12 # Normal
    metrics = {"packet_loss_pct": 0.05, "availability_pct": 99.98}
    score, level, actions = calculate_risk(prob, anomaly, metrics, ["latency_ms"])
    assert 0.0 <= score <= 1.0
    assert level == "LOW"
    assert len(actions) > 0

def test_risk_scoring_critical():
    prob = 0.95
    anomaly = -0.25 # Highly anomalous
    metrics = {"packet_loss_pct": 18.5, "availability_pct": 65.0}
    score, level, actions = calculate_risk(prob, anomaly, metrics, ["rsrp_dbm", "sinr_db"])
    assert score >= 0.70
    assert level == "CRITICAL"
    assert "Adjust gNodeB remote electrical tilt" in actions[0]
