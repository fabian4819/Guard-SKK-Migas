'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, Legend, Scatter, ScatterChart, ZAxis } from 'recharts';
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
    date: format(new Date(item.datetime), 'MMM dd, yyyy'),
    fullDate: item.datetime,
    threshold_ratio: item.threshold_ratio,
    status: item.status,
    isAnomaly: item.status === 'ANOMALY',
    isCurrent: index === currentIndex,
  }));

  // Extract anomaly points for red dots
  const anomalyPoints = chartData
    .map((item, idx) => ({ ...item, originalIndex: idx }))
    .filter(item => item.isAnomaly);

  // Current position point (green triangle)
  const currentPoint = currentIndex !== undefined && currentIndex >= 0 ? chartData[currentIndex] : null;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
        <defs>
          <linearGradient id="colorThreshold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4287f5" stopOpacity={0.4}/>
            <stop offset="95%" stopColor="#4287f5" stopOpacity={0.1}/>
          </linearGradient>
        </defs>

        {/* Grid */}
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />

        {/* X Axis - Time */}
        <XAxis
          dataKey="time"
          stroke="#9ca3af"
          tick={{ fontSize: 11, fill: '#6b7280' }}
          tickLine={false}
          interval="preserveStartEnd"
          label={{ value: chartData[0]?.date || '', position: 'insideBottomLeft', offset: -5, fontSize: 11, fill: '#9ca3af' }}
        />

        {/* Y Axis */}
        <YAxis
          stroke="#9ca3af"
          tick={{ fontSize: 11, fill: '#6b7280' }}
          tickLine={false}
          domain={[0, 'auto']}
        />

        {/* Tooltip */}
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '8px 12px',
            fontSize: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
          formatter={(value: any) => [`${Number(value).toFixed(1)}%`, 'Threshold Ratio']}
          labelStyle={{ color: '#374151', fontWeight: 600, marginBottom: '4px' }}
        />

        {/* Legend */}
        <Legend
          wrapperStyle={{ paddingTop: '10px' }}
          iconType="line"
          formatter={(value) => <span style={{ color: '#6b7280', fontSize: '13px' }}>{value}</span>}
        />

        {/* Threshold line at 100% */}
        <ReferenceLine
          y={100}
          stroke="#ff9800"
          strokeDasharray="5 5"
          strokeWidth={2}
          label={{ value: 'Threshold', position: 'right', fill: '#ff9800', fontSize: 11 }}
        />

        {/* Area fill */}
        <Area
          type="monotone"
          dataKey="threshold_ratio"
          fill="url(#colorThreshold)"
          stroke="none"
        />

        {/* Main threshold ratio line */}
        <Line
          type="monotone"
          dataKey="threshold_ratio"
          stroke="#4287f5"
          strokeWidth={2.5}
          dot={false}
          activeDot={{ r: 5, fill: '#4287f5', strokeWidth: 2, stroke: '#fff' }}
          name="Threshold Ratio"
        />

        {/* Anomaly dots (red circles) - Single scatter for all anomalies */}
        {anomalyPoints.length > 0 && (
          <Scatter
            data={anomalyPoints.map(point => ({ time: point.time, threshold_ratio: point.threshold_ratio }))}
            fill="#ef4444"
            shape="circle"
            name="Anomaly"
          >
            <ZAxis range={[100, 100]} />
          </Scatter>
        )}

        {/* Current position marker (green triangle) */}
        {currentPoint && (
          <Scatter
            data={[{ time: currentPoint.time, threshold_ratio: currentPoint.threshold_ratio }]}
            fill="#22c55e"
            shape="triangle"
            name="Current"
          >
            <ZAxis range={[120, 120]} />
          </Scatter>
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
