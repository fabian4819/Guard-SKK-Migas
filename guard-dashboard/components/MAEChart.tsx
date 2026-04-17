'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area } from 'recharts';
import { SensorData } from '@/types';
import { format } from 'date-fns';

interface MAEChartProps {
  data: SensorData[];
  currentIndex?: number;
}

export default function MAEChart({ data, currentIndex }: MAEChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <p>No data available</p>
      </div>
    );
  }

  const chartData = data.map((item, index) => ({
    time: format(new Date(item.datetime), 'HH:mm:ss'),
    fullDate: item.datetime,
    threshold_ratio: item.threshold_ratio * (item.threshold_ratio < 2 ? 100 : 1),
    status: item.status,
    isAnomaly: item.status === 'ANOMALY',
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorThreshold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="rgba(66, 135, 245, 0.3)" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="rgba(66, 135, 245, 0.3)" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
        <XAxis
          dataKey="time"
          stroke="#999"
          tick={{ fontSize: 11 }}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          stroke="#999"
          tick={{ fontSize: 11 }}
          tickLine={false}
          domain={[0, 'auto']}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            padding: '8px 12px',
            fontSize: '12px',
          }}
          formatter={(value: any) => [`${Number(value).toFixed(1)}%`, 'Threshold Ratio']}
          labelStyle={{ color: '#666', fontWeight: 600 }}
        />

        {/* Threshold line at 100% */}
        <ReferenceLine y={100} stroke="#ff9800" strokeDasharray="3 3" strokeWidth={2} />

        {/* Area fill */}
        <Area
          type="monotone"
          dataKey="threshold_ratio"
          fill="url(#colorThreshold)"
          stroke="none"
        />

        {/* Main line */}
        <Line
          type="monotone"
          dataKey="threshold_ratio"
          stroke="rgba(66, 135, 245, 0.8)"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6, fill: '#4287f5' }}
        />

        {/* Anomaly markers */}
        <Line
          type="monotone"
          dataKey={(entry) => entry.isAnomaly ? entry.threshold_ratio : null}
          stroke="none"
          dot={{ r: 6, fill: '#ff5722', strokeWidth: 0 }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
