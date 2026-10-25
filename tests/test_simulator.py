import pytest
from backend.app.simulator.generator import NetworkTelemetrySimulator

def test_simulator_nominal_generation():
    sim = NetworkTelemetrySimulator(seed=42)
    point = sim.generate_point("SITE-01", "CELL-01", "gNodeB-CU")
    
    assert point["site_id"] == "SITE-01"
    assert point["cell_id"] == "CELL-01"
    assert point["component_id"] == "gNodeB-CU"
    assert -140.0 <= point["rsrp_dbm"] <= -40.0
    assert -25.0 <= point["rsrq_db"] <= -3.0
    assert -15.0 <= point["sinr_db"] <= 35.0
    assert point["latency_ms"] > 0
    assert 0.0 <= point["packet_loss_pct"] <= 100.0
    assert point["throughput_mbps"] >= 0.0
    assert point["fault_type"] == "NORMAL"
    assert point["fault_active"] is False

def test_simulator_scenario_injection():
    sim = NetworkTelemetrySimulator(seed=42)
    scen_id = sim.trigger_scenario(
        scenario_type="radio_degradation",
        target_site="SITE-01",
        target_cell="CELL-01",
        duration_seconds=10
    )
    assert scen_id.startswith("SCEN-")
    
    point = sim.generate_point("SITE-01", "CELL-01", "gNodeB-CU")
    assert point["fault_type"] == "radio_degradation"
    assert point["fault_active"] is True
    assert point["rsrp_dbm"] < -100.0  # Degraded signal
