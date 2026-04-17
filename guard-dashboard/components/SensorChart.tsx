'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area } from 'recharts';
import { SensorData } from '@/types';
import { format } from 'date-fns';

interface SensorChartProps {
  data: SensorData[];
}

function MiniSensorChart({ data, dataKey, color, title, unit }: {
  data: any[],
  dataKey: string,
  color: string,
  title: string,
  unit: string
}) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[280px] flex items-center justify-center text-gray-400">
        <p className="text-sm">No data</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title} ({unit})</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.2}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey="time"
            stroke="#999"
            tick={{ fontSize: 10 }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#999"
            tick={{ fontSize: 10 }}
            tickLine={false}
            width={40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e0e0e0',
              borderRadius: '6px',
              padding: '6px 10px',
              fontSize: '11px',
            }}
            formatter={(value: any) => [Number(value).toFixed(2), title]}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            fill={`url(#gradient-${dataKey})`}
            stroke="none"
          />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function SensorChart({ data }: SensorChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-400 py-12">
        <p>No sensor data available. Start the simulation to begin monitoring.</p>
      </div>
    );
  }

  const chartData = data.map((item) => ({
    time: format(new Date(item.datetime), 'HH:mm:ss'),
    flowRate: item.Flow_Rate,
    suctionPressure: item.Suction_Pressure,
    dischargePressure: item.Discharge_Pressure,
    suctionTemp: item.Suction_Temperature,
    dischargeTemp: item.Discharge_Temperature,
  }));

  const sensors = [
    { dataKey: 'flowRate', color: '#ff9800', title: 'Flow Rate', unit: 'MMSCFD' },
    { dataKey: 'suctionPressure', color: '#2196f3', title: 'Suction Pressure', unit: 'barg' },
    { dataKey: 'dischargePressure', color: '#ff5722', title: 'Discharge Pressure', unit: 'barg' },
    { dataKey: 'suctionTemp', color: '#4caf50', title: 'Suction Temperature', unit: '°C' },
    { dataKey: 'dischargeTemp', color: '#9c27b0', title: 'Discharge Temperature', unit: '°C' },
  ];

  return (
    <div className="space-y-6">
      {/* Row 1: 3 sensors */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sensors.slice(0, 3).map((sensor) => (
          <MiniSensorChart
            key={sensor.dataKey}
            data={chartData}
            dataKey={sensor.dataKey}
            color={sensor.color}
            title={sensor.title}
            unit={sensor.unit}
          />
        ))}
      </div>

      {/* Row 2: 2 sensors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sensors.slice(3, 5).map((sensor) => (
          <MiniSensorChart
            key={sensor.dataKey}
            data={chartData}
            dataKey={sensor.dataKey}
            color={sensor.color}
            title={sensor.title}
            unit={sensor.unit}
          />
        ))}
      </div>
    </div>
  );
}
