import React from 'react';
import { X, Building2, MapPin, Target, ShieldAlert, Cpu } from 'lucide-react';
import { RiskBadge } from '../common/RiskBadge';
import { ShapFactorList } from '../explainability/ShapFactorList';
import { ExplanationFactor } from '../../types/prediction';

export interface DrawerLocationData {
  rank?: number;
  location_id: string;
  location_name?: string;
  location_type?: string;
  bank_name?: string;
  latitude: number;
  longitude: number;
  district?: string;
  state?: string;
  risk_score: number;
  risk_level: string;
  top_factors?: ExplanationFactor[];
}

interface LocationDrawerProps {
  location: DrawerLocationData | null;
  onClose: () => void;
  predictionWindowHours?: number;
}

export const LocationDrawer: React.FC<LocationDrawerProps> = ({
  location,
  onClose,
  predictionWindowHours = 6
}) => {
  if (!location) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-[1500] w-full sm:w-[420px] bg-white border-l border-slate-200 shadow-2xl p-6 overflow-y-auto animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-slate-800" />
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            Candidate Location Dossier
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="mt-5 space-y-5">
        {/* Top Summary Card */}
        <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-mono text-slate-500 font-bold uppercase">
                RANK #{location.rank || 1} • {location.location_type || 'ATM'}
              </p>
              <h3 className="text-base font-bold font-mono text-slate-900 mt-0.5">
                {location.location_id}
              </h3>
            </div>
            <RiskBadge level={location.risk_level} score={location.risk_score} />
          </div>

          <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs">
            <div className="flex items-center gap-2 text-slate-700">
              <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span className="font-medium">{location.bank_name || 'Commercial Bank'}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span>{location.district}, {location.state}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-500 font-mono text-[11px]">
              <span>GPS: ({location.latitude.toFixed(4)}, {location.longitude.toFixed(4)})</span>
            </div>
          </div>
        </div>

        {/* Operational Horizon */}
        <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-slate-600" />
            <span>Surveillance Window:</span>
          </div>
          <span className="font-mono font-bold text-slate-900">Next {predictionWindowHours} Hours</span>
        </div>

        {/* SHAP Factors */}
        <div>
          <ShapFactorList
            factors={location.top_factors || []}
            locationId={location.location_id}
            riskScore={location.risk_score}
          />
        </div>

        {/* LEA Action Guidelines */}
        <div className="p-3.5 rounded-md bg-amber-50/70 border border-amber-200 space-y-1.5 text-xs text-amber-900">
          <div className="flex items-center gap-1.5 font-bold text-amber-900 uppercase tracking-wider text-[11px]">
            <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
            <span>Recommended LEA Protocol</span>
          </div>
          <p className="text-[11px] leading-relaxed text-amber-800">
            1. Flag location with jurisdictional patrol and nodal crime teams.<br />
            2. Alert acquiring bank fraud desk to monitor journal log telemetry.<br />
            3. Synchronize physical CCTV surveillance if suspicious cash-out attempted.
          </p>
        </div>
      </div>
    </div>
  );
};
