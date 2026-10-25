import React, { useEffect, useState } from 'react';
import {
  Sliders,
  Play,
  Square,
  AlertTriangle,
  Radio,
  Zap,
  Activity,
  Layers,
  Cpu,
  Clock,
  CheckCircle,
  Flame
} from 'lucide-react';
import { api } from '../services/api';
import { SimulatorStatus } from '../types';

export const SimulatorControls: React.FC = () => {
  const [simStatus, setSimStatus] = useState<SimulatorStatus | null>(null);
  const [selectedSite, setSelectedSite] = useState<string>('SITE-01');
  const [selectedCell, setSelectedCell] = useState<string>('CELL-01');
  const [selectedComponent, setSelectedComponent] = useState<string>('gNodeB-CU');
  const [duration, setDuration] = useState<number>(45);
  const [severity, setSeverity] = useState<string>('CRITICAL');
  const [triggering, setTriggering] = useState<string | null>(null);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const scenarios = [
    {
      id: 'radio_degradation',
      name: 'Radio Signal Degradation',
      desc: 'Severely drops RSRP (-130 dBm) and SINR (-4 dB). Simulates antenna misalignment, RF feeder fault, or shadowing.',
      icon: Radio,
      badge: 'RF Layer'
    },
    {
      id: 'cell_congestion',
      name: 'Cell Resource Congestion',
      desc: 'Spikes PRB utilization to 98% and surges connected UEs to 500+. Simulates stadium crowds or slice exhaustion.',
      icon: Layers,
      badge: 'MAC/PRB'
    },
    {
      id: 'packet_loss_instability',
      name: 'Packet Loss & Jitter',
      desc: 'Injects 15-30% packet loss and high transmission jitter on Fronthaul/eCPRI transport paths.',
      icon: AlertTriangle,
      badge: 'Transport'
    },
    {
      id: 'increased_latency',
      name: 'Increased RTT Latency',
      desc: 'Increases round-trip latency to 200-350ms, breaching URLLC delay bounds and SLA constraints.',
      icon: Clock,
      badge: 'URLLC SLA'
    },
    {
      id: 'throughput_degradation',
      name: 'Throughput Collapse',
      desc: 'Collapses user plane throughput to <15 Mbps while keeping users active, simulating rank/CQI collapse.',
      icon: Activity,
      badge: 'User Plane'
    },
    {
      id: 'cpu_memory_saturation',
      name: 'NFVI Compute Saturation',
      desc: 'Pushes NFVI container CPU to 99% and Memory to 95%, causing microservice starvation and dropped frames.',
      icon: Cpu,
      badge: 'Cloud NFVI'
    },
    {
      id: 'backhaul_interruption',
      name: 'Backhaul Link Interruption',
      desc: 'Cuts transport connectivity: 85% packet loss, 500ms latency, triggering immediate critical alert.',
      icon: Flame,
      badge: 'Backhaul N3'
    },
    {
      id: 'service_availability_degradation',
      name: 'Core Service Degradation',
      desc: 'Degrades availability to <45%, simulating AMF/NRF signaling failures and registration drops.',
      icon: Zap,
      badge: '5G Core'
    }
  ];

  const fetchStatus = async () => {
    try {
      const s = await api.getSimulatorStatus();
      setSimStatus(s);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleStartStop = async () => {
    try {
      if (simStatus?.is_running) {
        await api.stopSimulator();
      } else {
        await api.startSimulator();
      }
      fetchStatus();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerScenario = async (scenId: string, scenName: string) => {
    setTriggering(scenId);
    try {
      const res = await api.triggerScenario({
        scenario_type: scenId,
        target_site: selectedSite,
        target_cell: selectedCell,
        target_component: selectedComponent,
        duration_seconds: duration,
        severity: severity
      });
      setFeedbackMsg(`Successfully injected "${scenName}" on ${selectedSite}/${selectedCell}!`);
      setTimeout(() => setFeedbackMsg(null), 5000);
      fetchStatus();
    } catch (err) {
      console.error(err);
    } finally {
      setTriggering(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Control Bar */}
      <div className="noc-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Sliders className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-black text-white">5G Testbed Fault Injection & Telemetry Simulator</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Simulates realistic 5G RAN and Core degradation scenarios to validate AI fault prediction and alert dispatch.
          </p>
        </div>

        {/* Master Start/Stop Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleStartStop}
            className={`px-4 py-2 rounded-lg font-bold text-xs transition flex items-center gap-2 shadow-md ${
              simStatus?.is_running
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/30'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30'
            }`}
          >
            {simStatus?.is_running ? <Square className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {simStatus?.is_running ? 'Stop Telemetry Loop' : 'Start Telemetry Loop'}
          </button>
        </div>
      </div>

      {feedbackMsg && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-500/50 rounded-lg text-emerald-200 text-xs flex items-center justify-between animate-fade-in">
          <span>{feedbackMsg}</span>
          <button onClick={() => setFeedbackMsg(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Target Configuration Panel */}
      <div className="noc-panel p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-4 text-xs">
        <span className="font-bold text-white uppercase tracking-wider">Injection Targets:</span>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Site:</span>
          <select
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1 text-xs"
          >
            <option value="SITE-01">SITE-01 (Urban Macro)</option>
            <option value="SITE-02">SITE-02 (Sub-Urban)</option>
            <option value="SITE-03">SITE-03 (Industrial Campus)</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Cell:</span>
          <select
            value={selectedCell}
            onChange={(e) => setSelectedCell(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1 text-xs"
          >
            <option value="CELL-01">CELL-01 (Sector 1)</option>
            <option value="CELL-02">CELL-02 (Sector 2)</option>
            <option value="CELL-03">CELL-03 (Sector 3)</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Component:</span>
          <select
            value={selectedComponent}
            onChange={(e) => setSelectedComponent(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1 text-xs"
          >
            <option value="gNodeB-CU">gNodeB-CU (Central Unit)</option>
            <option value="gNodeB-DU">gNodeB-DU (Distributed Unit)</option>
            <option value="RU-RadioUnit">RU-RadioUnit (Active Antenna)</option>
            <option value="5G-Core-UPF">5G-Core-UPF (User Plane)</option>
            <option value="5G-Core-AMF">5G-Core-AMF (Control Plane)</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Duration:</span>
          <select
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1 text-xs"
          >
            <option value={30}>30 Seconds</option>
            <option value={45}>45 Seconds</option>
            <option value={60}>60 Seconds</option>
            <option value={90}>90 Seconds</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Severity:</span>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1 text-xs"
          >
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {/* Active Fault Scenarios Countdown Table */}
      {simStatus && simStatus.active_scenarios.length > 0 && (
        <div className="noc-panel p-4 rounded-xl border border-rose-800/80 bg-rose-950/20">
          <h3 className="text-xs font-bold text-rose-300 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-500 animate-bounce" />
            Currently Active Injected Fault Scenarios ({simStatus.active_scenarios.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {simStatus.active_scenarios.map((sc) => {
              const remaining = Math.max(0, Math.round(sc.duration_seconds - sc.elapsed_seconds));
              return (
                <div key={sc.scenario_id} className="p-3 rounded-lg bg-slate-900 border border-rose-700/60 text-xs">
                  <div className="flex items-center justify-between font-bold text-white">
                    <span className="capitalize">{sc.scenario_type.replace('_', ' ')}</span>
                    <span className="text-rose-400 font-mono">{remaining}s left</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 font-mono">
                    Target: {sc.target_site} / {sc.target_cell} ({sc.target_component})
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 8 Fault Scenario Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {scenarios.map((scen) => {
          const Icon = scen.icon;
          return (
            <div
              key={scen.id}
              className="noc-panel noc-panel-hover p-4 rounded-xl border border-slate-800 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-900 text-cyan-400 border border-slate-800">
                    {scen.badge}
                  </span>
                  <Icon className="w-4 h-4 text-cyan-400" />
                </div>
                <h3 className="text-sm font-bold text-white mt-2.5">{scen.name}</h3>
                <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{scen.desc}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80">
                <button
                  onClick={() => handleTriggerScenario(scen.id, scen.name)}
                  disabled={triggering !== null}
                  className="w-full py-1.5 px-3 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition flex items-center justify-center gap-1.5"
                >
                  <Flame className="w-3.5 h-3.5 text-cyan-400" />
                  {triggering === scen.id ? 'Injecting...' : 'Inject Scenario'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
