'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { SensorData } from '@/types';
import { format } from 'date-fns';

interface SensorChartProps {
  data: SensorData[];
}

export default function SensorChart({ data }: SensorChartProps) {
  const chartData = data.map((item) => ({
    time: format(new Date(item.datetime), 'HH:mm'),
    'Flow Rate': item.Flow_Rate,
    'Suction Pressure': item.Suction_Pressure,
    'Discharge Pressure': item.Discharge_Pressure,
    'Suction Temp': item.Suction_Temperature,
    'Discharge Temp': item.Discharge_Temperature,
  }));

  const sensors = [
    { key: 'Flow Rate', color: '#1976d2' },
    { key: 'Suction Pressure', color: '#ff9800' },
    { key: 'Discharge Pressure', color: '#4caf50' },
    { key: 'Suction Temp', color: '#9c27b0' },
    { key: 'Discharge Temp', color: '#f44336' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">📊 Live Sensor Readings</h2>
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
            label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '8px',
              padding: '10px',
            }}
            formatter={(value: any) => value.toFixed(2)}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />

          {sensors.map((sensor) => (
            <Line
              key={sensor.key}
              type="monotone"
              dataKey={sensor.key}
              stroke={sensor.color}
              strokeWidth={2}
              dot={false}
              name={sensor.key}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
        {sensors.map((sensor) => (
          <div key={sensor.key} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: sensor.color }}></div>
            <span className="text-gray-700">{sensor.key}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
