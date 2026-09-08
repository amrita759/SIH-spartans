import React from 'react';
import { Alert } from '../../types/alert';
import { RiskBadge } from '../common/RiskBadge';
import { AlertTriangle, CheckCircle2, Eye, MapPin, Building2, Clock } from 'lucide-react';

interface AlertItemProps {
  alert: Alert;
  onAcknowledge: (alertId: string) => void;
  onViewCase?: (caseId: string) => void;
  onViewLocation?: (locationId: string) => void;
}

export const AlertItem: React.FC<AlertItemProps> = ({
  alert,
  onAcknowledge,
  onViewCase,
  onViewLocation
}) => {
  const isAcknowledged = alert.status !== 'NEW';

  return (
    <div
      className={`p-4 rounded-md border transition-all ${
        isAcknowledged
          ? 'bg-white border-slate-200 text-slate-600'
          : 'bg-red-50/25 border-red-200 shadow-xs'
      }`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Left: Alert Header & IDs */}
        <div className="flex items-start gap-3">
          <div
            className={`p-2 rounded border shrink-0 ${
              isAcknowledged
                ? 'bg-slate-100 border-slate-200 text-slate-500'
                : 'bg-red-50 border-red-200 text-red-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-xs font-bold text-slate-900">{alert.alert_id}</span>
              <span className="text-slate-400">•</span>
              <button
                onClick={() => onViewCase && onViewCase(alert.case_id)}
                className="font-mono text-xs font-bold text-slate-900 hover:text-blue-700 hover:underline cursor-pointer"
              >
                {alert.case_id}
              </button>
              <RiskBadge level={alert.risk_level} score={alert.risk_score} />
              <span
                className={`px-1.5 py-0.2 rounded text-[10px] font-bold uppercase tracking-wider border ${
                  isAcknowledged
                    ? 'bg-slate-100 text-slate-600 border-slate-200'
                    : 'bg-red-100 text-red-800 border-red-200'
                }`}
              >
                {alert.status}
              </span>
            </div>

            <div className="mt-1.5 flex items-center gap-4 text-xs text-slate-600 flex-wrap">
              <span className="flex items-center gap-1 font-mono font-semibold text-slate-800">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                Terminal: {alert.location_id}
              </span>
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-slate-500" />
                {alert.bank_name || 'Bank'}
              </span>
              <span className="flex items-center gap-1 text-slate-500 font-mono text-[11px]">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Recent'}
              </span>
            </div>

            {alert.message && (
              <p className="mt-2 text-xs text-slate-700 font-sans leading-relaxed whitespace-pre-line bg-slate-50 p-2 rounded border border-slate-200">
                {alert.message}
              </p>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 self-end md:self-center shrink-0">
          {onViewCase && (
            <button
              onClick={() => onViewCase(alert.case_id)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-300 text-xs font-medium text-slate-700 transition cursor-pointer"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Dossier</span>
            </button>
          )}

          {!isAcknowledged ? (
            <button
              onClick={() => onAcknowledge(alert.alert_id)}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-red-600 hover:bg-red-700 text-white font-semibold text-xs transition shadow-xs cursor-pointer"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Acknowledge</span>
            </button>
          ) : (
            <div className="text-right text-[11px] text-slate-500 font-mono">
              <span>Ack by: {alert.acknowledged_by || 'OFFICER'}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
