import React, { useEffect, useState } from 'react';
import { ShieldCheck, AlertOctagon, Activity, Radio, Info } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine
} from 'recharts';
import { api } from '../services/api';
import { PredictionRecord } from '../types';

export const AnomalyDetection: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionRecord[]>([]);

  const fetchData = async () => {
    try {
      const data = await api.getPredictionHistory(undefined, undefined, 40);
      setPredictions(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const uniqueTimeMap = new Map();
  predictions.forEach((p) => {
    const timeStr = new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (!uniqueTimeMap.has(timeStr)) {
      uniqueTimeMap.set(timeStr, {
        time: timeStr,
        score: p.anomaly_score,
        is_anomaly: p.is_anomaly,
        risk: p.risk_score,
        entity: `${p.site_id}/${p.cell_id}`
      });
    }
  });
  const chartData = Array.from(uniqueTimeMap.values());

  const anomalyCount = predictions.filter(p => p.is_anomaly).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="noc-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-black text-white">Unsupervised Anomaly Detection (Isolation Forest)</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Detects zero-day structural anomalies, silent degradation, and outlier telemetry patterns without requiring predefined labels.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <div className="text-[10px] text-slate-400">Contamination Ratio</div>
            <div className="font-mono font-bold text-cyan-400">8.0% Adaptive</div>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <div className="text-[10px] text-slate-400">Threshold Cutoff</div>
            <div className="font-mono font-bold text-rose-400">-0.05 Score</div>
          </div>
        </div>
      </div>

      {/* Main Chart: Isolation Score Timeline */}
      <div className="noc-panel p-5 rounded-xl border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-bold text-white">Anomaly Decision Function Timeline</h2>
            <p className="text-xs text-slate-400">Negative scores beneath the red line indicate multi-dimensional outlier isolation</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-slate-400">Flagged Anomalies:</span>
            <span className={`font-bold ${anomalyCount > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {anomalyCount} / {predictions.length}
            </span>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#94a3b8" domain={[-0.35, 0.25]} fontSize={10} />
              <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
              <ReferenceLine y={-0.05} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: 'Anomaly Threshold (-0.05)', fill: '#f43f5e', fontSize: 10, position: 'top' }} />
              <ReferenceLine y={0.0} stroke="#475569" strokeDasharray="2 2" />
              <Line type="monotone" dataKey="score" stroke="#00f0ff" strokeWidth={2} dot={(props: any) => {
                const { cx, cy, payload } = props;
                if (payload.is_anomaly) {
                  return <circle cx={cx} cy={cy} r={4} fill="#f43f5e" stroke="#fff" strokeWidth={1} />;
                }
                return <circle cx={cx} cy={cy} r={2} fill="#00f0ff" />;
              }} name="Anomaly Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Flagged Anomalies Grid */}
      <div className="noc-panel p-5 rounded-xl border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-white">Isolation Forest Outlier Ingestion Audit</h2>
          <span className="text-xs text-slate-400">Real-time isolation path length analysis</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2 px-3">Time</th>
                <th className="py-2 px-3">Entity</th>
                <th className="py-2 px-3">Decision Score</th>
                <th className="py-2 px-3">Classification</th>
                <th className="py-2 px-3">Risk Assessment</th>
                <th className="py-2 px-3">Top Anomaly Dimension</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {predictions.slice(-10).reverse().map((p) => {
                const topFeat = Object.keys(p.top_contributing_features || {})[0] || 'Nominal envelope';
                return (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-2 px-3 text-slate-400">{new Date(p.timestamp).toLocaleTimeString()}</td>
                    <td className="py-2 px-3 text-slate-300 font-bold">{p.site_id}/{p.cell_id}</td>
                    <td className={`py-2 px-3 font-bold ${p.anomaly_score < -0.05 ? 'text-rose-400' : 'text-cyan-400'}`}>
                      {p.anomaly_score.toFixed(4)}
                    </td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        p.is_anomaly ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}>
                        {p.is_anomaly ? 'ANOMALOUS' : 'NOMINAL'}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <span className="text-slate-300 font-semibold">{p.risk_level} ({(p.risk_score * 100).toFixed(0)}%)</span>
                    </td>
                    <td className="py-2 px-3 text-slate-400 truncate max-w-xs">{topFeat}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
