import React, { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  variant?: 'cyan' | 'red' | 'amber' | 'emerald' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'cyan'
}) => {
  const iconVariants = {
    cyan: 'text-slate-700 bg-slate-100 border-slate-200',
    red: 'text-red-700 bg-red-50 border-red-200',
    amber: 'text-amber-700 bg-amber-50 border-amber-200',
    emerald: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    purple: 'text-slate-800 bg-slate-100 border-slate-200',
  };

  return (
    <div className="bg-white rounded-md p-4 border border-slate-200 shadow-xs flex items-center justify-between transition hover:border-slate-300">
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{title}</p>
        <p className="text-2xl font-bold font-mono text-slate-900 mt-0.5">{value}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">{subtitle}</p>}
      </div>
      <div className={`p-2.5 rounded border shrink-0 ${iconVariants[variant]}`}>
        {icon}
      </div>
    </div>
  );
};
