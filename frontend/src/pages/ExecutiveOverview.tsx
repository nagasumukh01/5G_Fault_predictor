import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Radio,
  Zap,
  TrendingDown,
  TrendingUp,
  ShieldCheck,
  CheckCircle,
  Play,
  RotateCcw,
  Clock
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import { api } from '../services/api';
import { TelemetryMetric, PredictionRecord, AlertRecord, SimulatorStatus } from '../types';

export const ExecutiveOverview: React.FC = () => {
  const [metrics, setMetrics] = useState<TelemetryMetric[]>([]);
  const [predictions, setPredictions] = useState<PredictionRecord[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [simStatus, setSimStatus] = useState<SimulatorStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [triggering, setTriggering] = useState<string | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [mRes, pRes, aRes, sRes] = await Promise.all([
        api.getMetricHistory('SITE-01', 'CELL-01', 30),
        api.getLatestPredictions('SITE-01', 'CELL-01', 15),
        api.getAlerts({ status: 'ACTIVE', limit: 10 }),
        api.getSimulatorStatus()
      ]);
      setMetrics(mRes);
      setPredictions(pRes);
      setAlerts(aRes);
      setSimStatus(sRes);
    } catch (err) {
      console.error('Failed to fetch executive data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleQuickTrigger = async (type: string, name: string) => {
    setTriggering(type);
    try {
      await api.triggerScenario({
        scenario_type: type,
        target_site: 'SITE-01',
        target_cell: 'CELL-01',
        target_component: 'gNodeB-CU',
        duration_seconds: 40,
        severity: 'CRITICAL'
      });
      setNotification(`Injected scenario: ${name}. Watch predictions and alerts adapt!`);
      setTimeout(() => setNotification(null), 5000);
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setTriggering(null);
    }
  };

  // Aggregated KPIs
  const latestMetric = metrics[metrics.length - 1];
  const activeAlertCount = alerts.filter(a => a.status === 'ACTIVE').length;
  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL' && a.status === 'ACTIVE').length;
  const latestPrediction = predictions[0];
  const avgThroughput = metrics.length ? Math.round(metrics.reduce((acc, m) => acc + m.throughput_mbps, 0) / metrics.length) : 550;
  const avgLatency = metrics.length ? Math.round(metrics.reduce((acc, m) => acc + m.latency_ms, 0) / metrics.length) : 12;

  // Chart series formatting with unique timestamps
  const uniqueTimeMap = new Map();
  metrics.forEach((m) => {
    const timeStr = new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (!uniqueTimeMap.has(timeStr)) {
      uniqueTimeMap.set(timeStr, {
        time: timeStr,
        throughput: m.throughput_mbps,
        latency: m.latency_ms,
        packet_loss: m.packet_loss_pct,
        rsrp: m.rsrp_dbm,
        sinr: m.sinr_db
      });
    }
  });
  const chartData = Array.from(uniqueTimeMap.values());

  return (
    <div className="space-y-6">
      {/* Page Title & Mission Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 noc-panel p-6 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white tracking-tight">
              Executive Network Operations & AI Radar
            </h1>
            <span className="px-2 py-0.5 rounded text-xs font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
              LIVE 5G TESTBED
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Real-time proactive fault prediction, multi-cell telemetric analysis, and autonomous risk scoring.
          </p>
        </div>

        {/* Quick Simulator injection actions */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium mr-1">Inject Fault:</span>
          <button
            onClick={() => handleQuickTrigger('radio_degradation', 'Radio Degradation')}
            disabled={triggering !== null}
            className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold transition"
          >
            Radio Drop
          </button>
          <button
            onClick={() => handleQuickTrigger('cell_congestion', 'Cell Congestion')}
            disabled={triggering !== null}
            className="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-semibold transition"
          >
            Congestion
          </button>
          <button
            onClick={() => handleQuickTrigger('backhaul_interruption', 'Backhaul Cut')}
            disabled={triggering !== null}
            className="px-3 py-1.5 rounded-lg bg-red-600/10 hover:bg-red-600/20 text-red-400 border border-red-600/30 text-xs font-semibold transition"
          >
            Backhaul Cut
          </button>
        </div>
      </div>

      {notification && (
        <div className="p-3 bg-cyan-950/80 border border-cyan-500/50 rounded-lg text-cyan-200 text-xs flex items-center justify-between animate-fade-in">
          <span>{notification}</span>
          <button onClick={() => setNotification(null)} className="text-cyan-400 hover:text-white">✕</button>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* KPI 1: Risk Level */}
        <div className="noc-panel noc-panel-hover p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Network Risk Level</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span
              className={`text-2xl font-black ${
                latestPrediction?.risk_level === 'CRITICAL'
                  ? 'text-rose-500 animate-pulse'
                  : latestPrediction?.risk_level === 'HIGH'
                  ? 'text-amber-400'
                  : latestPrediction?.risk_level === 'MEDIUM'
                  ? 'text-yellow-300'
                  : 'text-emerald-400'
              }`}
            >
              {latestPrediction?.risk_level || 'LOW'}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Score: {latestPrediction ? (latestPrediction.risk_score * 100).toFixed(0) : '0'}%
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 flex items-center gap-1">
            <Clock className="w-3 h-3 text-cyan-400" />
            Lead horizon: ~22.5 mins
          </div>
        </div>

        {/* KPI 2: Active Alarms */}
        <div className="noc-panel noc-panel-hover p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Active Incidents</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">{activeAlertCount}</span>
            {criticalCount > 0 && (
              <span className="text-xs text-rose-400 font-semibold bg-rose-950 px-1.5 py-0.5 rounded border border-rose-800">
                {criticalCount} Critical
              </span>
            )}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">
            {activeAlertCount === 0 ? 'Nominal envelope maintained' : 'Requires triage & mitigation'}
          </div>
        </div>

        {/* KPI 3: User Throughput */}
        <div className="noc-panel noc-panel-hover p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg Throughput</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-2xl font-black text-cyan-400">{avgThroughput}</span>
            <span className="text-xs text-slate-400">Mbps</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">
            Latest: {latestMetric?.throughput_mbps.toFixed(1) || '0'} Mbps
          </div>
        </div>

        {/* KPI 4: Transport Latency */}
        <div className="noc-panel noc-panel-hover p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>RTT Transport Latency</span>
            <TrendingDown className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-2xl font-black text-white">{avgLatency}</span>
            <span className="text-xs text-slate-400">ms</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">
            Packet loss: {latestMetric?.packet_loss_pct.toFixed(2) || '0'}%
          </div>
        </div>

        {/* KPI 5: Model Engine */}
        <div className="noc-panel noc-panel-hover p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>ML Predictive State</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-2xl font-black text-emerald-400">99.7%</span>
            <span className="text-xs text-slate-400">F1 score</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">
            RF (Primary) + IsoForest
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time Throughput & Latency Trend */}
        <div className="lg:col-span-2 noc-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Live 5G Throughput & Transport Latency
              </h2>
              <p className="text-xs text-slate-400">Real-time telemetry stream across monitored cells</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Throughput (Mbps)
              </span>
              <span className="flex items-center gap-1.5 text-indigo-400">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400" /> Latency (ms)
              </span>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorThroughput" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00f0ff" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#818cf8" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis yAxisId="left" stroke="#00f0ff" fontSize={11} />
                <YAxis yAxisId="right" orientation="right" stroke="#818cf8" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Area yAxisId="left" type="monotone" dataKey="throughput" stroke="#00f0ff" fillOpacity={1} fill="url(#colorThroughput)" name="Throughput (Mbps)" />
                <Area yAxisId="right" type="monotone" dataKey="latency" stroke="#818cf8" fillOpacity={1} fill="url(#colorLatency)" name="Latency (ms)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Imminent Fault Radar & Recent Alerts */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-white tracking-wide">
                Active Incidents & Alerts
              </h2>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                {activeAlertCount} Unresolved
              </span>
            </div>

            <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
              {alerts.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-xs">
                  <CheckCircle className="w-8 h-8 mx-auto text-emerald-500/50 mb-2" />
                  All 5G nodes running nominal. No active faults detected.
                </div>
              ) : (
                alerts.slice(0, 4).map((a) => (
                  <div
                    key={a.id}
                    className={`p-3 rounded-lg border text-xs ${
                      a.severity === 'CRITICAL'
                        ? 'bg-rose-950/40 border-rose-800 text-rose-200'
                        : 'bg-amber-950/40 border-amber-800 text-amber-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold tracking-wide uppercase">{a.fault_type.replace('_', ' ')}</span>
                      <span className="text-[10px] font-mono opacity-80">{a.site_id} / {a.cell_id}</span>
                    </div>
                    <p className="text-[11px] mt-1 text-slate-300 line-clamp-1">{a.message}</p>
                    <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                      <span>Risk: {(a.risk_score * 100).toFixed(0)}%</span>
                      <span className="font-mono">{new Date(a.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <span>Simulator Status:</span>
            <span className={`font-semibold ${simStatus?.is_running ? 'text-emerald-400' : 'text-slate-500'}`}>
              {simStatus?.is_running ? '● STREAMING (2.0s tick)' : '○ PAUSED'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
