import React, { useEffect, useState } from 'react';
import { Zap, Clock, ShieldAlert, Cpu, CheckCircle2, Play, AlertCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar
} from 'recharts';
import { api } from '../services/api';
import { PredictionRecord } from '../types';

export const FaultPrediction: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionRecord[]>([]);
  const [testResult, setTestResult] = useState<any | null>(null);
  const [runningTest, setRunningTest] = useState<boolean>(false);
  const [selectedSite, setSelectedSite] = useState<string>('SITE-01');
  const [selectedCell, setSelectedCell] = useState<string>('CELL-01');

  const fetchPredictions = async () => {
    try {
      const data = await api.getPredictionHistory(undefined, undefined, 35);
      setPredictions(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleRunInference = async () => {
    setRunningTest(true);
    try {
      const res = await api.runPrediction({
        site_id: selectedSite,
        cell_id: selectedCell,
        component_id: 'gNodeB-CU'
      });
      setTestResult(res);
      fetchPredictions();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningTest(false);
    }
  };

  const latest = predictions[predictions.length - 1];

  const uniqueTimeMap = new Map();
  predictions.forEach((p) => {
    const timeStr = new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (!uniqueTimeMap.has(timeStr)) {
      uniqueTimeMap.set(timeStr, {
        time: timeStr,
        probability: Math.round(p.fault_probability * 100),
        risk_score: Math.round(p.risk_score * 100),
        predicted_fault: p.predicted_fault ? 1 : 0
      });
    }
  });
  const chartData = Array.from(uniqueTimeMap.values());

  // Format top features for bar chart
  const featureList = latest?.top_contributing_features
    ? Object.entries(latest.top_contributing_features).map(([name, val]) => ({
        feature: name.replace('_rolling_mean_3', ' (roll)').replace('_pct', '%'),
        value: typeof val === 'number' ? Math.round(val * 10) / 10 : 0
      }))
    : [
        { feature: 'latency_mean', value: 12.4 },
        { feature: 'prb_util', value: 38.2 },
        { feature: 'spectral_eff', value: 14.5 }
      ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="noc-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Zap className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-black text-white">AI Supervised Future-Fault Prediction</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Supervised Random Forest Classifier forecasting network service disruptions 15-22.5 minutes prior to threshold breach.
          </p>
        </div>

        {/* Status Pills */}
        <div className="flex items-center gap-4">
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-[10px] text-slate-400">Prediction Horizon</div>
              <div className="font-mono font-bold text-white">15 Steps (~22.5m)</div>
            </div>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="text-[10px] text-slate-400">Primary Classifier</div>
              <div className="font-mono font-bold text-emerald-400">Random Forest</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Probability Gauge & Feature Contribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Current Prediction Card */}
        <div className="noc-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-4">
              <span>Active Imminent Risk Status</span>
              <span className="font-mono">{latest?.site_id} / {latest?.cell_id}</span>
            </div>

            <div className="text-center py-4">
              <div className="text-5xl font-black text-white tracking-tight">
                {latest ? Math.round(latest.fault_probability * 100) : 0}%
              </div>
              <div className="text-xs font-semibold text-slate-400 mt-1">Fault Probability</div>

              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold border">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    latest?.risk_level === 'CRITICAL'
                      ? 'bg-rose-500 animate-ping'
                      : latest?.risk_level === 'HIGH'
                      ? 'bg-amber-400'
                      : 'bg-emerald-400'
                  }`}
                />
                <span className="text-white">RISK LEVEL: {latest?.risk_level || 'LOW'}</span>
              </div>
            </div>

            <div className="mt-6 space-y-2 text-xs border-t border-slate-800 pt-4">
              <div className="flex justify-between text-slate-400">
                <span>Predicted Condition:</span>
                <span className="font-bold text-white">{latest?.fault_type || 'NORMAL'}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Model Confidence:</span>
                <span className="font-mono text-cyan-400">{(latest?.confidence || 0.98) * 100}%</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Anomaly Detection Score:</span>
                <span className="font-mono text-indigo-400">{latest?.anomaly_score.toFixed(3) || '0.000'}</span>
              </div>
            </div>
          </div>

          {/* Test Inference Trigger */}
          <div className="mt-6 pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2">
              <select
                value={selectedSite}
                onChange={(e) => setSelectedSite(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2 py-1 text-xs"
              >
                <option value="SITE-01">SITE-01</option>
                <option value="SITE-02">SITE-02</option>
                <option value="SITE-03">SITE-03</option>
              </select>
              <select
                value={selectedCell}
                onChange={(e) => setSelectedCell(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2 py-1 text-xs"
              >
                <option value="CELL-01">CELL-01</option>
                <option value="CELL-02">CELL-02</option>
                <option value="CELL-03">CELL-03</option>
              </select>
              <button
                onClick={handleRunInference}
                disabled={runningTest}
                className="flex-1 flex items-center justify-center gap-1.5 bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-1 px-3 rounded text-xs transition"
              >
                <Play className="w-3 h-3" />
                {runningTest ? 'Running...' : 'Run Test'}
              </button>
            </div>
            {testResult && (
              <div className="mt-2 text-[11px] text-emerald-400 bg-emerald-950/60 p-2 rounded border border-emerald-800">
                {testResult.message}
              </div>
            )}
          </div>
        </div>

        {/* Center & Right: Fault Probability Trend Chart */}
        <div className="lg:col-span-2 noc-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-bold text-white">Fault Probability & Composite Risk Score Horizon</h2>
                <p className="text-xs text-slate-400">Sequential model outputs showing early precursor ramp-up</p>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="flex items-center gap-1.5 text-rose-400">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400" /> Fault Prob (%)
                </span>
                <span className="flex items-center gap-1.5 text-cyan-400">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Risk Score (%)
                </span>
              </div>
            </div>

            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.5}/>
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#00f0ff" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#94a3b8" domain={[0, 100]} fontSize={10} />
                  <Tooltip contentStyle={{ backgroundColor: '#121722', borderColor: '#1f293d' }} />
                  <Area type="monotone" dataKey="probability" stroke="#f43f5e" fillOpacity={1} fill="url(#colorProb)" name="Fault Probability (%)" />
                  <Area type="monotone" dataKey="risk_score" stroke="#00f0ff" fillOpacity={1} fill="url(#colorRisk)" name="Risk Score (%)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Contributing Features Visualizer */}
          <div className="mt-4 pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-white mb-2">Key Contributing Input Features (SHAP / Gini Proxy)</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {featureList.slice(0, 4).map((f) => (
                <div key={f.feature} className="p-2 rounded bg-slate-900 border border-slate-800 text-xs">
                  <div className="text-[10px] text-slate-400 truncate">{f.feature}</div>
                  <div className="font-mono font-bold text-cyan-400 mt-0.5">{f.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
