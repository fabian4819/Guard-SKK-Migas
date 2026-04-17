'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Scatter, ScatterChart } from 'recharts';
import { SensorData } from '@/types';
import { format } from 'date-fns';

interface MAEChartProps {
  data: SensorData[];
  currentIndex?: number;
}

export default function MAEChart({ data, currentIndex }: MAEChartProps) {
  const chartData = data.map((item, index) => ({
    time: format(new Date(item.datetime), 'HH:mm'),
    fullDate: item.datetime,
    MAE: item.MAE,
    status: item.status,
    isAnomaly: item.status === 'ANOMALY',
    isCurrent: index === currentIndex,
  }));

  const anomalies = chartData.filter(d => d.isAnomaly);
  const currentPoint = currentIndex !== undefined ? chartData[currentIndex] : null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">📈 Live Anomaly Detection - MAE Timeline</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="time"
            stroke="#666"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#666"
            tick={{ fontSize: 12 }}
            label={{ value: 'MAE', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '8px',
              padding: '10px',
            }}
            formatter={(value: any, name?: any) => {
              if (name === 'MAE') return [value.toFixed(4), 'MAE'];
              return [value, name];
            }}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Legend />

          {/* MAE Line */}
          <Line
            type="monotone"
            dataKey="MAE"
            stroke="#1976d2"
            strokeWidth={2}
            dot={false}
            name="MAE"
          />

          {/* Anomaly Points */}
          {anomalies.map((anomaly, index) => (
            <Scatter
              key={`anomaly-${index}`}
              data={[anomaly]}
              fill="#f44336"
              shape="cross"
              name={index === 0 ? 'Anomaly' : ''}
            />
          ))}

          {/* Current Position */}
          {currentPoint && (
            <Scatter
              data={[currentPoint]}
              fill="#4caf50"
              shape="triangle"
              name="Current"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-4 flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-blue-600"></div>
          <span>MAE Value</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-red-600">✕</span>
          <span>Anomaly Detected</span>
        </div>
        {currentIndex !== undefined && (
          <div className="flex items-center gap-2">
            <span className="text-green-600">▲</span>
            <span>Current Position</span>
          </div>
        )}
      </div>
    </div>
  );
}
