import React from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  Cpu, 
  AlertTriangle, 
  Wrench, 
  BarChart3, 
  Box, 
  Bot,
  ShieldCheck
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenAssistant: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, onOpenAssistant }) => {
  const menuItems = [
    { id: 'overview', label: 'Fleet Overview', icon: LayoutDashboard },
    { id: 'monitoring', label: 'Machine Telemetry', icon: Activity },
    { id: 'predictions', label: 'AI Prognostics & SHAP', icon: Cpu },
    { id: 'alerts', label: 'Alert Center', icon: AlertTriangle },
    { id: 'maintenance', label: 'Work Orders & Sched', icon: Wrench },
    { id: 'digital-twin', label: '3D Digital Twin', icon: Box },
    { id: 'analytics', label: 'Model Benchmarks', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-[#0F172A] border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      <div>
        {/* Brand */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold tracking-tight text-white flex items-center gap-1.5">
              Predix<span className="text-sky-400">AI</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 font-semibold">v2.0</span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">Machine Health OS</div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="p-3 space-y-1">
          <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Platform Modules
          </div>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-500/15 text-sky-400 shadow-sm border border-sky-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* AI Assistant Callout & Status */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        <button
          onClick={onOpenAssistant}
          className="w-full flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-sky-950/80 to-slate-900 border border-sky-500/30 text-left hover:border-sky-400/60 transition-all group"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-sky-500/20 flex items-center justify-center text-sky-400 group-hover:scale-105 transition-transform">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-white">AI Diagnostics</div>
              <div className="text-[10px] text-slate-400">Ask Root-Cause LLM</div>
            </div>
          </div>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
          </span>
        </button>

        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono px-1">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Models Online
          </span>
          <span className="text-emerald-400 font-semibold">99.8% Uptime</span>
        </div>
      </div>
    </aside>
  );
};
