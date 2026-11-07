import { Machine, Alert, MaintenanceRecord, AnalyticsResponse, ShapFactor } from '../types';

const API_BASE = '/api';

export const api = {
  // Machines
  getMachines: async (): Promise<Machine[]> => {
    const res = await fetch(`${API_BASE}/machines`);
    if (!res.ok) throw new Error('Failed to fetch machines');
    return res.json();
  },

  getMachineDetails: async (machineId: string) => {
    const res = await fetch(`${API_BASE}/machines/${machineId}`);
    if (!res.ok) throw new Error(`Failed to fetch details for ${machineId}`);
    return res.json();
  },

  registerMachine: async (data: Partial<Machine>): Promise<Machine> => {
    const res = await fetch(`${API_BASE}/machines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to register machine');
    return res.json();
  },

  // Predictions
  predictFull: async (reading: any) => {
    const res = await fetch(`${API_BASE}/predict/full`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reading)
    });
    if (!res.ok) throw new Error('Prediction failed');
    return res.json();
  },

  // Alerts
  getAlerts: async (machineId?: string): Promise<Alert[]> => {
    const url = machineId ? `${API_BASE}/alerts?machine_id=${machineId}` : `${API_BASE}/alerts`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  acknowledgeAlert: async (alertId: number): Promise<Alert> => {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'PATCH'
    });
    if (!res.ok) throw new Error('Failed to acknowledge alert');
    return res.json();
  },

  // Maintenance
  getMaintenanceRecords: async (machineId?: string): Promise<MaintenanceRecord[]> => {
    const url = machineId ? `${API_BASE}/maintenance?machine_id=${machineId}` : `${API_BASE}/maintenance`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch maintenance records');
    return res.json();
  },

  scheduleMaintenance: async (record: Partial<MaintenanceRecord>): Promise<MaintenanceRecord> => {
    const res = await fetch(`${API_BASE}/maintenance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record)
    });
    if (!res.ok) throw new Error('Failed to schedule maintenance');
    return res.json();
  },

  updateMaintenanceStatus: async (recordId: number, status: string) => {
    const res = await fetch(`${API_BASE}/maintenance/${recordId}/status?new_status=${status}`, {
      method: 'PATCH'
    });
    if (!res.ok) throw new Error('Failed to update maintenance status');
    return res.json();
  },

  // Analytics
  getAnalytics: async (): Promise<AnalyticsResponse> => {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  // AI Maintenance Assistant
  askAssistant: async (query: string, machineId?: string) => {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, machine_id: machineId })
    });
    if (!res.ok) throw new Error('Assistant query failed');
    return res.json();
  }
};
