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
    primary: 'text-blue-900',
    success: 'text-green-700',
    danger: 'text-red-600',
    warning: 'text-orange-700',
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm transition-all hover:shadow-md h-full">
      <div className="flex flex-col h-full">
        <p className="text-[12px] font-black uppercase tracking-widest text-[#94a3b8] mb-6">{title}</p>
        <div className="mt-auto">
          <div className="whitespace-pre-line text-[#1e3c72] leading-tight font-black tracking-tight">
            {typeof value === 'string' && value.includes('\n') ? (
              <>
                <div className="text-2xl opacity-80 mb-1">{value.split('\n')[0]}</div>
                <div className="text-4xl">{value.split('\n')[1]}</div>
              </>
            ) : (
              <span className="text-3xl">{value}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
