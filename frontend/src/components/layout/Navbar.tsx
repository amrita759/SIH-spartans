import React from 'react';
import { Shield, AlertTriangle, Cpu, UserCheck } from 'lucide-react';

interface NavbarProps {
  activeAlertsCount?: number;
  onAlertsClick?: () => void;
  modelVersion?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeAlertsCount = 0,
  onAlertsClick,
  modelVersion = 'v1.0.0'
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-200 px-4 lg:px-8 py-2.5">
      <div className="flex items-center justify-between">
        {/* Left: Branding & Institutional Identity */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded bg-slate-900 text-white border border-slate-800 shrink-0">
            <Shield className="w-5 h-5 text-slate-100" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-sm tracking-wide text-slate-900 uppercase">
                NATIONAL CYBERCRIME PREDICTIVE INTELLIGENCE PLATFORM
              </span>
              <span className="bg-slate-100 text-slate-700 text-[10px] font-semibold px-2 py-0.5 rounded border border-slate-200">
                OPERATIONAL DEMONSTRATION
              </span>
            </div>
            <p className="text-[11px] text-slate-500 tracking-tight hidden sm:block">
              Ministry of Home Affairs / I4C Framework • Problem Statement SIH26184
            </p>
          </div>
        </div>

        {/* Right: Operational Status & Alert Controls */}
        <div className="flex items-center gap-3">
          {/* Real-Time Telemetry Status */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded bg-slate-50 border border-slate-200 text-xs text-slate-700">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-600" />
            <span className="font-semibold text-[11px] tracking-wide text-slate-700">SURVEILLANCE ACTIVE</span>
            <span className="text-slate-300">|</span>
            <span className="flex items-center gap-1 text-slate-600 text-[11px]">
              <Cpu className="w-3.5 h-3.5 text-slate-500" />
              LightGBM ({modelVersion})
            </span>
          </div>

          {/* Active Alerts Button */}
          <button
            onClick={onAlertsClick}
            className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold border transition cursor-pointer ${
              activeAlertsCount > 0
                ? 'bg-red-50 border-red-300 text-red-700 hover:bg-red-100'
                : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <AlertTriangle className={`w-3.5 h-3.5 ${activeAlertsCount > 0 ? 'text-red-600' : 'text-slate-500'}`} />
            <span>ALERTS</span>
            {activeAlertsCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 bg-red-600 text-white rounded text-[10px] font-bold">
                {activeAlertsCount}
              </span>
            )}
          </button>

          {/* User Role Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-100 border border-slate-200 rounded text-xs text-slate-700">
            <UserCheck className="w-3.5 h-3.5 text-slate-600" />
            <span className="font-mono text-[11px] hidden sm:inline font-semibold">LEA_OFFICER</span>
          </div>
        </div>
      </div>
    </header>
  );
};
