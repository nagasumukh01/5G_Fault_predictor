# System Architecture: AI-Powered Fault Prediction in 5G Testbed
**Team:** Team Dynamites  
**Version:** 1.0.0 (Production / Research Grade)

---

## 1. High-Level System Architecture

The platform architecture follows a modular, cloud-ready, event-driven design that separates data generation, collection, feature processing, machine learning inference, incident lifecycle management, and dashboard visualization.

```mermaid
graph TD
    subgraph "5G Testbed / Data Generation Layer"
        SIM[5G Telemetry Simulator]
        SCEN[Fault Scenario Injector<br/>8 Scenarios]
        O_ADAPT[ONAP VES Adapter Mock<br/>3GPP Compliant]
    end

    subgraph "Ingestion & Storage Layer"
        API_COL[Telemetry Ingestion Service]
        DB[(SQLite / PostgreSQL<br/>Time-Series Storage)]
    end

    subgraph "Feature Engineering & ML Engine"
        FE[Feature Pipeline<br/>Rolling Stats, Lags, Deltas, 5G Domain]
        RF[Random Forest<br/>Supervised Future Fault Predictor]
        LR[Logistic Regression<br/>Baseline Classifier]
        ISO[Isolation Forest<br/>Unsupervised Anomaly Detector]
        RISK[Composite Risk Scoring Engine<br/>LOW / MEDIUM / HIGH / CRITICAL]
    end

    subgraph "Backend Application Services (Render)"
        FASTAPI[FastAPI Server]
        ALERT_MGR[Incident Lifecycle Manager<br/>Normal->Warning->Critical->Resolved]
        PROM[Prometheus /metrics Exporter]
    end

    subgraph "Frontend Operations UI (Vercel)"
        REACT[React 18 + Vite + TypeScript]
        P1[1. Executive Overview]
        P2[2. Network Monitoring]
        P3[3. AI Fault Prediction]
        P4[4. Anomaly Detection]
        P5[5. Alert Center]
        P6[6. Model Evaluation]
        P7[7. 5G Simulator Controls]
        P8[8. System Health & API]
    end

    SIM --> API_COL
    SCEN --> SIM
    API_COL --> DB
    API_COL --> PROM
    DB --> FE
    FE --> RF
    FE --> LR
    FE --> ISO
    RF --> RISK
    ISO --> RISK
    RISK --> ALERT_MGR
    ALERT_MGR --> O_ADAPT
    ALERT_MGR --> DB
    FASTAPI --> DB
    FASTAPI --> RISK
    FASTAPI --> PROM
    REACT --> FASTAPI
    REACT --> P1
    REACT --> P2
    REACT --> P3
    REACT --> P4
    REACT --> P5
    REACT --> P6
    REACT --> P7
    REACT --> P8
```

---

## 2. Telemetry and ML Data-Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor NOC as NOC Engineer
    participant Sim as 5G Simulator / gNodeB
    participant API as FastAPI Backend
    participant DB as SQLite / PostgreSQL
    participant ML as ML Engine (RF + IsoForest)
    participant Alert as Alert Lifecycle Service
    participant UI as React Operations UI

    Sim->>API: Ingest multi-cell telemetry (RSRP, SINR, Latency, Loss, PRB, CPU)
    API->>DB: Store raw time-series metrics
    API->>ML: Extract rolling stats, lags, and domain interaction features
    ML->>ML: Predict future fault probability (RF) & Anomaly score (IsoForest)
    ML->>ML: Calculate composite risk score & identify top contributors
    alt Risk >= HIGH or Fault Active
        ML->>Alert: Trigger Alert (Severity: WARNING or CRITICAL)
        Alert->>DB: Deduplicate and store AlertRecord
    end
    UI->>API: Poll / WebSocket update (/metrics, /predictions, /alerts)
    API-->>UI: Return live streams & synchronized charts
    NOC->>UI: View alert and click "Acknowledge"
    UI->>API: POST /api/v1/alerts/{id}/acknowledge
    API->>DB: Update status to ACKNOWLEDGED with operator audit
    NOC->>UI: Apply mitigation and click "Resolve"
    UI->>API: POST /api/v1/alerts/{id}/resolve
    API->>DB: Update status to RESOLVED with mitigation notes
```

---

## 3. Supported 5G Network Topologies & Fault Dimensions

1. **Topology:**
   - Multi-Site: `SITE-01` (Urban Macro), `SITE-02` (Sub-Urban), `SITE-03` (Industrial Campus)
   - Multi-Cell: `CELL-01`, `CELL-02`, `CELL-03`
   - Component Hierarchy: `RU-RadioUnit`, `gNodeB-DU`, `gNodeB-CU`, `5G-Core-UPF`, `5G-Core-AMF`

2. **Fault Catalog (8 Standard 3GPP / O-RAN Scenarios):**
   - **Radio Degradation:** Severe RSRP/SINR drop, azimuth drift, or feeder fault.
   - **Cell Congestion:** Extreme PRB exhaustion and UE connection spikes.
   - **Packet Loss & Jitter:** Fronthaul/eCPRI transport frame drops.
   - **Increased Latency:** RTT delay exceeding URLLC 5G SLA boundaries.
   - **Throughput Collapse:** MIMO rank and CQI degradation under nominal load.
   - **NFVI Compute Saturation:** Containerized NF CPU/Memory thrashing.
   - **Backhaul Interruption:** N2/N3 fiber link flaps and packet loss spikes.
   - **Core Availability Degradation:** AMF/NRF signaling registration failure.
