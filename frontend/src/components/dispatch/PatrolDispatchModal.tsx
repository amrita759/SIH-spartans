import React, { useState } from 'react';
import { api } from '../../services/api';
import {
  ShieldAlert,
  Radio,
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Send,
  X,
  Building2,
  Car
} from 'lucide-react';

interface CandidateLocation {
  location_id: string;
  bank_name: string;
  location_type: string;
  district: string;
  state: string;
  risk_score: number;
  risk_level: string;
  rank: number;
}

interface PatrolDispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  fraudAmount: number;
  fraudType: string;
  topCandidates: CandidateLocation[];
  onDispatched: (unit: string, locationId: string) => void;
}

export const PatrolDispatchModal: React.FC<PatrolDispatchModalProps> = ({
  isOpen,
  onClose,
  caseId,
  fraudAmount,
  fraudType,
  topCandidates,
  onDispatched
}) => {
  const [selectedLocationId, setSelectedLocationId] = useState<string>(
    topCandidates[0]?.location_id || ''
  );
  const [patrolUnit, setPatrolUnit] = useState('PCR-DELTA-04 (Town PS Quick Response - 1.8 km)');
  const [channel, setChannel] = useState('ERSS_112_CAD');
  const [directives, setDirectives] = useState(
    'Establish discreet observation at target ATM/CRM booth. Monitor multiple rapid card attempts matching stolen outflow. Request bank CCTV coordination. Intercept suspect prior to cash disbursement.'
  );
  const [isSending, setIsSending] = useState(false);
  const [successInfo, setSuccessInfo] = useState<{
    unit: string;
    message: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const targetLocation =
    topCandidates.find((c) => c.location_id === selectedLocationId) || topCandidates[0];

  const handleDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetLocation) {
      setError('Please select a candidate disbursement terminal.');
      return;
    }

    setIsSending(true);
    setError(null);

    try {
      const res = await api.dispatchPatrol(caseId, {
        patrol_unit: patrolUnit.split(' ')[0],
        target_location_id: targetLocation.location_id,
        directives: directives
      });

      setSuccessInfo({
        unit: patrolUnit.split(' ')[0],
        message: res.message
      });

      onDispatched(patrolUnit.split(' ')[0], targetLocation.location_id);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to transmit patrol dispatch order.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
      <div className="relative w-full max-w-xl bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded bg-slate-900 text-white">
              <Radio className="w-4 h-4 text-blue-400 animate-pulse" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Tactical Patrol Dispatch Order
              </h2>
              <p className="text-[11px] text-slate-500 font-mono">
                Case: {caseId} • Law Enforcement Field Interception Directives
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 max-h-[78vh] overflow-y-auto">
          {error && (
            <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successInfo ? (
            <div className="p-5 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 space-y-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <h3 className="text-xs font-bold uppercase tracking-wider">
                  Patrol Unit Dispatched Successfully
                </h3>
              </div>
              <p className="text-xs leading-relaxed text-emerald-800">
                Tactical alert order transmitted to <strong className="font-mono">{successInfo.unit}</strong> via ERSS-112 Police CAD Gateway.
                The field patrol is en route to establish visual surveillance at <strong className="font-semibold">{targetLocation?.bank_name} ({targetLocation?.location_type})</strong>.
              </p>
              <div className="p-3 bg-white/80 rounded border border-emerald-300 text-[11px] font-mono space-y-1">
                <div>• Target Terminal: {targetLocation?.location_id}</div>
                <div>• Risk Probability: {targetLocation?.risk_score.toFixed(1)} ({targetLocation?.risk_level})</div>
                <div>• Case Status: ESCALATED TO MONITORED</div>
              </div>
              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded bg-slate-900 text-white text-xs font-semibold shadow-xs hover:bg-slate-800 transition cursor-pointer"
                >
                  Return to Case Dossier
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleDispatch} className="space-y-4">
              {/* Case Context Pill */}
              <div className="p-3 rounded bg-slate-50 border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="text-slate-500">Complaint Loss: </span>
                  <strong className="font-mono text-slate-900">₹{fraudAmount.toLocaleString('en-IN')}</strong>
                </div>
                <div>
                  <span className="text-slate-500">Fraud Scenario: </span>
                  <strong className="capitalize text-slate-800">{fraudType.replace(/_/g, ' ')}</strong>
                </div>
                <div className="font-mono text-[11px] text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  Lead Time Window: ~2.6h
                </div>
              </div>

              {/* Target Location Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-red-600" />
                  <span>Target Candidate ATM/CRM for Interception</span>
                </label>
                <select
                  value={selectedLocationId}
                  onChange={(e) => setSelectedLocationId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs text-slate-900 font-medium focus:outline-none focus:ring-1 focus:ring-slate-900"
                >
                  {topCandidates.map((loc) => (
                    <option key={loc.location_id} value={loc.location_id}>
                      Rank #{loc.rank} — {loc.bank_name} ({loc.location_type}) • Score {loc.risk_score.toFixed(1)} [{loc.risk_level}] • {loc.district}
                    </option>
                  ))}
                </select>
                {targetLocation && (
                  <p className="text-[11px] text-slate-500 flex items-center gap-2">
                    <span>ID: <code className="font-mono font-semibold">{targetLocation.location_id}</code></span>
                    <span>•</span>
                    <span>Jurisdiction: {targetLocation.district}, {targetLocation.state}</span>
                  </p>
                )}
              </div>

              {/* Assign Nearby Patrol Unit */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                  <Car className="w-3.5 h-3.5 text-blue-700" />
                  <span>Nearest Patrol Unit (Auto-Identified via Geo-Fence)</span>
                </label>
                <select
                  value={patrolUnit}
                  onChange={(e) => setPatrolUnit(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs text-slate-900 font-medium focus:outline-none focus:ring-1 focus:ring-slate-900"
                >
                  <option value="PCR-DELTA-04 (Town PS Quick Response - 1.8 km)">
                    PCR-DELTA-04 (Town Police Station Quick Response — 1.8 km / ETA 6 mins)
                  </option>
                  <option value="BEAT-PATROL-02 (Sector 4 Surveillance Motorcycle Unit - 2.4 km)">
                    BEAT-PATROL-02 (Sector 4 Surveillance Motorcycle Unit — 2.4 km / ETA 8 mins)
                  </option>
                  <option value="CYBER-FLYING-SQUAD (District Cyber Crime Cell - 4.1 km)">
                    CYBER-FLYING-SQUAD (District Cyber Crime Cell — 4.1 km / ETA 12 mins)
                  </option>
                  <option value="STATION-SUB-INSPECTOR (Local Thana On-Duty - 1.2 km)">
                    STATION-SUB-INSPECTOR (Local Police Station On-Duty Officer — 1.2 km / ETA 5 mins)
                  </option>
                </select>
              </div>

              {/* Directives */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Standard Operating Procedures & Tactical Directives
                </label>
                <textarea
                  value={directives}
                  onChange={(e) => setDirectives(e.target.value)}
                  rows={3}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 leading-relaxed"
                />
              </div>

              {/* Transmission Gateway */}
              <div className="p-3 rounded bg-blue-50/70 border border-blue-200 text-xs space-y-1.5">
                <div className="flex items-center gap-1.5 text-blue-900 font-semibold text-[11px] uppercase tracking-wider">
                  <ShieldAlert className="w-3.5 h-3.5 text-blue-700" />
                  <span>Dispatch Transmission Protocol</span>
                </div>
                <div className="flex flex-wrap gap-2 text-[11px]">
                  <label className="flex items-center gap-1.5 cursor-pointer bg-white px-2.5 py-1 rounded border border-blue-200 text-blue-900">
                    <input
                      type="radio"
                      name="channel"
                      checked={channel === 'ERSS_112_CAD'}
                      onChange={() => setChannel('ERSS_112_CAD')}
                    />
                    <span>ERSS-112 CAD Gateway (High Priority)</span>
                  </label>
                  <label className="flex items-center gap-1.5 cursor-pointer bg-white px-2.5 py-1 rounded border border-blue-200 text-blue-900">
                    <input
                      type="radio"
                      name="channel"
                      checked={channel === 'POLICE_WIRELESS'}
                      onChange={() => setChannel('POLICE_WIRELESS')}
                    />
                    <span>Police Wireless Net (Channel 4)</span>
                  </label>
                </div>
              </div>

              {/* Form Buttons */}
              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3.5 py-2 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold shadow-xs transition cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSending}
                  className="flex items-center gap-1.5 px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
                >
                  <Send className={`w-3.5 h-3.5 ${isSending ? 'animate-spin' : ''}`} />
                  <span>{isSending ? 'Transmitting Dispatch...' : 'Transmit Tactical Dispatch to Patrol'}</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
