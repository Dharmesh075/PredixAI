import React from 'react';
import { Machine, FleetKPIs, Alert } from '../types';
import { 
  Cpu, 
  Activity, 
  AlertTriangle, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  ArrowUpRight, 
  ArrowRight,
  TrendingUp,
  Flame
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface OverviewPageProps {
  machines: Machine[];
  kpis: FleetKPIs;
  alerts: Alert[];
  onSelectMachine: (machineId: string) => void;
  onNavigate: (tab: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  machines,
  kpis,
  alerts,
  onSelectMachine,
  onNavigate
}) => {
  const pieData = [
    { name: 'Healthy', value: kpis.healthy_machines, color: '#10B981' },
    { name: 'Warning', value: kpis.warning_machines, color: '#F59E0B' },
    { name: 'Critical', value: kpis.critical_machines, color: '#EF4444' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
            Fleet Health Overview
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono border border-emerald-500/20">
              Continuous Ingestion
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-sensor telemetry, RUL prognostics, and automated maintenance scheduling
          </p>
        </div>
        <button
          onClick={() => onNavigate('digital-twin')}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white text-xs font-semibold hover:shadow-lg hover:shadow-sky-500/25 transition-all flex items-center gap-2"
        >
          <span>Launch 3D Digital Twin</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Equipment */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold tracking-wider uppercase font-mono">Monitored Assets</span>
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{kpis.total_machines}</span>
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-0.5">
              <TrendingUp className="w-3 h-3" /> 100% Online
            </span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2 font-mono">Turbofan C-MAPSS Fleet</div>
        </div>

        {/* Fleet Health Score */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold tracking-wider uppercase font-mono">Fleet Health Index</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{kpis.fleet_health_score}%</span>
            <span className="text-xs text-slate-400 font-medium">Composite score</span>
          </div>
          {/* Health progress bar */}
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${kpis.fleet_health_score}%` }}
            />
          </div>
        </div>

        {/* Average RUL */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold tracking-wider uppercase font-mono">Fleet Avg RUL</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{kpis.fleet_average_rul}</span>
            <span className="text-xs text-slate-400 font-mono">cycles</span>
          </div>
          <div className="text-[11px] text-amber-400 mt-2 font-mono">
            {kpis.critical_machines > 0 ? `${kpis.critical_machines} unit near critical wear` : 'All units within safety margins'}
          </div>
        </div>

        {/* Active Alerts */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold tracking-wider uppercase font-mono">Active Warnings</span>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{kpis.active_alerts}</span>
            {kpis.critical_alerts > 0 && (
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                {kpis.critical_alerts} CRITICAL
              </span>
            )}
          </div>
          <div className="text-[11px] text-slate-400 mt-2 font-mono">
            {kpis.scheduled_maintenance_orders} work orders in progress
          </div>
        </div>
      </div>

      {/* Main Grid: Machine Fleet Cards + Health Distribution Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Machine Cards Fleet (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 font-mono">
              Live Machinery Fleet Status
            </h2>
            <span className="text-xs text-slate-400 font-mono">Click to inspect machine</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {machines.map((m) => {
              const isCrit = m.health_score < 40;
              const isWarn = m.health_score >= 40 && m.health_score < 80;
              return (
                <div
                  key={m.machine_id}
                  onClick={() => {
                    onSelectMachine(m.machine_id);
                    onNavigate('monitoring');
                  }}
                  className={`p-4 rounded-xl bg-slate-900/90 border transition-all cursor-pointer group hover:scale-[1.01] ${
                    isCrit
                      ? 'border-red-500/50 hover:border-red-400 shadow-lg shadow-red-500/5'
                      : (isWarn ? 'border-amber-500/40 hover:border-amber-400' : 'border-slate-800 hover:border-sky-500/50')
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-white text-base group-hover:text-sky-400 transition-colors">
                          {m.machine_id}
                        </span>
                        <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
                          isCrit
                            ? 'bg-red-500/20 text-red-400 border-red-500/30'
                            : (isWarn ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30')
                        }`}>
                          {m.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">{m.name}</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-sky-400 transition-colors" />
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-2 py-2 border-y border-slate-800/80 text-[11px] font-mono">
                    <div>
                      <span className="text-slate-500 block text-[10px]">CYCLE</span>
                      <span className="text-slate-200 font-bold">{m.current_cycle}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">RUL PROGNOSIS</span>
                      <span className={`font-bold ${isCrit ? 'text-red-400' : (isWarn ? 'text-amber-400' : 'text-emerald-400')}`}>
                        {m.predicted_rul.toFixed(0)} cyc
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">FAIL RISK</span>
                      <span className="text-slate-200 font-bold">{(m.failure_probability * 100).toFixed(1)}%</span>
                    </div>
                  </div>

                  {/* Health Bar */}
                  <div className="mt-3">
                    <div className="flex justify-between text-[11px] font-mono mb-1">
                      <span className="text-slate-400">Health Index</span>
                      <span className={`font-bold ${isCrit ? 'text-red-400' : (isWarn ? 'text-amber-400' : 'text-emerald-400')}`}>
                        {m.health_score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          isCrit ? 'bg-red-500' : (isWarn ? 'bg-amber-500' : 'bg-emerald-500')
                        }`}
                        style={{ width: `${Math.min(100, Math.max(5, m.health_score))}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Fleet Health Distribution & Recent Alerts */}
        <div className="space-y-6">
          {/* Health Distribution Donut */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono mb-4">
              Fleet Health Distribution
            </h3>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={65}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 text-xs font-mono mt-2">
              {pieData.map((p) => (
                <div key={p.name} className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }}></span>
                  <span className="text-slate-400">{p.name}: <strong className="text-white">{p.value}</strong></span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Active Alerts */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
                Recent Critical Warnings
              </h3>
              <button
                onClick={() => onNavigate('alerts')}
                className="text-[11px] text-sky-400 hover:underline font-mono"
              >
                View all ({alerts.length})
              </button>
            </div>

            <div className="space-y-2.5">
              {alerts.slice(0, 3).map((a) => (
                <div
                  key={a.id}
                  className={`p-3 rounded-xl border text-xs ${
                    a.severity === 'Critical'
                      ? 'bg-red-950/30 border-red-500/40 text-red-200'
                      : 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                  }`}
                >
                  <div className="flex items-center justify-between font-mono font-bold">
                    <span>{a.machine_id}</span>
                    <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-black/40">
                      {a.severity}
                    </span>
                  </div>
                  <div className="text-slate-300 font-medium mt-1">{a.title}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
