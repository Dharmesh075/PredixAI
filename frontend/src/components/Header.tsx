import React from 'react';
import { Radio, RefreshCw, Bell, Search, ShieldAlert, Cpu } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  isStreaming: boolean;
  onToggleStreaming: () => void;
  activeAlertsCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  onRefresh,
  isStreaming,
  onToggleStreaming,
  activeAlertsCount
}) => {
  return (
    <header className="h-16 bg-[#0F172A]/90 backdrop-blur border-b border-slate-800 px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search equipment ID, unit, location, or tag..."
            className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Live IoT Telemetry Simulator Toggle */}
        <button
          onClick={onToggleStreaming}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold font-mono transition-all border ${
            isStreaming
              ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400 shadow-sm shadow-emerald-500/10'
              : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-800'
          }`}
        >
          <Radio className={`w-3.5 h-3.5 ${isStreaming ? 'animate-pulse text-emerald-400' : 'text-slate-400'}`} />
          <span>{isStreaming ? 'LIVE TELEMETRY ACTIVE' : 'STREAM TELEMETRY'}</span>
        </button>

        {/* Manual Refresh */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
          title="Refresh Data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Alerts Pill */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <div className="relative p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300">
            <Bell className="w-4 h-4" />
            {activeAlertsCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white font-mono text-[10px] font-bold rounded-full flex items-center justify-center animate-radar">
                {activeAlertsCount}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span className="font-mono text-slate-300 text-[11px]">NASA C-MAPSS FD001</span>
          </div>
        </div>
      </div>
    </header>
  );
};
