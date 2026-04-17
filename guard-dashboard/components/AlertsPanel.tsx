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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-[#43a047] px-4 py-3 border-b border-gray-200">
        <h2 className="text-white text-md font-bold uppercase tracking-wide">Anomaly History</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#f8f9fa] text-gray-600 uppercase font-black tracking-tighter">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3 text-right">Ratio</th>
              <th className="px-4 py-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 italic">
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-gray-400 font-medium">
                  No anomalies recorded
                </td>
              </tr>
            ) : (
              displayAlerts.map((alert, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-600 font-medium whitespace-nowrap">
                    {format(new Date(alert.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                  </td>
                  <td className="px-4 py-3 text-right font-black text-red-600">
                    {(alert.threshold_ratio * (alert.threshold_ratio < 2 ? 100 : 1)).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button className="px-3 py-1 border border-gray-200 rounded-lg text-[10px] font-bold text-gray-500 hover:bg-white hover:shadow-sm transition-all uppercase tracking-tighter shadow-xs">
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
