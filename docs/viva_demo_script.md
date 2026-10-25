# Viva / Live Review Demo Script
**Project:** AI-Powered Fault Prediction in 5G Testbed  
**Team:** Team Dynamites  
**Duration:** ~5–7 Minutes

---

## 1. Introduction (30 seconds)
> *"Good morning / afternoon professors and evaluators. We are Team Dynamites, presenting our capstone research project: **AI-Powered Fault Prediction in 5G Testbed**.
> Traditional telecom operations rely on reactive threshold alarms that fire after quality-of-service has already collapsed. Our project delivers an autonomous, proactive system that leverages historical and streaming telemetry to predict network disruptions up to 22.5 minutes before SLA breaches occur, providing actionable root-cause advisories."*

---

## 2. Step-by-Step Interactive Walkthrough

### Step 1: Show System Running & Executive Overview
1. Open browser to `http://localhost:5173`.
2. Point out:
   - Live backend status badge (`API LIVE`).
   - Executive KPIs: Low Risk Level, Average Throughput (~550 Mbps), Transport Latency (~12 ms).
   - Real-time animated area chart updating every 2 seconds with simulated 5G signals.

### Step 2: Multi-Cell Network Monitoring (Page 2)
1. Navigate to **Monitoring** in the top navigation bar.
2. Select `SITE-01` -> `CELL-01`.
3. Highlight the 4 synchronized real-time telemetry charts:
   - **Radio Channel:** RSRP & SINR.
   - **Transport Stability:** RTT Latency & Packet Loss.
   - **User Plane:** Throughput & Connected UEs.
   - **Compute:** PRB utilization & NFVI CPU/Memory.

### Step 3: Inject a Controlled Fault Scenario (Page 7)
1. Navigate to **5G Simulator** in the top navigation bar.
2. Choose **Radio Signal Degradation** (or **Cell Resource Congestion**).
3. Set Target: `SITE-01` / `CELL-01`, Duration: `45s`, Severity: `CRITICAL`.
4. Click **Inject Scenario**.
5. Point out the active countdown timer showing the injected fault is live.

### Step 4: Proactive AI Prediction & Risk Radar (Page 3 & Page 4)
1. Navigate to **AI Prediction**:
   - Watch the **Fault Probability** gauge spike from nominal (<10%) to >85%!
   - Risk level transitions from `LOW` -> `CRITICAL`.
   - Point out the **Key Contributing Input Features** (e.g. `latency_rolling_mean_3`, `rsrp_lag_1`, `spectral_efficiency_proxy`).
2. Navigate to **Anomaly Detection**:
   - Show the Isolation Forest score falling below the red threshold line (`-0.05`), flagging the multi-variate outlier in the audit table.

### Step 5: Incident Command Center & Remediation (Page 5)
1. Navigate to **Alert Center**:
   - Show the newly triggered `CRITICAL` alert for `SITE-01 / CELL-01`.
   - Point out the **Recommended Remediation Actions** (e.g. *"Adjust gNodeB remote electrical tilt (RET)"* or *"Initiate Carrier Aggregation slice load balancing"*).
2. Click **Acknowledge** -> Notice state changes to `ACKNOWLEDGED`.
3. Click **Resolve** -> Type a mitigation note -> Click **Confirm Resolution** -> Notice state updates to `RESOLVED` with operator audit trail.

### Step 6: Empirical Model Evaluation & Test Results (Page 6)
1. Navigate to **Model Evaluation**:
   - Present real test-set metrics: **Precision: 99.32%**, **Recall: 100.0%**, **F1-Score: 99.66%**, **ROC-AUC: 1.000**.
   - Show the **Confusion Matrix**: 3,004 TN, 1 FP, 0 FN, 145 TP.
   - Show the **ML vs Static Threshold Benchmark**: ML F1 (99.7%) vs 3GPP Thresholds (75.0%), explaining how static rules miss early subtle degradation.

### Step 7: System Health & OpenAPI Documentation (Page 8)
1. Navigate to **System Health**:
   - Show the loaded model paths (`artifacts/models/random_forest_5g.joblib`).
   - Click the **Interactive Swagger Docs** button to show FastAPI's interactive `/docs` UI with all 16 endpoints.

---

## 3. Concluding Summary
> *"In summary, Team Dynamites has delivered an end-to-end, production-ready 5G fault prediction platform with empirical validation, full incident lifecycle, zero retraining delay, and ready for deployment on Vercel and Render. Thank you!"*
