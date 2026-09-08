import React from 'react';
import { ExplanationFactor } from '../../types/prediction';
import { TrendingUp, TrendingDown, Info, ShieldAlert } from 'lucide-react';

interface ShapFactorListProps {
  factors: ExplanationFactor[];
  locationId?: string;
  riskScore?: number;
}

export const ShapFactorList: React.FC<ShapFactorListProps> = ({
  factors,
  locationId,
  riskScore
}) => {
  if (!factors || factors.length === 0) {
    return (
      <div className="p-4 bg-slate-50 border border-slate-200 rounded text-xs text-slate-500 text-center">
        No factor attribution data available for this candidate.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-slate-700" />
          <span className="text-xs font-bold text-slate-900 tracking-wide uppercase">
            Model Behavioral Attribution (TreeSHAP)
          </span>
        </div>
        {locationId && (
          <span className="font-mono text-[11px] text-slate-600">
            {locationId} {riskScore ? `• Risk: ${riskScore.toFixed(1)}/100` : ''}
          </span>
        )}
      </div>

      <div className="space-y-2">
        {factors.map((factor, idx) => {
          const isIncrease = factor.impact === 'INCREASES_RISK' || factor.contribution > 0;
          return (
            <div
              key={idx}
              className={`p-2.5 rounded border transition-all ${
                isIncrease
                  ? 'bg-red-50/50 border-red-200 hover:border-red-300'
                  : 'bg-emerald-50/50 border-emerald-200 hover:border-emerald-300'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2">
                  <div className={`mt-0.5 p-1 rounded ${isIncrease ? 'text-red-700 bg-red-100' : 'text-emerald-700 bg-emerald-100'}`}>
                    {isIncrease ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-900">{factor.description}</p>
                    <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                      Feature: <span className="text-slate-700 font-semibold">{factor.feature}</span>
                    </p>
                  </div>
                </div>
                <div className="text-right whitespace-nowrap">
                  <span
                    className={`font-mono text-xs font-bold ${
                      isIncrease ? 'text-red-700' : 'text-emerald-700'
                    }`}
                  >
                    {factor.contribution > 0 ? `+${factor.contribution.toFixed(3)}` : factor.contribution.toFixed(3)}
                  </span>
                  <p className="text-[9px] uppercase tracking-wider text-slate-500 mt-0.5">
                    {isIncrease ? 'Increases Risk' : 'Decreases Risk'}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-start gap-2 p-2.5 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
        <Info className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
        <span>
          SHAP values represent localized model prioritization dynamics computed at snapshot time $T$. Factors identify operational risk indicators and do not constitute criminal evidence.
        </span>
      </div>
    </div>
  );
};
