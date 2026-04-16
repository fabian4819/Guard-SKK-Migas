'use client';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'primary' | 'success' | 'danger' | 'warning';
}

export default function StatsCard({ title, value, icon, trend, color = 'primary' }: StatsCardProps) {
  const colorClasses = {
    primary: 'bg-blue-50 border-blue-200 text-blue-700',
    success: 'bg-green-50 border-green-200 text-green-700',
    danger: 'bg-red-50 border-red-200 text-red-700',
    warning: 'bg-orange-50 border-orange-200 text-orange-700',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]} transition-all hover:shadow-lg`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-70">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        {icon && <div className="text-4xl opacity-50">{icon}</div>}
      </div>
      {trend && (
        <div className="mt-3 text-xs">
          <span className={`inline-flex items-center ${
            trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
          }`}>
            {trend === 'up' && '↑'}
            {trend === 'down' && '↓'}
            {trend === 'neutral' && '→'}
          </span>
        </div>
      )}
    </div>
  );
}
