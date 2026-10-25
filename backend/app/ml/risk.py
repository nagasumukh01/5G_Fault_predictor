from typing import Dict, List, Any, Tuple
import numpy as np

MITIGATION_ACTIONS = {
    "radio_degradation": [
        "Adjust gNodeB remote electrical tilt (RET) and azimuth beam steering",
        "Inspect RU RF feeder cables and VSWR standing wave ratio",
        "Trigger inter-frequency handover for cell-edge UEs"
    ],
    "cell_congestion": [
        "Initiate Carrier Aggregation (CA) slice load balancing",
        "Throttle non-critical background 5G QoS flows (QFI 9 to default bearer)",
        "Dynamically adjust PRB allocation quotas for eMBB / URLLC slices"
    ],
    "packet_loss_instability": [
        "Verify Fronthaul eCPRI synchronization and jitter buffer limits",
        "Check transport layer GTP-U tunnel packet drops on N3 interface",
        "Inspect switch port error counters and MTU configuration"
    ],
    "increased_latency": [
        "Reroute user plane traffic to secondary UPF edge instance",
        "Examine transport router queuing delay and DSCP priority marking",
        "Verify gNB scheduler TTI round-robin vs proportional fair parameters"
    ],
    "throughput_degradation": [
        "Re-evaluate MIMO rank indicator and CQI channel feedback reports",
        "Check 5G Core AMF/SMF session rate limiting rules",
        "Inspect UPF throughput policing policies"
    ],
    "cpu_memory_saturation": [
        "Trigger horizontal pod autoscaling (HPA) for containerized 5G Core NFs",
        "Clear ephemeral log buffers and restart unresponsive microservices",
        "Migrate gNB DU worker pods to reserve NUMA node"
    ],
    "backhaul_interruption": [
        "Switch primary N2/N3 fiber link to redundant microwave/satellite backup",
        "Verify BGP route convergence and MPLS segment routing paths",
        "Notify transport operations center of backhaul link flap"
    ],
    "service_availability_degradation": [
        "Restart AMF/NRF registration handlers and restore SCTP associations",
        "Verify subscriber database (UDR/UDM) latency and query timeout",
        "Isolate degraded gNB sector and reroute traffic to neighbor cells"
    ],
    "NORMAL": [
        "Routine health monitoring envelope is active",
        "No mitigation required; telemetry within nominal baseline"
    ]
}

def calculate_risk(
    fault_probability: float,
    anomaly_score: float, # Raw isolation forest decision function (negative = anomalous)
    metrics_snapshot: Dict[str, Any],
    top_feature_names: List[str]
) -> Tuple[float, str, List[str]]:
    """
    Computes a composite risk score (0.0 to 1.0) and assigns an operational risk level
    (LOW, MEDIUM, HIGH, CRITICAL) along with root-cause mitigation advice.
    """
    # Normalize anomaly score: typical decision_function ranges from -0.4 (extreme anomaly) to +0.2 (very normal)
    # Map to [0, 1] where 1 is highest anomaly
    norm_anomaly = float(np.clip((0.15 - anomaly_score) / 0.50, 0.0, 1.0))

    # Metric severity modifier
    pkt_loss = float(metrics_snapshot.get("packet_loss_pct", 0.0))
    avail = float(metrics_snapshot.get("availability_pct", 100.0))
    cpu = float(metrics_snapshot.get("cpu_utilization_pct", 40.0))
    
    sev_penalty = 0.0
    if pkt_loss > 5.0 or avail < 95.0 or cpu > 90.0:
        sev_penalty += 0.25
    if pkt_loss > 20.0 or avail < 80.0:
        sev_penalty += 0.40

    composite_score = float(np.clip(
        0.55 * fault_probability + 0.30 * norm_anomaly + 0.15 * min(1.0, sev_penalty),
        0.0,
        1.0
    ))

    if composite_score >= 0.75:
        risk_level = "CRITICAL"
    elif composite_score >= 0.55:
        risk_level = "HIGH"
    elif composite_score >= 0.35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Identify mitigation actions based on top features / probable fault
    detected_type = "NORMAL"
    if any("rsrp" in f or "sinr" in f for f in top_feature_names):
        detected_type = "radio_degradation"
    elif any("prb" in f or "users" in f for f in top_feature_names):
        detected_type = "cell_congestion"
    elif any("packet_loss" in f for f in top_feature_names):
        detected_type = "packet_loss_instability"
    elif any("latency" in f for f in top_feature_names):
        detected_type = "increased_latency"
    elif any("cpu" in f or "memory" in f for f in top_feature_names):
        detected_type = "cpu_memory_saturation"
    elif any("throughput" in f for f in top_feature_names):
        detected_type = "throughput_degradation"
    elif any("availability" in f for f in top_feature_names):
        detected_type = "service_availability_degradation"

    actions = MITIGATION_ACTIONS.get(detected_type, MITIGATION_ACTIONS["NORMAL"])
    return round(composite_score, 4), risk_level, actions
