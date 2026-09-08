import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';
import { Alert } from '../types/alert';
import { AlertItem } from '../components/alerts/AlertItem';
import {
  Bell,
  CheckCircle2,
  AlertTriangle,
  Filter,
  RefreshCw,
  ShieldAlert
} from 'lucide-react';

interface AlertsPageProps {
  onOpenCase: (caseId: string) => void;
  onRefreshAlerts?: () => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ onOpenCase, onRefreshAlerts }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId, 'LEA_PATROL_LEAD');
      await fetchAlerts();
      if (onRefreshAlerts) onRefreshAlerts();
    } catch (err: any) {
      alert('Failed to acknowledge alert: ' + (err?.message || 'Unknown error'));
    }
  };

  const filteredAlerts = useMemo(() => {
    if (statusFilter === 'ALL') return alerts;
    return alerts.filter((a) => a.status === statusFilter);
  }, [alerts, statusFilter]);

  const newCount = alerts.filter((a) => a.status === 'NEW').length;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-base font-bold text-slate-900 tracking-tight">
              Law Enforcement Dispatch &amp; Priority Alerts
            </h1>
            {newCount > 0 && (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase bg-red-100 text-red-800 border border-red-300">
                {newCount} Pending
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated alerts dispatched when candidate ATM/CRM probability exceeds threshold (&ge; 80.0 score).
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-slate-600' : 'text-slate-500'}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Operational Disclaimer */}
      <div className="p-3 rounded border border-amber-200 bg-amber-50/80 text-xs text-amber-900 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>LEA Dispatch Protocol:</strong> Alerts represent high-probability disbursement candidates scored at pre-withdrawal boundary time <span className="font-mono">T</span>. Acknowledging an alert escalates the complaint dossier to <span className="font-semibold text-slate-900">UNDER_REVIEW</span> and transmits tactical terminal coordinates to field patrol units.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="p-2.5 rounded border border-slate-200 bg-white shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-600">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-medium">Filter Status:</span>
          <div className="flex items-center gap-1">
            {['ALL', 'NEW', 'ACKNOWLEDGED', 'UNDER_REVIEW', 'RESOLVED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1 rounded text-[11px] font-semibold transition cursor-pointer ${
                  statusFilter === st
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <span className="font-mono text-slate-500 text-[11px]">
          Showing {filteredAlerts.length} of {alerts.length} notifications
        </span>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-2.5">
        {filteredAlerts.length === 0 ? (
          <div className="p-12 text-center bg-white rounded border border-slate-200 text-slate-500 text-xs space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-600/60 mx-auto" />
            <p className="font-medium text-slate-700">No active alerts matching filter "{statusFilter}".</p>
            <p className="text-[11px] text-slate-400">All high-risk candidate ATM events in this state have been handled or cleared.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertItem
              key={alert.alert_id}
              alert={alert}
              onAcknowledge={handleAcknowledgeAlert}
              onViewCase={onOpenCase}
            />
          ))
        )}
      </div>
    </div>
  );
};
