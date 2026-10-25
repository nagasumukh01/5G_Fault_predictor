import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Search,
  Check,
  CheckCheck,
  ShieldAlert,
  Radio,
  Sliders,
  XCircle,
  FileText
} from 'lucide-react';
import { api } from '../services/api';
import { AlertRecord } from '../types';

export const AlertCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<AlertRecord | null>(null);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [operatorNotes, setOperatorNotes] = useState<string>('Investigating gNodeB telemetry parameters');
  const [resolveNotes, setResolveNotes] = useState<string>('Applied slice reconfiguration and cleared PRB congestion');
  const [isResolveModalOpen, setIsResolveModalOpen] = useState<boolean>(false);

  const fetchAlerts = async () => {
    try {
      const data = await api.getAlerts({
        status: statusFilter,
        severity: severityFilter,
        limit: 50
      });
      setAlerts(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, [statusFilter, severityFilter]);

  const handleAcknowledge = async (alertId: string) => {
    setActionLoading(true);
    try {
      await api.acknowledgeAlert(alertId, 'NOC Lead Engineer', operatorNotes);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async (alertId: string) => {
    setActionLoading(true);
    try {
      await api.resolveAlert(alertId, 'NOC Lead Engineer', resolveNotes);
      setIsResolveModalOpen(false);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.alert_id.toLowerCase().includes(q) ||
      a.site_id.toLowerCase().includes(q) ||
      a.cell_id.toLowerCase().includes(q) ||
      a.fault_type.toLowerCase().includes(q) ||
      a.message.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header & Incident Stats */}
      <div className="noc-panel p-6 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-black text-white">5G NOC Incident & Alert Command Center</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Complete incident lifecycle management with proactive root-cause analysis, deduplication, and mitigation advisories.
          </p>
        </div>

        {/* Status Count Pills */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300">
            Active: {alerts.filter(a => a.status === 'ACTIVE').length}
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-800 text-amber-300">
            Ack'd: {alerts.filter(a => a.status === 'ACKNOWLEDGED').length}
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300">
            Resolved: {alerts.filter(a => a.status === 'RESOLVED').length}
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="noc-panel p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {/* Status Tabs */}
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs font-medium">
            {['ALL', 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-md transition ${
                  statusFilter === st ? 'bg-cyan-500 text-black font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded-md px-2.5 py-1.5 text-xs"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="WARNING">Warning Only</option>
          </select>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search alerts by site, cell, fault..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded-md pl-9 pr-3 py-1.5 text-xs w-64 focus:outline-none focus:border-cyan-400"
          />
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="noc-panel p-12 text-center rounded-xl border border-slate-800">
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-60" />
            <h3 className="text-base font-bold text-white">No Incidents Found</h3>
            <p className="text-xs text-slate-400 mt-1">
              All 5G cells are currently performing within nominal SLA thresholds.
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`noc-panel p-5 rounded-xl border transition ${
                alert.status === 'ACTIVE'
                  ? alert.severity === 'CRITICAL'
                    ? 'border-rose-700/80 bg-rose-950/20'
                    : 'border-amber-700/80 bg-amber-950/20'
                  : alert.status === 'ACKNOWLEDGED'
                  ? 'border-indigo-700/60 bg-indigo-950/20'
                  : 'border-slate-800 bg-[#0e131d]/60 opacity-80'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                {/* Left: Metadata & Details */}
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400">
                      {alert.alert_id}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-900 text-rose-200 border border-rose-700'
                          : 'bg-amber-900 text-amber-200 border border-amber-700'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        alert.status === 'ACTIVE'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                          : alert.status === 'ACKNOWLEDGED'
                          ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      }`}
                    >
                      {alert.status}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {alert.site_id} • {alert.cell_id} • {alert.component_id}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white tracking-wide">
                    {alert.message}
                  </h3>

                  {/* Telemetry Snapshot Metrics */}
                  <div className="flex flex-wrap gap-4 pt-2 text-xs font-mono text-slate-300">
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      RSRP: <strong className="text-cyan-400">{alert.metrics_snapshot?.rsrp_dbm ?? 'N/A'} dBm</strong>
                    </span>
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      Latency: <strong className="text-rose-400">{alert.metrics_snapshot?.latency_ms ?? 'N/A'} ms</strong>
                    </span>
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      Loss: <strong className="text-amber-400">{alert.metrics_snapshot?.packet_loss_pct ?? 'N/A'}%</strong>
                    </span>
                    <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800">
                      Throughput: <strong className="text-emerald-400">{alert.metrics_snapshot?.throughput_mbps ?? 'N/A'} Mbps</strong>
                    </span>
                  </div>

                  {/* Recommended Actions */}
                  {alert.recommended_actions && alert.recommended_actions.length > 0 && (
                    <div className="mt-3 pt-2 text-xs">
                      <span className="font-semibold text-cyan-400 flex items-center gap-1">
                        <Sliders className="w-3.5 h-3.5" /> Recommended Remediation Actions:
                      </span>
                      <ul className="list-disc list-inside mt-1 space-y-0.5 text-slate-300">
                        {alert.recommended_actions.map((act, idx) => (
                          <li key={idx}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Audit Trail Notes */}
                  {alert.resolution_notes && (
                    <div className="mt-2 text-xs bg-slate-900/80 p-2 rounded border border-slate-800 text-slate-400 font-mono">
                      {alert.resolution_notes}
                    </div>
                  )}
                </div>

                {/* Right: Actions */}
                <div className="flex flex-col items-end gap-2 text-right">
                  <span className="text-xs text-slate-400 font-mono">
                    {new Date(alert.timestamp).toLocaleString()}
                  </span>

                  <div className="flex items-center gap-2 mt-2">
                    {alert.status === 'ACTIVE' && (
                      <button
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        disabled={actionLoading}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-sm"
                      >
                        <Check className="w-3.5 h-3.5" /> Acknowledge
                      </button>
                    )}

                    {alert.status !== 'RESOLVED' && (
                      <button
                        onClick={() => {
                          setSelectedAlert(alert);
                          setIsResolveModalOpen(true);
                        }}
                        disabled={actionLoading}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-sm"
                      >
                        <CheckCheck className="w-3.5 h-3.5" /> Resolve
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Resolve Modal */}
      {isResolveModalOpen && selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="noc-panel p-6 rounded-xl border border-slate-700 w-full max-w-md space-y-4 animate-scale-up">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCheck className="w-5 h-5 text-emerald-400" />
              Resolve Incident: {selectedAlert.alert_id}
            </h3>
            <p className="text-xs text-slate-400">
              Document root-cause confirmation and mitigation actions taken before closing this alert.
            </p>

            <textarea
              value={resolveNotes}
              onChange={(e) => setResolveNotes(e.target.value)}
              rows={3}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 font-mono"
            />

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsResolveModalOpen(false)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => handleResolve(selectedAlert.alert_id)}
                disabled={actionLoading}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1"
              >
                Confirm Resolution
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
