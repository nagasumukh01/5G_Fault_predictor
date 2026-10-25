import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, Text, JSON
)
from backend.app.db.session import Base

class TelemetryMetric(Base):
    __tablename__ = "telemetry_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, index=True)
    site_id = Column(String(50), index=True, nullable=False)
    cell_id = Column(String(50), index=True, nullable=False)
    component_id = Column(String(50), index=True, nullable=False)
    
    # Radio Metrics
    rsrp_dbm = Column(Float, nullable=False)           # Reference Signal Received Power (-140 to -40 dBm)
    rsrq_db = Column(Float, nullable=False)            # Reference Signal Received Quality (-20 to -3 dB)
    sinr_db = Column(Float, nullable=False)            # Signal-to-Interference-plus-Noise Ratio (-10 to 30 dB)
    
    # Transport & Network Quality
    latency_ms = Column(Float, nullable=False)         # RTT Latency in ms (5 to 150+ ms)
    packet_loss_pct = Column(Float, nullable=False)    # Packet Loss percentage (0% to 100%)
    throughput_mbps = Column(Float, nullable=False)    # User plane throughput in Mbps
    
    # Load & Capacity
    connected_users = Column(Integer, nullable=False)  # Active UE connections
    prb_utilization_pct = Column(Float, nullable=False)# Physical Resource Block utilization (0% to 100%)
    
    # Compute & Infrastructure
    cpu_utilization_pct = Column(Float, nullable=False)# NFVI CPU utilization (0% to 100%)
    memory_utilization_pct = Column(Float, nullable=False) # NFVI Memory utilization (0% to 100%)
    availability_pct = Column(Float, nullable=False)   # Service uptime availability (0% to 100%)
    
    # Ground Truth / Simulation Annotations
    fault_type = Column(String(100), default="NORMAL", index=True)
    fault_severity = Column(String(50), default="NONE")  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    fault_active = Column(Boolean, default=False)
    future_fault_within_horizon = Column(Boolean, default=False, index=True)
    is_simulated = Column(Boolean, default=True)

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, index=True)
    site_id = Column(String(50), index=True, nullable=False)
    cell_id = Column(String(50), index=True, nullable=False)
    component_id = Column(String(50), index=True, nullable=False)
    
    # Model inference results
    fault_probability = Column(Float, nullable=False)
    predicted_fault = Column(Boolean, default=False)
    fault_type = Column(String(100), default="NORMAL")
    confidence = Column(Float, default=1.0)
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    risk_level = Column(String(50), default="LOW")      # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float, default=0.0)            # 0.0 to 1.0 composite score
    
    top_contributing_features = Column(JSON, default=dict)
    lead_time_minutes = Column(Float, default=15.0)
    horizon_steps = Column(Integer, default=15)
    model_version = Column(String(50), default="v1.0-rf-iforest")

class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    site_id = Column(String(50), index=True, nullable=False)
    cell_id = Column(String(50), index=True, nullable=False)
    component_id = Column(String(50), index=True, nullable=False)
    
    severity = Column(String(50), nullable=False)      # WARNING, CRITICAL
    status = Column(String(50), default="ACTIVE", index=True) # ACTIVE, ACKNOWLEDGED, RESOLVED
    fault_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    
    risk_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    
    metrics_snapshot = Column(JSON, default=dict)
    top_features = Column(JSON, default=list)
    recommended_actions = Column(JSON, default=list)
    
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class SimulatorScenarioRecord(Base):
    __tablename__ = "simulator_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    scenario_name = Column(String(100), nullable=False)
    target_site = Column(String(50), nullable=False)
    target_cell = Column(String(50), nullable=False)
    target_component = Column(String(50), nullable=False)
    duration_seconds = Column(Integer, default=60)
    severity = Column(String(50), default="HIGH")
    is_active = Column(Boolean, default=True)
    injected_by = Column(String(100), default="Operator")
