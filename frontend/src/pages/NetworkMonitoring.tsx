import React, { useEffect, useState } from 'react';
import { Radio, Filter, RefreshCw, BarChart2, Layers, Cpu, Users } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { api } from '../services/api';
import { TelemetryMetric, SiteInfo, CellInfo } from '../types';

export const NetworkMonitoring: React.FC = () => {
  const [metrics, setMetrics] = useState<TelemetryMetric[]>([]);
  const [sites, setSites] = useState<SiteInfo[]>([]);
  const [cells, setCells] = useState<CellInfo[]>([]);
  const [selectedSite, setSelectedSite] = useState<string>('ALL');
  const [selectedCell, setSelectedCell] = useState<string>('ALL');
  const [limit, setLimit] = useState<number>(40);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchFilters = async () => {
    try {
      const [sRes, cRes] = await Promise.all([api.getSites(), api.getCells()]);
      setSites(sRes);
      setCells(cRes);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const data = await api.getMetricHistory(selectedSite, selectedCell, limit);
      setMetrics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilters();
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2500);
    return () => clearInterval(interval);
  }, [selectedSite, selectedCell, limit]);

  const uniqueTimeMap = new Map();
  metrics.forEach((m) => {
    const timeStr = new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (!uniqueTimeMap.has(timeStr)) {
      uniqueTimeMap.set(timeStr, {
        time: timeStr,
        rsrp: m.rsrp_dbm,
        sinr: m.sinr_db,
        rsrq: m.rsrq_db,
        latency: m.latency_ms,
        packet_loss: m.packet_loss_pct,
        throughput: m.throughput_mbps,
        users: m.connected_users,
        prb: m.prb_utilization_pct,
        cpu: m.cpu_utilization_pct,
        memory: m.memory_utilization_pct,
        site_cell: `${m.site_id}/${m.cell_id}`,
        fault_active: m.fault_active,
        fault_type: m.fault_type
      });
    }
  });
  const chartData = Array.from(uniqueTimeMap.values());

  return (
    <div className="space-y-6">
      {/* Top Filter Bar */}
      <div className="noc-panel p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">5G Telemetry & RAN Monitoring</h1>
            <p className="text-xs text-slate-400">Time-series signals across gNodeB radio, user plane, and compute layers</p>
          </div>
        </div>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Site:</span>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded-md px-2.5 py-1 text-xs focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Sites</option>
              {sites.map((s) => (
                <option key={s.site_id} value={s.site_id}>{s.site_id}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Cell:</span>
            <select
              value={selectedCell}
              onChange={(e) => setSelectedCell(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded-md px-2.5 py-1 text-xs focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Cells</option>
              {cells.map((c) => (
                <option key={`${c.site_id}-${c.cell_id}`} value={c.cell_id}>{c.site_id} - {c.cell_id}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Horizon:</span>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded-md px-2.5 py-1 text-xs focus:outline-none focus:border-cyan-400"
            >
              <option value={25}>Latest 25 pts</option>
              <option value={50}>Latest 50 pts</option>
              <option value={100}>Latest 100 pts</option>
            </select>
          </div>

          <button
            onClick={fetchMetrics}
            className="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 4 Interactive Real-time Telemetry Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Radio Signal Quality (RSRP & SINR) */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-white">Radio Channel Quality (RSRP & SINR)</h2>
              <p className="text-xs text-slate-400">RSRP nominal: -85 dBm | SINR nominal: &gt;18 dB</p>
            </div>
            <div className="text-xs font-mono text-cyan-400">Layer 1/2</div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis yAxisId="rsrp" stroke="#00f0ff" domain={[-140, -40]} fontSize={10} />
                <YAxis yAxisId="sinr" orientation="right" stroke="#a78bfa" domain={[-10, 35]} fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line yAxisId="rsrp" type="monotone" dataKey="rsrp" stroke="#00f0ff" dot={false} strokeWidth={2} name="RSRP (dBm)" />
                <Line yAxisId="sinr" type="monotone" dataKey="sinr" stroke="#a78bfa" dot={false} strokeWidth={2} name="SINR (dB)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Transport & Jitter (Latency & Packet Loss) */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-white">Transport Stability (Latency & Packet Loss)</h2>
              <p className="text-xs text-slate-400">Fronthaul / Midhaul / Backhaul RTT & frame drop percentage</p>
            </div>
            <div className="text-xs font-mono text-rose-400">N3 / GTP-U</div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis yAxisId="lat" stroke="#f43f5e" fontSize={10} />
                <YAxis yAxisId="loss" orientation="right" stroke="#f59e0b" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line yAxisId="lat" type="monotone" dataKey="latency" stroke="#f43f5e" dot={false} strokeWidth={2} name="Latency (ms)" />
                <Line yAxisId="loss" type="monotone" dataKey="packet_loss" stroke="#f59e0b" dot={false} strokeWidth={2} name="Packet Loss (%)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: User Plane Throughput & UE Count */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-white">User Plane Throughput & Active UEs</h2>
              <p className="text-xs text-slate-400">Downlink aggregated bandwidth and connected subscriber count</p>
            </div>
            <div className="text-xs font-mono text-emerald-400">UPF / gNB-CU</div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis yAxisId="tp" stroke="#10b981" fontSize={10} />
                <YAxis yAxisId="users" orientation="right" stroke="#38bdf8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line yAxisId="tp" type="monotone" dataKey="throughput" stroke="#10b981" dot={false} strokeWidth={2} name="Throughput (Mbps)" />
                <Line yAxisId="users" type="monotone" dataKey="users" stroke="#38bdf8" dot={false} strokeWidth={2} name="Active Users" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: PRB & NFVI Compute Load */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-white">PRB Utilization & Compute Load</h2>
              <p className="text-xs text-slate-400">Physical resource blocks vs virtualized NFVI CPU/Memory usage</p>
            </div>
            <div className="text-xs font-mono text-amber-400">NFVI & MAC</div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#fbbf24" domain={[0, 100]} fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="prb" stroke="#fbbf24" dot={false} strokeWidth={2} name="PRB Util (%)" />
                <Line type="monotone" dataKey="cpu" stroke="#c084fc" dot={false} strokeWidth={2} name="CPU Util (%)" />
                <Line type="monotone" dataKey="memory" stroke="#60a5fa" dot={false} strokeWidth={2} name="Memory (%)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Live Raw Telemetry Stream Table */}
      <div className="noc-panel p-5 rounded-xl border border-slate-800">
        <h2 className="text-sm font-bold text-white mb-3">Live 5G Metrics Ingestion Buffer (Latest Samples)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2 px-3">Timestamp</th>
                <th className="py-2 px-3">Entity</th>
                <th className="py-2 px-3">RSRP (dBm)</th>
                <th className="py-2 px-3">SINR (dB)</th>
                <th className="py-2 px-3">Latency (ms)</th>
                <th className="py-2 px-3">Loss (%)</th>
                <th className="py-2 px-3">Throughput</th>
                <th className="py-2 px-3">PRB (%)</th>
                <th className="py-2 px-3">CPU (%)</th>
                <th className="py-2 px-3">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {metrics.slice(-10).reverse().map((m) => (
                <tr key={m.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-2 px-3 text-slate-400">{new Date(m.timestamp).toLocaleTimeString()}</td>
                  <td className="py-2 px-3 text-slate-300 font-semibold">{m.site_id}/{m.cell_id}</td>
                  <td className={`py-2 px-3 ${m.rsrp_dbm < -105 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>{m.rsrp_dbm}</td>
                  <td className={`py-2 px-3 ${m.sinr_db < 5 ? 'text-amber-400 font-bold' : 'text-slate-300'}`}>{m.sinr_db}</td>
                  <td className={`py-2 px-3 ${m.latency_ms > 40 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>{m.latency_ms}</td>
                  <td className={`py-2 px-3 ${m.packet_loss_pct > 2 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>{m.packet_loss_pct}</td>
                  <td className="py-2 px-3 text-emerald-400">{m.throughput_mbps} Mbps</td>
                  <td className="py-2 px-3 text-slate-300">{m.prb_utilization_pct}%</td>
                  <td className="py-2 px-3 text-slate-300">{m.cpu_utilization_pct}%</td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        m.fault_active
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : m.future_fault_within_horizon
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}
                    >
                      {m.fault_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
