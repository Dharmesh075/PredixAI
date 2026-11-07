import React, { useEffect, useState } from 'react';
import { Machine, SensorReading } from '../types';
import { api } from '../services/api';
import { 
  Activity, 
  Thermometer, 
  Gauge, 
  Wind, 
  Zap, 
  Clock, 
  Flame, 
  TrendingUp,
  Cpu
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area 
} from 'recharts';

interface MachineMonitoringPageProps {
  machines: Machine[];
  selectedMachineId: string;
  onSelectMachineId: (id: string) => void;
  onOpenAssistant: () => void;
}

export const MachineMonitoringPage: React.FC<MachineMonitoringPageProps> = ({
  machines,
  selectedMachineId,
  onSelectMachineId,
  onOpenAssistant
}) => {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedMachineId) return;
    setLoading(true);
    api.getMachineDetails(selectedMachineId)
      .then((data) => setDetails(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedMachineId]);

  const machine: Machine | undefined = machines.find((m) => m.machine_id === selectedMachineId) || details?.machine;
  const readings: SensorReading[] = details?.recent_readings || [];

  const latestReading = readings.length > 0 ? readings[readings.length - 1] : null;

  return (
    <div className="space-y-6">
      {/* Top Selector Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-sky-500/20 flex items-center justify-center text-sky-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black text-white">{machine?.machine_id || 'ENG-001'}</h2>
              <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
                (machine?.health_score || 100) < 40
                  ? 'bg-red-500/20 text-red-400 border-red-500/30'
                  : ((machine?.health_score || 100) < 80 ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30')
              }`}>
                {machine?.status.toUpperCase() || 'ACTIVE'}
              </span>
            </div>
            <p className="text-xs text-slate-400">{machine?.name} • {machine?.location}</p>
          </div>
        </div>

        {/* Machine Dropdown & Assistant Button */}
        <div className="flex items-center gap-3">
          <select
            value={selectedMachineId}
            onChange={(e) => onSelectMachineId(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-sky-500"
          >
            {machines.map((m) => (
              <option key={m.machine_id} value={m.machine_id}>
                {m.machine_id} - {m.name} ({m.health_score.toFixed(0)}%)
              </option>
            ))}
          </select>

          <button
            onClick={onOpenAssistant}
            className="px-3.5 py-2 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 text-xs font-semibold hover:bg-sky-500/25 transition-colors font-mono flex items-center gap-1.5"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>AI Diagnostics</span>
          </button>
        </div>
      </div>

      {/* Live Sensor KPI Gauges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Core Temperature T30 */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>HPC OUTLET TEMP (T30)</span>
            <Thermometer className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1 font-mono">
            <span className="text-2xl font-black text-white">{latestReading?.s3?.toFixed(1) || '1589.7'}</span>
            <span className="text-xs text-slate-500">°R</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1 font-mono">Nominal: 1580 - 1595 °R</div>
        </div>

        {/* LPT Temperature T50 */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>LPT OUTLET TEMP (T50)</span>
            <Flame className="w-4 h-4 text-red-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1 font-mono">
            <span className="text-2xl font-black text-white">{latestReading?.s4?.toFixed(1) || '1404.2'}</span>
            <span className="text-xs text-slate-500">°R</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1 font-mono">Primary thermal wear signal</div>
        </div>

        {/* HPC Static Pressure Ps30 */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>STATIC PRESSURE (Ps30)</span>
            <Gauge className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1 font-mono">
            <span className="text-2xl font-black text-white">{latestReading?.s11?.toFixed(2) || '47.47'}</span>
            <span className="text-xs text-slate-500">psia</span>
          </div>
          <div className="text-[10px] text-cyan-400 mt-1 font-mono">High degradation correlation</div>
        </div>

        {/* Fuel Flow Ratio */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>FUEL FLOW RATIO (phi)</span>
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1 font-mono">
            <span className="text-2xl font-black text-white">{latestReading?.s12?.toFixed(2) || '521.66'}</span>
            <span className="text-xs text-slate-500">pps/psi</span>
          </div>
          <div className="text-[10px] text-emerald-400 mt-1 font-mono">Burner efficiency ratio</div>
        </div>
      </div>

      {/* Degradation Time-Series Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Temperature Drift */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white text-sm">Thermal Profile Over Cycles</h3>
              <p className="text-[11px] text-slate-400 font-mono">HPC Outlet Temp (s3) vs LPT Outlet Temp (s4)</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              {readings.length} data points
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={readings}>
                <defs>
                  <linearGradient id="colorT30" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#38BDF8" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorT50" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="cycle" stroke="#64748B" fontSize={11} tickFormatter={(val) => `C${val}`} />
                <YAxis stroke="#64748B" fontSize={11} domain={['auto', 'auto']} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                <Area type="monotone" dataKey="s3" name="T30 Temp" stroke="#38BDF8" fillOpacity={1} fill="url(#colorT30)" />
                <Area type="monotone" dataKey="s4" name="T50 Temp" stroke="#F59E0B" fillOpacity={1} fill="url(#colorT50)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Pressure & Speed Dynamics */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white text-sm">Pressure & Speed Dynamics</h3>
              <p className="text-[11px] text-slate-400 font-mono">HPC Static Pressure (s11) & Physical Core RPM (s9)</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Sensor s11 & s9
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={readings}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="cycle" stroke="#64748B" fontSize={11} tickFormatter={(val) => `C${val}`} />
                <YAxis stroke="#64748B" fontSize={11} domain={['auto', 'auto']} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                <Line type="monotone" dataKey="s11" name="Ps30 Pressure" stroke="#10B981" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="s12" name="Fuel Flow" stroke="#A855F7" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
