# Machine Learning Methodology: 5G Telemetry & Fault Prediction
**Team:** Team Dynamites

---

## 1. Problem Formulation & Temporal Horizon

Traditional telecom fault monitoring relies on reactive threshold alarms (e.g., alert when latency > 50 ms or packet loss > 3%). This approach generates high false alarm rates during transient bursts and fails to give network operations center (NOC) teams actionable lead time before catastrophic service failure.

Our proactive system formulates the task as **Early Future-Fault Prediction**:
Given a multi-variate telemetry stream $\mathbf{x}_t$ at current observation time $t$:
$$y_t = \begin{cases} 1 & \text{if a network fault begins in } [t+1, t+H] \\ 0 & \text{otherwise} \end{cases}$$
where $H = 15 \text{ steps}$ (corresponding to a 15–22.5 minute proactive lead time).

---

## 2. Leakage-Free Temporal Feature Engineering

To guarantee strict prevention of future target leakage, feature extraction uses only causal backward-looking operations:

1. **Rolling Averages & Volatility (Historical Window $W=3$):**
   $$\mu_{i, t} = \frac{1}{W} \sum_{k=0}^{W-1} x_{i, t-k}, \quad \sigma_{i, t} = \sqrt{\frac{1}{W-1} \sum_{k=0}^{W-1} (x_{i, t-k} - \mu_{i, t})^2}$$
2. **Sequential Lags:**
   $$x_{i, t-1}, \quad x_{i, t-2}$$
3. **Temporal First-Difference (Deltas):**
   $$\Delta x_{i, t} = x_{i, t} - x_{i, t-1}$$
4. **Domain-Specific 5G Interaction Features:**
   - **Spectral Efficiency Proxy:**
     $$\text{SEP}_t = \frac{\text{Throughput}_t}{\text{PRB Utilization}_t + 10^{-4}}$$
   - **Load Stress Index (NFVI & Radio Composite):**
     $$\text{LSI}_t = 0.40 \cdot \text{PRB}_t + 0.30 \cdot \text{CPU}_t + 0.30 \cdot \text{MEM}_t$$
   - **Channel Quality Deficit:**
     $$\text{CQD}_t = \max(0, -95 - \text{RSRP}_t) + \max(0, 10 - \text{SINR}_t)$$

---

## 3. Machine Learning Models

### A. Primary Supervised Predictor: Random Forest
- **Ensemble size:** 120 estimators
- **Max tree depth:** 14 (prevents overfitting to noise)
- **Class weighting:** Balanced (accounts for normal traffic prevalence)
- **Criterion:** Gini impurity with bootstrap aggregation

### B. Baseline Supervised Predictor: Logistic Regression
- Standardized feature scaling (Z-score normalized)
- L2 regularization with balanced class weights

### C. Unsupervised Anomaly Detector: Isolation Forest
- **Estimators:** 100 trees
- **Contamination rate:** 0.08
- Generates decision score $s(x) \in [-0.4, +0.25]$. Scores below $-0.05$ indicate isolation in short tree paths (structural anomaly).

---

## 4. Composite Risk Scoring Formula

The operational risk score $R \in [0.0, 1.0]$ blends supervised prediction probability, unsupervised anomaly deviation, and physical metric penalties:

$$R = 0.55 \cdot P(\text{Fault}) + 0.30 \cdot \text{NormAnomaly} + 0.15 \cdot \text{SevPenalty}$$

Where:
$$\text{NormAnomaly} = \text{clip}\left(\frac{0.15 - s(x)}{0.50}, 0.0, 1.0\right)$$

### Operational Risk Levels:
- **LOW ($R < 0.35$):** Nominal operational envelope. Routine telemetry logging.
- **MEDIUM ($0.35 \le R < 0.55$):** Precursor detected. Increased sampling frequency.
- **HIGH ($0.55 \le R < 0.75$):** High probability of imminent disruption within 20 minutes. Auto-generate WARNING alert.
- **CRITICAL ($R \ge 0.75$):** Imminent or active severe service failure. Auto-generate CRITICAL alert and dispatch ONAP VES event.
