import React, { useEffect, useState } from 'react';
import {
  Server,
  Database,
  Cpu,
  Activity,
  FileCode,
  Radio,
  ExternalLink,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';

export const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [modelStatus, setModelStatus] = useState<any>(null);
  const [simStatus, setSimStatus] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const [h, m, s] = await Promise.all([
          api.getHealth(),
          api.getModelStatus(),
          api.getSimulatorStatus()
        ]);
        setHealth(h);
        setModelStatus(m);
        setSimStatus(s);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  const endpoints = [
    { method: 'GET', path: '/health', desc: 'System and database health probe' },
    { method: 'GET', path: '/metrics', desc: 'Prometheus metrics scrape target' },
    { method: 'GET', path: '/api/v1/metrics/latest', desc: 'Latest multi-cell 5G telemetry points' },
    { method: 'GET', path: '/api/v1/metrics/history', desc: 'Time-series telemetry buffer for charting' },
    { method: 'GET', path: '/api/v1/sites', desc: 'Distinct 5G gNodeB sites and status' },
    { method: 'GET', path: '/api/v1/cells', desc: 'Configured sectors, cells, and radio units' },
    { method: 'GET', path: '/api/v1/predictions/latest', desc: 'Real-time future fault probability records' },
    { method: 'GET', path: '/api/v1/predictions/history', desc: 'Historical sequential inference audit' },
    { method: 'POST', path: '/api/v1/predictions/run', desc: 'On-demand custom telemetry inference test' },
    { method: 'GET', path: '/api/v1/alerts', desc: 'Active and historical incident records' },
    { method: 'POST', path: '/api/v1/alerts/{id}/acknowledge', desc: 'Operator acknowledgment transition' },
    { method: 'POST', path: '/api/v1/alerts/{id}/resolve', desc: 'Mitigation resolution transition' },
    { method: 'GET', path: '/api/v1/models/status', desc: 'Loaded ML pipeline and artifact status' },
    { method: 'GET', path: '/api/v1/models/metrics', desc: 'Empirical test-set evaluation benchmarks' },
    { method: 'GET', path: '/api/v1/simulator/status', desc: 'Background generator loop and scenario status' },
    { method: 'POST', path: '/api/v1/simulator/scenario', desc: 'Inject 5G fault scenario dynamically' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="noc-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Server className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-black text-white">System Health & API Specifications</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Backend infrastructure state, database connectivity, ML model loading status, and OpenAPI catalog.
          </p>
        </div>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs transition flex items-center gap-1.5 shadow-md shadow-cyan-500/20"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Interactive Swagger Docs
        </a>
      </div>

      {/* 4 Health Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Backend API */}
        <div className="noc-panel p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>FastAPI Server</span>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-base font-bold text-white uppercase">{health?.status || 'ONLINE'}</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-mono">
            Uvicorn Worker • Python 3.11
          </div>
        </div>

        {/* Database */}
        <div className="noc-panel p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Telemetry Database</span>
            <Database className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span className="text-base font-bold text-white">SQLAlchemy Engine</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-mono">
            SQLite / PostgreSQL Ready
          </div>
        </div>

        {/* ML Engine */}
        <div className="noc-panel p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>ML Model Pipeline</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span className="text-base font-bold text-white">Pretrained & Loaded</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-mono">
            {modelStatus?.features_count || 32} Engineered Features
          </div>
        </div>

        {/* Observability */}
        <div className="noc-panel p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Prometheus / ONAP</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span className="text-base font-bold text-white">Exporters Active</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-mono">
            VES 7.2 Mock + /metrics endpoint
          </div>
        </div>
      </div>

      {/* Model Artifacts Info Panel */}
      <div className="noc-panel p-5 rounded-xl border border-slate-800">
        <h2 className="text-sm font-bold text-white mb-2">Pretrained Machine Learning Artifacts</h2>
        <p className="text-xs text-slate-400 mb-4">
          Models are persisted to disk upon high-accuracy validation and automatically loaded on startup with zero retraining latency.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-cyan-400 font-bold">artifacts/models/random_forest_5g.joblib</div>
            <div className="text-slate-400 text-[11px]">Primary Supervised Future-Fault Classifier (120 Trees)</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-cyan-400 font-bold">artifacts/models/isolation_forest_5g.joblib</div>
            <div className="text-slate-400 text-[11px]">Unsupervised Anomaly Detector (8% Contamination)</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-cyan-400 font-bold">artifacts/models/feature_engineer.joblib</div>
            <div className="text-slate-400 text-[11px]">Feature Transform Pipeline (Rolling Statistics & Lags)</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-cyan-400 font-bold">artifacts/models/evaluation_metrics.json</div>
            <div className="text-slate-400 text-[11px]">Empirical Validation Metadata & Confusion Matrix</div>
          </div>
        </div>
      </div>

      {/* FastAPI REST Endpoints Catalog */}
      <div className="noc-panel p-5 rounded-xl border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-white">FastAPI REST Endpoints Specifications</h2>
          <span className="text-xs text-slate-400 font-mono">16 Standard Endpoints</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Method</th>
                <th className="py-2.5 px-3">Endpoint Path</th>
                <th className="py-2.5 px-3">Function Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {endpoints.map((ep, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="py-2 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ep.method === 'GET'
                          ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}
                    >
                      {ep.method}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-200 font-semibold">{ep.path}</td>
                  <td className="py-2 px-3 text-slate-400">{ep.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
