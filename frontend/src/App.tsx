import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DigitalTwin } from './components/DigitalTwin';
import { AssistantDrawer } from './components/AssistantDrawer';
import { OverviewPage } from './pages/OverviewPage';
import { MachineMonitoringPage } from './pages/MachineMonitoringPage';
import { PredictionsPage } from './pages/PredictionsPage';
import { AlertsPage } from './pages/AlertsPage';
import { MaintenancePage } from './pages/MaintenancePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { api } from './services/api';
import { Machine, Alert, MaintenanceRecord, FleetKPIs, AnalyticsResponse } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedMachineId, setSelectedMachineId] = useState<string>('ENG-001');
  const [isAssistantOpen, setIsAssistantOpen] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  // Data states
  const [machines, setMachines] = useState<Machine[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const defaultKpis: FleetKPIs = {
    total_machines: machines.length || 6,
    healthy_machines: machines.filter((m) => m.health_score >= 80).length || 4,
    warning_machines: machines.filter((m) => m.health_score >= 40 && m.health_score < 80).length || 1,
    critical_machines: machines.filter((m) => m.health_score < 40).length || 1,
    fleet_health_score: 83.2,
    fleet_average_rul: 112.4,
    active_alerts: alerts.filter((a) => !a.is_acknowledged).length || 2,
    critical_alerts: alerts.filter((a) => a.severity === 'Critical' && !a.is_acknowledged).length || 1,
    scheduled_maintenance_orders: maintenance.filter((m) => m.status === 'Scheduled').length || 2
  };

  const loadAllData = async () => {
    try {
      const [machs, alrts, maints, anas] = await Promise.all([
        api.getMachines(),
        api.getAlerts(),
        api.getMaintenanceRecords(),
        api.getAnalytics()
      ]);
      setMachines(machs);
      setAlerts(alrts);
      setMaintenance(maints);
      setAnalytics(anas);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Telemetry stream simulation timer
  useEffect(() => {
    let interval: any;
    if (isStreaming) {
      interval = setInterval(async () => {
        // Send a realistic cycle increment for the selected machine
        const baseSensors = {
          machine_id: selectedMachineId,
          cycle: Math.floor(Math.random() * 50) + 100,
          s2: 642.0 + Math.random() * 1.5,
          s3: 1588.0 + Math.random() * 4.0,
          s4: 1403.0 + Math.random() * 3.5,
          s7: 553.0 + Math.random() * 1.5,
          s8: 2388.05 + Math.random() * 0.1,
          s9: 9046.0 + Math.random() * 8.0,
          s11: 47.45 + Math.random() * 0.2,
          s12: 521.6 + Math.random() * 1.0,
          s13: 2388.02 + Math.random() * 0.1,
          s14: 8135.0 + Math.random() * 8.0,
          s15: 8.41 + Math.random() * 0.05,
          s17: 392.0 + Math.random() * 1.0,
          s20: 38.9 + Math.random() * 0.3,
          s21: 23.4 + Math.random() * 0.1
        };
        try {
          await api.predictFull(baseSensors);
          loadAllData();
        } catch (e) {
          console.error(e);
        }
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [isStreaming, selectedMachineId]);

  const selectedMachine = machines.find((m) => m.machine_id === selectedMachineId) || machines[0];

  return (
    <div className="flex h-screen bg-[#0B0F17] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAssistant={() => setIsAssistantOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <Header
          onRefresh={loadAllData}
          isStreaming={isStreaming}
          onToggleStreaming={() => setIsStreaming(!isStreaming)}
          activeAlertsCount={alerts.filter((a) => !a.is_acknowledged).length}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'overview' && (
            <OverviewPage
              machines={machines}
              kpis={analytics?.kpis || defaultKpis}
              alerts={alerts}
              onSelectMachine={(id) => setSelectedMachineId(id)}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'monitoring' && (
            <MachineMonitoringPage
              machines={machines}
              selectedMachineId={selectedMachineId}
              onSelectMachineId={setSelectedMachineId}
              onOpenAssistant={() => setIsAssistantOpen(true)}
            />
          )}

          {activeTab === 'predictions' && (
            <PredictionsPage
              machines={machines}
              selectedMachineId={selectedMachineId}
              onSelectMachineId={setSelectedMachineId}
              onOpenAssistant={() => setIsAssistantOpen(true)}
            />
          )}

          {activeTab === 'alerts' && (
            <AlertsPage
              alerts={alerts}
              onRefresh={loadAllData}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'maintenance' && (
            <MaintenancePage
              records={maintenance}
              machines={machines}
              onRefresh={loadAllData}
            />
          )}

          {activeTab === 'digital-twin' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-black text-white">3D Digital Twin Viewer</h1>
                  <p className="text-xs text-slate-400">Interactive Three.js physics & thermal degradation simulation</p>
                </div>
                <select
                  value={selectedMachineId}
                  onChange={(e) => setSelectedMachineId(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-xs text-slate-200 font-mono"
                >
                  {machines.map((m) => (
                    <option key={m.machine_id} value={m.machine_id}>
                      {m.machine_id} ({m.health_score.toFixed(0)}% Health)
                    </option>
                  ))}
                </select>
              </div>
              <DigitalTwin machine={selectedMachine} />
            </div>
          )}

          {activeTab === 'analytics' && (
            <AnalyticsPage analytics={analytics} />
          )}
        </main>
      </div>

      {/* Floating AI Maintenance Assistant Drawer */}
      <AssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        selectedMachine={selectedMachine}
      />
    </div>
  );
};
export default App;
