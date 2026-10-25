import pytest
from backend.app.ml.pipeline import model_pipeline

def test_model_pipeline_loading():
    loaded = model_pipeline.load_models_if_present()
    assert loaded is True
    assert model_pipeline.rf_model is not None
    assert model_pipeline.iso_model is not None

def test_model_pipeline_inference():
    if not model_pipeline.is_loaded:
        model_pipeline.load_models_if_present()

    nominal_pt = {
        "site_id": "SITE-01",
        "cell_id": "CELL-01",
        "component_id": "gNodeB-CU",
        "rsrp_dbm": -80.0,
        "rsrq_db": -9.0,
        "sinr_db": 22.0,
        "latency_ms": 11.0,
        "packet_loss_pct": 0.02,
        "throughput_mbps": 580.0,
        "connected_users": 80,
        "prb_utilization_pct": 35.0,
        "cpu_utilization_pct": 40.0,
        "memory_utilization_pct": 45.0,
        "availability_pct": 99.98
    }
    pred = model_pipeline.predict_point(nominal_pt)
    assert "fault_probability" in pred
    assert 0.0 <= pred["fault_probability"] <= 1.0
    assert "anomaly_score" in pred
    assert "top_features" in pred
