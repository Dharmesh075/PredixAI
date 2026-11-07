import React, { useState } from 'react';
import { Alert } from '../types';
import { api } from '../services/api';
import { 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  CheckCircle2, 
  Filter, 
  Wrench, 
  Clock, 
  ShieldAlert
} from 'lucide-react';

interface AlertsPageProps {
  alerts: Alert[];
  onRefresh: () => void;
  onNavigate: (tab: string) => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({
  alerts,
  onRefresh,
  onNavigate
}) => {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [filterAcknowledged, setFilterAcknowledged] = useState<boolean | null>(null);

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity !== 'ALL' && a.severity !== filterSeverity) return false;
    if (filterAcknowledged !== null && a.is_acknowledged !== filterAcknowledged) return false;
    return true;
  });

  const handleAcknowledge = async (alertId: number) => {
    try {
      await api.acknowledgeAlert(alertId);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-white flex items-center gap-2">
            Industrial Alert Management
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-400 font-mono border border-red-500/30">
              {alerts.filter((a) => !a.is_acknowledged).length} Unacknowledged
            </span>
          </h1>
          <p className="text-xs text-slate-400">
            Real-time degradation threshold triggers and prescriptive maintenance remediation actions
          </p>
        </div>

        {/* Severity Filters */}
        <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-xl border border-slate-800 text-xs">
          {['ALL', 'Critical', 'Warning', 'Info'].map((s) => (
            <button
              key={s}
              onClick={() => setFilterSeverity(s)}
              className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                filterSeverity === s
                  ? 'bg-sky-500 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800 text-slate-400">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-80" />
            <p className="text-sm font-semibold text-white">No active alerts matching filter</p>
            <p className="text-xs text-slate-500 mt-1">All monitored machines within operating tolerances.</p>
          </div>
        ) : (
          filteredAlerts.map((a) => {
            const isCrit = a.severity === 'Critical';
            const isWarn = a.severity === 'Warning';
            return (
              <div
                key={a.id}
                className={`p-5 rounded-2xl border transition-all ${
                  isCrit
                    ? 'bg-red-950/20 border-red-500/40 shadow-sm shadow-red-500/5'
                    : (isWarn ? 'bg-amber-950/15 border-amber-500/30' : 'bg-slate-900 border-slate-800')
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className={`p-2.5 rounded-xl mt-0.5 ${
                      isCrit ? 'bg-red-500/20 text-red-400' : (isWarn ? 'bg-amber-500/20 text-amber-400' : 'bg-sky-500/20 text-sky-400')
                    }`}>
                      {isCrit ? <AlertTriangle className="w-5 h-5" /> : (isWarn ? <AlertCircle className="w-5 h-5" /> : <Info className="w-5 h-5" />)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2.5">
                        <span className="font-mono font-bold text-white text-sm">{a.machine_id}</span>
                        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${
                          isCrit
                            ? 'bg-red-500/20 text-red-400 border-red-500/30'
                            : (isWarn ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-sky-500/20 text-sky-400 border-sky-500/30')
                        }`}>
                          {a.severity}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          {new Date(a.created_at).toLocaleString()}
                        </span>
                        {a.is_acknowledged && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-semibold flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> Acknowledged
                          </span>
                        )}
                      </div>
                      <h3 className="text-sm font-bold text-white mt-1">{a.title}</h3>
                      <p className="text-xs text-slate-300 mt-1 leading-relaxed">{a.description}</p>

                      {/* Recommended Industrial Action Box */}
                      {a.recommended_action && (
                        <div className="mt-3 p-3 rounded-xl bg-black/40 border border-slate-800 text-xs text-slate-200">
                          <strong className="text-sky-400 block mb-0.5 font-mono text-[11px] uppercase">
                            Prescribed Industrial SOP:
                          </strong>
                          {a.recommended_action}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row items-end gap-2 shrink-0">
                    {!a.is_acknowledged && (
                      <button
                        onClick={() => handleAcknowledge(a.id)}
                        className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 text-xs font-medium border border-slate-700 transition-colors"
                      >
                        Acknowledge
                      </button>
                    )}
                    <button
                      onClick={() => onNavigate('maintenance')}
                      className="px-3 py-1.5 rounded-lg bg-sky-500/20 border border-sky-500/40 text-sky-300 hover:bg-sky-500/30 text-xs font-semibold transition-colors flex items-center gap-1.5"
                    >
                      <Wrench className="w-3.5 h-3.5" />
                      <span>Dispatch Team</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
