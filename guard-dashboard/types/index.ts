export interface SensorData {
  datetime: string;
  status: 'NORMAL' | 'ANOMALY';
  MAE: number;
  threshold_ratio: number;
  exceed_percent: number;
  is_anomaly: boolean;
  Flow_Rate: number;
  Suction_Pressure: number;
  Discharge_Pressure: number;
  Suction_Temperature: number;
  Discharge_Temperature: number;
  contrib_Flow_Rate: number;
  contrib_Suction_Pressure: number;
  contrib_Discharge_Pressure: number;
  contrib_Suction_Temperature: number;
  contrib_Discharge_Temperature: number;
  pct_Flow_Rate: number;
  pct_Suction_Pressure: number;
  pct_Discharge_Pressure: number;
  pct_Suction_Temperature: number;
  pct_Discharge_Temperature: number;
  dev_Flow_Rate: number;
  dev_Suction_Pressure: number;
  dev_Discharge_Pressure: number;
  dev_Suction_Temperature: number;
  dev_Discharge_Temperature: number;
  Production_Loss_MMSCFD: number;
  Gas_Loss_MMSCF: number;
}

export interface AnomalyAlert {
  timestamp: string;
  MAE: number;
  threshold_ratio: number;
  gas_loss: number;
  emailStatus?: 'Sent' | 'Failed' | 'Not Sent';
}

export interface SimulationState {
  running: boolean;
  currentIndex: number;
  dataBuffer: SensorData[];
  anomaliesDetected: AnomalyAlert[];
  emailsSent: Array<{
    timestamp: string;
    status: string;
    MAE: number;
  }>;
}

export interface DashboardStats {
  currentTime: string;
  pointsProcessed: number;
  anomaliesDetected: number;
  emailsSent: number;
}
