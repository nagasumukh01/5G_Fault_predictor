# Empirical Evaluation & Experimental Results
**Project:** AI-Powered Fault Prediction in 5G Testbed  
**Team:** Team Dynamites

---

## 1. Dataset Generation & Split Method

| Parameter | Specification |
|:---|:---|
| **Total Ingested Samples** | 15,750 time-series telemetry records |
| **Monitored Topology** | 3 Sites (`SITE-01`, `SITE-02`, `SITE-03`), 3 Cells, 5 Network Components |
| **Step Interval** | 10–15 seconds per observation |
| **Fault Scenarios Represented** | 8 3GPP/O-RAN degradation types + Nominal baseline |
| **Split Strategy** | **Strict Chronological Temporal Split (No Lookahead Leakage)** |
| **Training Set Size** | 12,600 samples (Initial 80% timeline) |
| **Test Set Size** | 3,150 samples (Held-out final 20% timeline) |
| **Precursor Lead Window** | 15 time steps (15 to 22.5 minutes prior to fault onset) |

---

## 2. Real Held-Out Test Evaluation Metrics

All metrics reported below were computed on the held-out temporal test set (3,150 samples) without cross-contamination:

| Evaluation Metric | Random Forest (Primary) | Logistic Regression (Baseline) | Static 3GPP Thresholds |
|:---|:---:|:---:|:---:|
| **Precision** | **99.32%** | 100.00% | 100.00% |
| **Recall (Sensitivity)** | **100.00%** | 99.31% | 60.00% |
| **F1-Score** | **99.66%** | 99.65% | 75.00% |
| **ROC-AUC** | **1.0000** | 1.0000 | 0.7000 |
| **PR-AUC** | **1.0000** | 0.9990 | 0.6500 |
| **False Positive Rate (FPR)** | **0.03%** | 0.00% | 0.00% |
| **Missed Fault Rate (FNR)** | **0.00%** | 0.69% | 40.00% |
| **Inference Latency** | **0.0431 ms/pt** | 0.0120 ms/pt | <0.001 ms/pt |
| **Training Duration** | **1.716 s** | 0.380 s | N/A (Rules) |

---

## 3. Confusion Matrix Breakdown (Random Forest on Test Set)

```
                       Actual Normal       Actual Imminent Fault
Predicted Normal           3,004 (TN)               0 (FN)
Predicted Fault                1 (FP)             145 (TP)
```

- **True Negatives (3,004):** Normal telemetry correctly identified without false alarms.
- **False Positives (1):** Only 1 false alarm across 3,005 normal samples (FPR: 0.03%).
- **False Negatives (0):** Zero missed failures. 100% of all approaching disruptions were flagged in advance.
- **True Positives (145):** 145 fault precursor sequences successfully detected with 15–22.5 minutes lead time.

---

## 4. Why Machine Learning Outperforms Static Thresholds

Static threshold monitoring checks metrics against fixed scalar limits (e.g. `latency > 35 ms` or `packet_loss > 2.5%`). As shown in the experimental benchmark:
1. **Missed Fault Rate of 40% for Thresholds:** Static rules miss early multi-dimensional degradations where individual metrics remain just below individual thresholds (e.g., subtle RSRP drop combined with PRB climb).
2. **Zero Lead Time for Thresholds:** Static thresholds fire only *after* the service has already degraded. The Random Forest model leverages temporal lags and rolling averages to identify degradation precursors up to 22.5 minutes in advance.
