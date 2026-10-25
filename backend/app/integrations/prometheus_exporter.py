from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

TELEMETRY_INGESTION_COUNT = Counter(
    "fiveg_telemetry_records_total",
    "Total number of 5G telemetry records ingested",
    ["site_id", "cell_id"]
)

FAULT_PREDICTIONS_COUNT = Counter(
    "fiveg_predictions_total",
    "Total number of ML predictions generated",
    ["predicted_fault", "risk_level"]
)

ACTIVE_ALERTS_GAUGE = Gauge(
    "fiveg_active_alerts_total",
    "Number of active alerts in the system",
    ["severity"]
)

NETWORK_RSRP_GAUGE = Gauge(
    "fiveg_radio_rsrp_dbm",
    "Latest RSRP signal power in dBm",
    ["site_id", "cell_id"]
)

NETWORK_THROUGHPUT_GAUGE = Gauge(
    "fiveg_user_throughput_mbps",
    "Latest 5G user plane throughput in Mbps",
    ["site_id", "cell_id"]
)

NETWORK_LATENCY_GAUGE = Gauge(
    "fiveg_transport_latency_ms",
    "Latest RTT transport latency in milliseconds",
    ["site_id", "cell_id"]
)

NETWORK_PACKET_LOSS_GAUGE = Gauge(
    "fiveg_packet_loss_pct",
    "Latest packet loss percentage",
    ["site_id", "cell_id"]
)

INFERENCE_LATENCY_HISTOGRAM = Histogram(
    "fiveg_ml_inference_duration_seconds",
    "ML inference latency in seconds"
)

def get_prometheus_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
