import React, { useState } from 'react';
import { MaintenanceRecord, Machine } from '../types';
import { api } from '../services/api';
import { 
  Wrench, 
  Calendar, 
  Clock, 
  UserCheck, 
  Plus, 
  CheckCircle2, 
  AlertCircle,
  FileText
} from 'lucide-react';

interface MaintenancePageProps {
  records: MaintenanceRecord[];
  machines: Machine[];
  onRefresh: () => void;
}

export const MaintenancePage: React.FC<MaintenancePageProps> = ({
  records,
  machines,
  onRefresh
}) => {
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    machine_id: machines[0]?.machine_id || 'ENG-001',
    maintenance_type: 'Preventive Inspection',
    scheduled_date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
    technician: 'Senior Field Engineer',
    downtime_hours: 4.0,
    notes: 'Scheduled inspection based on predictive model recommendation.'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.scheduleMaintenance({
        ...formData,
        scheduled_date: new Date(formData.scheduled_date).toISOString()
      });
      setShowModal(false);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const handleComplete = async (recordId: number) => {
    try {
      await api.updateMaintenanceStatus(recordId, 'Completed');
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const totalDowntime = records.reduce((acc, r) => acc + (r.downtime_hours || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-white flex items-center gap-2">
            Predictive Maintenance Work Orders
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 font-mono border border-sky-500/30">
              {records.length} Work Orders
            </span>
          </h1>
          <p className="text-xs text-slate-400">
            Intelligent maintenance dispatching, downtime tracking, and overhaul lifecycle management
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-xl bg-sky-500 text-white text-xs font-semibold hover:bg-sky-400 transition-colors flex items-center gap-2 shadow-lg shadow-sky-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Schedule Work Order</span>
        </button>
      </div>

      {/* KPI Stats Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono">Scheduled Jobs</div>
            <div className="text-xl font-extrabold text-white font-mono">
              {records.filter((r) => r.status === 'Scheduled').length}
            </div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono">Completed Overhauls</div>
            <div className="text-xl font-extrabold text-white font-mono">
              {records.filter((r) => r.status === 'Completed').length}
            </div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 uppercase font-mono">Total Estimated Downtime</div>
            <div className="text-xl font-extrabold text-white font-mono">{totalDowntime.toFixed(1)} hrs</div>
          </div>
        </div>
      </div>

      {/* Work Orders Table */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
            Active Maintenance Schedules
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="p-3.5 pl-6">Equipment</th>
                <th className="p-3.5">Maintenance Type</th>
                <th className="p-3.5">Scheduled Date</th>
                <th className="p-3.5">Assigned Technician</th>
                <th className="p-3.5">Downtime</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 pr-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-200">
              {records.map((r) => {
                const isCompleted = r.status === 'Completed';
                return (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 pl-6 font-mono font-bold text-white">{r.machine_id}</td>
                    <td className="p-3.5 font-medium">{r.maintenance_type}</td>
                    <td className="p-3.5 font-mono text-slate-400">
                      {new Date(r.scheduled_date).toLocaleDateString()}
                    </td>
                    <td className="p-3.5">{r.technician}</td>
                    <td className="p-3.5 font-mono">{r.downtime_hours} hrs</td>
                    <td className="p-3.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}>
                        {r.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-3.5 pr-6 text-right">
                      {!isCompleted ? (
                        <button
                          onClick={() => handleComplete(r.id)}
                          className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 font-semibold text-[11px] border border-emerald-500/30 transition-colors"
                        >
                          Mark Completed
                        </button>
                      ) : (
                        <span className="text-[11px] text-slate-500 font-mono">Resolved</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal for Scheduling Work Order */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-4">Schedule Predictive Maintenance</h3>
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1 font-mono">Target Equipment</label>
                <select
                  value={formData.machine_id}
                  onChange={(e) => setFormData({ ...formData, machine_id: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                >
                  {machines.map((m) => (
                    <option key={m.machine_id} value={m.machine_id}>
                      {m.machine_id} ({m.name})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-mono">Maintenance Type</label>
                <select
                  value={formData.maintenance_type}
                  onChange={(e) => setFormData({ ...formData, maintenance_type: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                >
                  <option value="Preventive Inspection">Preventive Inspection</option>
                  <option value="HPC Stage Overhaul">HPC Stage Overhaul</option>
                  <option value="Borescope Inspection">Borescope Inspection</option>
                  <option value="Sensor Transducer Calibration">Sensor Transducer Calibration</option>
                  <option value="Turbine Rotor Balance">Turbine Rotor Balance</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-mono">Target Date</label>
                <input
                  type="date"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1 font-mono">Technician</label>
                  <input
                    type="text"
                    value={formData.technician}
                    onChange={(e) => setFormData({ ...formData, technician: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1 font-mono">Downtime (Hours)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.downtime_hours}
                    onChange={(e) => setFormData({ ...formData, downtime_hours: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1 font-mono">Work Order Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-white"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-sky-500 text-white font-semibold hover:bg-sky-400"
                >
                  Confirm Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
