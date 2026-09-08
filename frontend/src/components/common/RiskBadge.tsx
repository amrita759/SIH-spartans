import React from 'react';

interface RiskBadgeProps {
  level: string;
  score?: number;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, className = '' }) => {
  const normLevel = (level || 'LOW').toUpperCase();

  let bgClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
  let dotClass = 'bg-emerald-600';

  if (normLevel === 'CRITICAL') {
    bgClass = 'bg-red-50 text-red-800 border-red-200';
    dotClass = 'bg-red-600';
  } else if (normLevel === 'HIGH') {
    bgClass = 'bg-orange-50 text-orange-800 border-orange-200';
    dotClass = 'bg-orange-600';
  } else if (normLevel === 'MEDIUM') {
    bgClass = 'bg-amber-50 text-amber-800 border-amber-200';
    dotClass = 'bg-amber-600';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-semibold tracking-normal border ${bgClass} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotClass}`} />
      <span>{normLevel}</span>
      {score !== undefined && (
        <span className="font-mono text-[11px] font-bold opacity-90">({score.toFixed(1)})</span>
      )}
    </span>
  );
};
