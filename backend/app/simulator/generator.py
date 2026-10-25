import random
import time
import math
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class ActiveFaultScenario:
    scenario_id: str
    scenario_type: str
    target_site: str
    target_cell: str
    target_component: str
    start_time: float
    duration_seconds: float
    severity: str = "HIGH"
    gradual_steps: int = 10
    current_step: int = 0

class NetworkTelemetrySimulator:
    """
    Realistic 5G Telemetry Simulator producing realistic radio, transport, capacity,
    and compute metrics with precursors, fault onset, and recovery cycles.
    """
    def __init__(self, seed: Optional[int] = 42):
        if seed is not None:
            random.seed(seed)
        
        self.sites = ["SITE-01", "SITE-02", "SITE-03"]
        self.cells = ["CELL-01", "CELL-02", "CELL-03"]
        self.components = ["gNodeB-CU", "gNodeB-DU", "RU-RadioUnit", "5G-Core-UPF", "5G-Core-AMF"]
        
        # State tracking per (site, cell, component)
        self.states: Dict[str, Dict[str, float]] = {}
        self.active_scenarios: Dict[str, ActiveFaultScenario] = {}
        self.scheduled_future_faults: List[Dict[str, Any]] = []
        
        self._init_nominal_states()

    def _state_key(self, site: str, cell: str, comp: str) -> str:
        return f"{site}::{cell}::{comp}"

    def _init_nominal_states(self):
        for s in self.sites:
            for c in self.cells:
                for comp in self.components:
                    key = self._state_key(s, c, comp)
                    self.states[key] = {
                        "rsrp_dbm": random.uniform(-85.0, -75.0),
                        "rsrq_db": random.uniform(-11.0, -8.0),
                        "sinr_db": random.uniform(16.0, 24.0),
                        "latency_ms": random.uniform(8.0, 15.0),
                        "packet_loss_pct": random.uniform(0.01, 0.15),
                        "throughput_mbps": random.uniform(420.0, 680.0),
                        "connected_users": random.randint(45, 110),
                        "prb_utilization_pct": random.uniform(25.0, 48.0),
                        "cpu_utilization_pct": random.uniform(28.0, 52.0),
                        "memory_utilization_pct": random.uniform(35.0, 55.0),
                        "availability_pct": 99.98,
                        "drift_phase": random.uniform(0, math.pi * 2)
                    }

    def trigger_scenario(
        self,
        scenario_type: str,
        target_site: str = "SITE-01",
        target_cell: str = "CELL-01",
        target_component: str = "gNodeB-CU",
        duration_seconds: int = 60,
        severity: str = "CRITICAL"
    ) -> str:
        scenario_id = f"SCEN-{int(time.time())}-{random.randint(100, 999)}"
        scenario = ActiveFaultScenario(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            target_site=target_site,
            target_cell=target_cell,
            target_component=target_component,
            start_time=time.time(),
            duration_seconds=duration_seconds,
            severity=severity
        )
        self.active_scenarios[scenario_id] = scenario
        return scenario_id

    def clear_scenarios(self):
        self.active_scenarios.clear()

    def generate_point(
        self,
        site_id: str,
        cell_id: str,
        component_id: str,
        timestamp: Optional[datetime.datetime] = None,
        force_scenario: Optional[str] = None,
        force_future_fault: bool = False
    ) -> Dict[str, Any]:
        if timestamp is None:
            timestamp = datetime.datetime.now()

        key = self._state_key(site_id, cell_id, component_id)
        if key not in self.states:
            self._init_nominal_states()
        
        st = self.states[key]
        st["drift_phase"] += 0.05
        cycle = math.sin(st["drift_phase"])

        # Check if an active scenario applies to this entity
        active_scen = None
        now_ts = time.time()
        for sc in list(self.active_scenarios.values()):
            if now_ts > sc.start_time + sc.duration_seconds:
                # Expired
                self.active_scenarios.pop(sc.scenario_id, None)
                continue
            if (sc.target_site == site_id and
                sc.target_cell == cell_id and
                (sc.target_component == component_id or sc.target_component == "ALL")):
                active_scen = sc
                break

        scenario_name = force_scenario or (active_scen.scenario_type if active_scen else "NORMAL")
        fault_active = scenario_name != "NORMAL"
        severity = active_scen.severity if active_scen else ("CRITICAL" if fault_active else "NONE")

        # Nominal baselines with natural stochastic noise
        rsrp = -80.0 + cycle * 3.0 + random.gauss(0, 1.2)
        rsrq = -9.5 + cycle * 0.8 + random.gauss(0, 0.4)
        sinr = 20.0 + cycle * 2.0 + random.gauss(0, 1.0)
        latency = 12.0 + random.gauss(0, 1.5)
        packet_loss = max(0.0, 0.05 + random.gauss(0, 0.02))
        throughput = 550.0 + cycle * 50.0 + random.gauss(0, 20.0)
        users = int(max(10, 80 + cycle * 25 + random.randint(-5, 5)))
        prb = max(10.0, min(95.0, 40.0 + cycle * 12.0 + random.gauss(0, 3.0)))
        cpu = max(15.0, min(98.0, 42.0 + cycle * 8.0 + random.gauss(0, 2.5)))
        memory = max(20.0, min(95.0, 48.0 + cycle * 5.0 + random.gauss(0, 1.5)))
        availability = 99.98

        # Precursor / future fault subtle indicators if future fault is near
        has_future_fault = force_future_fault
        if not fault_active and active_scen is not None:
            # Active scenario approaching or in early phase
            has_future_fault = True

        if has_future_fault and not fault_active:
            # Subtle degradation precursor: micro-jitter and slight SNR drop
            rsrp -= random.uniform(4.0, 8.0)
            sinr -= random.uniform(2.5, 5.0)
            latency += random.uniform(5.0, 12.0)
            cpu += random.uniform(6.0, 14.0)
            prb += random.uniform(8.0, 16.0)

        # Inject specific scenario perturbations
        if fault_active:
            if scenario_name == "radio_degradation":
                rsrp = -118.0 - random.uniform(5.0, 18.0)
                rsrq = -17.5 - random.uniform(1.0, 3.5)
                sinr = -2.5 - random.uniform(1.0, 6.0)
                throughput = max(10.0, throughput * 0.15)
                packet_loss += random.uniform(3.5, 9.0)
                latency += random.uniform(35.0, 80.0)
            
            elif scenario_name == "cell_congestion":
                users = random.randint(380, 580)
                prb = min(99.8, 92.0 + random.uniform(2.0, 7.5))
                latency += random.uniform(45.0, 110.0)
                packet_loss += random.uniform(2.0, 6.5)
                throughput = max(25.0, throughput * 0.25)
                cpu += random.uniform(25.0, 40.0)
            
            elif scenario_name == "packet_loss_instability":
                packet_loss = random.uniform(10.0, 32.0)
                latency += random.uniform(60.0, 140.0)
                throughput = max(15.0, throughput * 0.3)
            
            elif scenario_name == "increased_latency":
                latency = random.uniform(140.0, 310.0)
                packet_loss += random.uniform(1.5, 4.5)
                throughput = max(35.0, throughput * 0.4)
            
            elif scenario_name == "throughput_degradation":
                throughput = random.uniform(4.0, 18.0)
                packet_loss += random.uniform(2.0, 5.0)
                latency += random.uniform(25.0, 55.0)
            
            elif scenario_name == "cpu_memory_saturation":
                cpu = min(99.9, 94.0 + random.uniform(2.0, 5.8))
                memory = min(99.5, 92.0 + random.uniform(2.0, 7.2))
                latency += random.uniform(80.0, 190.0)
                packet_loss += random.uniform(3.0, 8.0)
                availability = max(70.0, availability - random.uniform(5.0, 20.0))
            
            elif scenario_name == "backhaul_interruption":
                packet_loss = random.uniform(55.0, 94.0)
                latency = random.uniform(320.0, 650.0)
                throughput = random.uniform(0.1, 4.0)
                availability = max(20.0, availability - random.uniform(30.0, 65.0))
            
            elif scenario_name == "service_availability_degradation":
                availability = random.uniform(25.0, 68.0)
                latency += random.uniform(90.0, 220.0)
                packet_loss += random.uniform(12.0, 35.0)
                throughput = max(5.0, throughput * 0.1)

        # Clamping to valid physical 5G ranges
        rsrp = max(-140.0, min(-40.0, rsrp))
        rsrq = max(-25.0, min(-3.0, rsrq))
        sinr = max(-15.0, min(35.0, sinr))
        latency = max(2.0, min(1200.0, latency))
        packet_loss = max(0.0, min(100.0, packet_loss))
        throughput = max(0.0, min(2500.0, throughput))
        prb = max(0.0, min(100.0, prb))
        cpu = max(0.0, min(100.0, cpu))
        memory = max(0.0, min(100.0, memory))
        availability = max(0.0, min(100.0, availability))

        return {
            "timestamp": timestamp,
            "site_id": site_id,
            "cell_id": cell_id,
            "component_id": component_id,
            "rsrp_dbm": round(rsrp, 2),
            "rsrq_db": round(rsrq, 2),
            "sinr_db": round(sinr, 2),
            "latency_ms": round(latency, 2),
            "packet_loss_pct": round(packet_loss, 2),
            "throughput_mbps": round(throughput, 2),
            "connected_users": int(users),
            "prb_utilization_pct": round(prb, 2),
            "cpu_utilization_pct": round(cpu, 2),
            "memory_utilization_pct": round(memory, 2),
            "availability_pct": round(availability, 2),
            "fault_type": scenario_name,
            "fault_severity": severity,
            "fault_active": fault_active,
            "future_fault_within_horizon": bool(has_future_fault or fault_active),
            "is_simulated": True
        }

    def generate_batch(
        self,
        num_steps: int = 500,
        step_interval_seconds: int = 15,
        start_time: Optional[datetime.datetime] = None,
        inject_fault_probability: float = 0.12
    ) -> List[Dict[str, Any]]:
        """
        Generate a fully labeled historical sequence across sites & cells with
        statistically sound precursors and balanced distribution across temporal train/test splits.
        """
        if start_time is None:
            start_time = datetime.datetime.now() - datetime.timedelta(seconds=num_steps * step_interval_seconds)

        records = []
        scenarios_catalog = [
            "radio_degradation",
            "cell_congestion",
            "packet_loss_instability",
            "increased_latency",
            "throughput_degradation",
            "cpu_memory_saturation",
            "backhaul_interruption",
            "service_availability_degradation"
        ]

        # Deterministically schedule episodes across the timeline (train AND test periods)
        episodes = []
        step = 25
        while step < num_steps - 15:
            scen = random.choice(scenarios_catalog)
            site = random.choice(self.sites)
            cell = random.choice(self.cells)
            # Either a specific component or ALL components in that cell
            comp = random.choice(self.components + ["ALL"])
            duration = random.randint(10, 22)  # steps of active fault
            precursor_len = random.randint(10, 16) # steps of precursor
            
            episodes.append({
                "start_step": step,
                "end_step": step + duration,
                "horizon_precursor_start": max(0, step - precursor_len),
                "scenario": scen,
                "site": site,
                "cell": cell,
                "comp": comp
            })
            step += duration + random.randint(20, 35)

        for step_idx in range(num_steps):
            current_dt = start_time + datetime.timedelta(seconds=step_idx * step_interval_seconds)
            
            for site in self.sites:
                for cell in self.cells:
                    for comp in self.components:
                        # Check episode matches
                        matching_active = [
                            ep for ep in episodes
                            if ep["site"] == site and ep["cell"] == cell and (ep["comp"] == comp or ep["comp"] == "ALL")
                            and ep["start_step"] <= step_idx <= ep["end_step"]
                        ]
                        matching_precursor = [
                            ep for ep in episodes
                            if ep["site"] == site and ep["cell"] == cell and (ep["comp"] == comp or ep["comp"] == "ALL")
                            and ep["horizon_precursor_start"] <= step_idx < ep["start_step"]
                        ]

                        force_scen = None
                        force_future = False

                        if matching_active:
                            force_scen = matching_active[0]["scenario"]
                            force_future = True
                        elif matching_precursor:
                            force_scen = "NORMAL"
                            force_future = True

                        point = self.generate_point(
                            site_id=site,
                            cell_id=cell,
                            component_id=comp,
                            timestamp=current_dt,
                            force_scenario=force_scen,
                            force_future_fault=force_future
                        )
                        records.append(point)

        return records
