# Engineering Limitations & Prioritized Roadmap
**Project:** AI-Powered Fault Prediction in 5G Testbed  
**Team:** Team Dynamites

---

## 1. Current Engineering Decisions & Limitations

1. **Simulation-First Telemetry:**
   - *Status:* Implemented
   - *Detail:* In compliance with the prompt's mandatory Mode A requirement, telemetry is generated via a stochastic 5G simulator adhering to 3GPP TS 38.215 / 38.331 ranges.
   - *Limitation:* It approximates multi-path Rayleigh fading, atmospheric absorption, and MAC scheduler dynamics rather than measuring physical millimeter-wave SDRs in an anechoic chamber.
   - *Workaround Provided:* Clean Open5GS / UERANSIM adapter interfaces provided in `backend/app/integrations/`.

2. **Database Storage Engine:**
   - *Status:* Implemented
   - *Detail:* SQLite is used by default for zero-friction local and CI/CD execution with WAL (write-ahead logging) mode.
   - *Limitation:* Highly concurrent multi-worker writes (>1,000 writes/sec) are better served by distributed time-series databases like TimescaleDB or InfluxDB.
   - *Workaround Provided:* Full SQLAlchemy ORM abstraction allowing immediate swap to PostgreSQL via a single `DATABASE_URL` environment variable.

3. **ONAP Adapter:**
   - *Status:* Mocked
   - *Detail:* Formats 100% compliant VES 7.2 commonEventHeader and faultFields payloads and records them in a local dispatch buffer.
   - *Limitation:* A live ONAP deployment requires extensive multi-node Kubernetes clusters (DCAE, SDNC, SO) which are outside local hardware scope.

---

## 2. Prioritized Roadmap & Next Steps

- [ ] **Phase A (Hardware Integration):** Connect live Open5GS core and UERANSIM / USRP B210 software-defined radios via the gNB F1-C / N2 interfaces.
- [ ] **Phase B (Deep Temporal Modeling):** Benchmark bidirectional LSTM / Temporal Convolutional Networks (TCN) alongside Random Forest for ultra-long horizon (60+ minute) prediction.
- [ ] **Phase C (Closed-Loop Automation):** Integrate automated O-RAN RIC (RAN Intelligent Controller) xApp actions to dynamically adjust antenna beam tilt and PRB slicing without human operator intervention.
