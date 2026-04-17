'use client';

import { useState } from 'react';
import { SensorData } from '@/types';
import { format } from 'date-fns';
import AnomalyDetailModal from './AnomalyDetailModal';

interface AlertsPanelProps {
  alerts: SensorData[];
  maxDisplay?: number;
}

export default function AlertsPanel({ alerts, maxDisplay = 5 }: AlertsPanelProps) {
  const [selectedAnomaly, setSelectedAnomaly] = useState<SensorData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const displayAlerts = alerts.slice(-maxDisplay).reverse();

  const handleViewClick = (anomaly: SensorData) => {
    setSelectedAnomaly(anomaly);
    setIsModalOpen(true);
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden flex flex-col" style={{ maxHeight: 'calc(400px + 200px)' }}>
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 px-5 py-3 flex-shrink-0">
          <h2 className="text-white font-semibold text-base">Anomaly History</h2>
        </div>

        {/* Table Header */}
        <div className="bg-gray-50 px-4 py-3 grid grid-cols-12 gap-2 border-b border-gray-200 flex-shrink-0">
          <div className="col-span-6 text-xs font-semibold text-gray-600 uppercase tracking-wide">Time</div>
          <div className="col-span-3 text-xs font-semibold text-gray-600 uppercase tracking-wide text-center">Ratio</div>
          <div className="col-span-3 text-xs font-semibold text-gray-600 uppercase tracking-wide text-center">Action</div>
        </div>

        {/* Table Body - Scrollable */}
        <div className="divide-y divide-gray-100 overflow-y-auto flex-1">
          {alerts.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-400 text-sm">
              No anomalies yet
            </div>
          ) : (
            displayAlerts.map((alert, index) => {
              const ratio = alert.threshold_ratio;
              let ratioColor = '#ff9800'; // orange
              if (ratio > 130) ratioColor = '#d32f2f'; // dark red
              else if (ratio > 120) ratioColor = '#f44336'; // red

              return (
                <div key={index} className="px-4 py-3 grid grid-cols-12 gap-2 hover:bg-gray-50 transition-colors">
                  <div className="col-span-6 text-xs text-gray-700 flex items-center">
                    {format(new Date(alert.datetime), 'yyyy-MM-dd HH:mm:ss')}
                  </div>
                  <div className="col-span-3 flex items-center justify-center">
                    <span className="text-sm font-bold" style={{ color: ratioColor }}>
                      {ratio.toFixed(1)}%
                    </span>
                  </div>
                  <div className="col-span-3 flex items-center justify-center">
                    <button
                      onClick={() => handleViewClick(alert)}
                      className="px-3 py-1 text-xs font-medium text-gray-600 border border-gray-300 rounded hover:bg-gray-50 hover:shadow-sm transition-all"
                    >
                      View
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Anomaly Detail Modal */}
      <AnomalyDetailModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        anomalyData={selectedAnomaly}
      />
    </>
  );
}
