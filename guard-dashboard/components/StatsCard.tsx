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
    primary: 'text-[#1e3c72]',
    success: 'text-[#4caf50]',
    danger: 'text-[#ff5722]',
    warning: 'text-orange-700',
  };

  return (
    <div className="bg-white rounded-lg p-5 shadow-sm border border-gray-100 transition-all hover:shadow-md hover:-translate-y-0.5 h-full">
      <div className="flex flex-col h-full">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 mb-3">{title}</p>
        <div className="mt-auto">
          <div className={`whitespace-pre-line leading-tight font-bold ${colorClasses[color]}`}>
            {typeof value === 'string' && value.includes('\n') ? (
              <>
                <div className="text-lg font-semibold mb-0.5">{value.split('\n')[0]}</div>
                <div className="text-3xl font-bold">{value.split('\n')[1]}</div>
              </>
            ) : (
              <span className="text-4xl">{value.toLocaleString()}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
