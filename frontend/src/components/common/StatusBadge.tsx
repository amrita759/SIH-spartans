import React from 'react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const norm = (status || 'NEW').toUpperCase();

  let styles = 'bg-slate-100 text-slate-700 border-slate-200';

  if (norm === 'NEW') {
    styles = 'bg-blue-50 text-blue-700 border-blue-200';
  } else if (norm === 'ANALYZING') {
    styles = 'bg-purple-50 text-purple-700 border-purple-200';
  } else if (norm === 'PREDICTION_READY') {
    styles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (norm === 'UNDER_REVIEW') {
    styles = 'bg-amber-50 text-amber-800 border-amber-200';
  } else if (norm === 'MONITORED') {
    styles = 'bg-slate-100 text-slate-700 border-slate-300';
  } else if (norm === 'RESOLVED') {
    styles = 'bg-slate-100 text-slate-500 border-slate-200 line-through';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${styles} ${className}`}>
      {norm}
    </span>
  );
};
