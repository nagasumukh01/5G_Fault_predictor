import pytest
import pandas as pd
import numpy as np
from backend.app.ml.features import FeatureEngineer, FEATURE_COLUMNS
from backend.app.simulator.generator import NetworkTelemetrySimulator

def test_feature_engineering_extraction():
    sim = NetworkTelemetrySimulator(seed=99)
    batch = sim.generate_batch(num_steps=15, step_interval_seconds=5)
    df = pd.DataFrame(batch)
    
    fe = FeatureEngineer()
    feat_df = fe.extract_features_df(df, is_training=True)
    
    assert len(feat_df) == len(df)
    for col in FEATURE_COLUMNS:
        assert col in feat_df.columns
        assert not feat_df[col].isnull().any()

def test_single_point_feature_extraction():
    fe = FeatureEngineer()
    raw_pt = {
        "site_id": "SITE-01",
        "cell_id": "CELL-01",
        "component_id": "gNodeB-CU",
        "rsrp_dbm": -82.0,
        "rsrq_db": -9.0,
        "sinr_db": 22.0,
        "latency_ms": 11.5,
        "packet_loss_pct": 0.05,
        "throughput_mbps": 560.0,
        "connected_users": 85,
        "prb_utilization_pct": 38.0,
        "cpu_utilization_pct": 42.0,
        "memory_utilization_pct": 48.0,
        "availability_pct": 99.98
    }
    vec = fe.extract_features_single(raw_pt)
    assert vec.shape == (1, len(FEATURE_COLUMNS))
    assert not np.isnan(vec).any()
