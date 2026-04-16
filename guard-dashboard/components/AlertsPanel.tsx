'use client';

import { AnomalyAlert } from '@/types';
import { format } from 'date-fns';
import { AlertTriangle, Mail, MailX } from 'lucide-react';

interface AlertsPanelProps {
  alerts: AnomalyAlert[];
  maxDisplay?: number;
}

export default function AlertsPanel({ alerts, maxDisplay = 10 }: AlertsPanelProps) {
  const displayAlerts = alerts.slice(-maxDisplay).reverse();

  if (alerts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">🚨 Recent Anomaly Alerts</h2>
        <div className="text-center py-12 text-gray-500">
          <AlertTriangle className="mx-auto mb-3 opacity-30" size={48} />
          <p>No anomalies detected yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">🚨 Recent Anomaly Alerts</h2>
        <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
          {alerts.length} Total
        </span>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {displayAlerts.map((alert, index) => (
          <div
            key={index}
            className="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg hover:bg-red-100 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="text-red-600" size={18} />
                  <span className="font-bold text-gray-800">
                    {format(new Date(alert.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="text-gray-600">MAE:</span>{' '}
                    <span className="font-semibold text-gray-800">{alert.MAE.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Threshold:</span>{' '}
                    <span className="font-semibold text-gray-800">
                      {(alert.threshold_ratio * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Gas Loss:</span>{' '}
                    <span className="font-semibold text-gray-800">
                      {alert.gas_loss.toFixed(4)} MMSCF
                    </span>
                  </div>
                </div>
              </div>
              <div className="ml-4">
                {alert.emailStatus === 'Sent' ? (
                  <div className="flex items-center gap-1 text-green-600 text-sm">
                    <Mail size={16} />
                    <span className="font-medium">Sent</span>
                  </div>
                ) : alert.emailStatus === 'Failed' ? (
                  <div className="flex items-center gap-1 text-red-600 text-sm">
                    <MailX size={16} />
                    <span className="font-medium">Failed</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-gray-500 text-sm">
                    <Mail size={16} />
                    <span className="font-medium">Not Sent</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {alerts.length > maxDisplay && (
        <div className="mt-4 text-center text-sm text-gray-600">
          Showing last {maxDisplay} of {alerts.length} alerts
        </div>
      )}
    </div>
  );
}
