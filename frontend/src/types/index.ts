export interface Machine {
  id: number;
  machine_id: string;
  name: string;
  machine_type: string;
  model_series: string;
  location: string;
  status: 'Active' | 'Warning' | 'Critical' | 'Maintenance' | 'Offline';
  current_cycle: number;
  health_score: number;
  failure_probability: number;
  predicted_rul: number;
  anomaly_score: number;
  is_anomalous: boolean;
  last_seen: string;
  created_at: string;
}

export interface SensorReading {
  cycle: number;
  timestamp: string;
  s2: number;
  s3: number;
  s4: number;
  s7: number;
  s8: number;
  s9: number;
  s11: number;
  s12: number;
  s14: number;
  s15: number;
  s17: number;
  s20: number;
  s21: number;
}

export interface ShapFactor {
  sensor: string;
  sensor_name?: string;
  contribution: number;
  impact: string;
  description: string;
}

export interface Alert {
  id: number;
  machine_id: string;
  severity: 'Critical' | 'Warning' | 'Info';
  alert_type: string;
  title: string;
  description: string;
  recommended_action: string;
  is_acknowledged: boolean;
  created_at: string;
}

export interface MaintenanceRecord {
  id: number;
  machine_id: string;
  maintenance_type: string;
  status: 'Scheduled' | 'In Progress' | 'Completed' | 'Deferred';
  scheduled_date: string;
  completed_date?: string;
  technician: string;
  downtime_hours: number;
  notes: string;
  created_at: string;
}

export interface FleetKPIs {
  total_machines: number;
  healthy_machines: number;
  warning_machines: number;
  critical_machines: number;
  fleet_health_score: number;
  fleet_average_rul: number;
  active_alerts: number;
  critical_alerts: number;
  scheduled_maintenance_orders: number;
}

export interface AnalyticsResponse {
  kpis: FleetKPIs;
  health_distribution: Array<{ name: string; value: number; color: string }>;
  model_benchmarks: any;
}
