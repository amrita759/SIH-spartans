import React from 'react';
import { Case } from '../../types/case';
import { StatusBadge } from '../common/StatusBadge';
import { RiskBadge } from '../common/RiskBadge';
import { Play, Eye } from 'lucide-react';

interface CaseTableProps {
  cases: Case[];
  onSelectCase: (caseItem: Case) => void;
  onRunPrediction: (caseItem: Case) => void;
  isLoading?: boolean;
}

export const CaseTable: React.FC<CaseTableProps> = ({
  cases,
  onSelectCase,
  onRunPrediction,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="p-12 text-center text-slate-500 bg-white rounded-md border border-slate-200">
        Fetching active cybercrime complaints from central intelligence repository...
      </div>
    );
  }

  if (!cases || cases.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-md border border-slate-200">
        No cybercrime complaints match the current filter.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-slate-200 bg-white shadow-xs">
      <table className="w-full text-left border-collapse text-xs">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 uppercase tracking-wider font-semibold text-[11px]">
            <th className="py-2.5 px-4">Case ID</th>
            <th className="py-2.5 px-4">Modus Operandi</th>
            <th className="py-2.5 px-4">Disputed Amount</th>
            <th className="py-2.5 px-4">Jurisdiction</th>
            <th className="py-2.5 px-4">Case Status</th>
            <th className="py-2.5 px-4">Prediction Risk</th>
            <th className="py-2.5 px-4 text-right">Intervention</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 font-sans">
          {cases.map((c) => {
            const hasPrediction = c.prediction_status === 'COMPLETED';

            return (
              <tr
                key={c.case_id}
                onClick={() => onSelectCase(c)}
                className="hover:bg-slate-50/80 transition-colors cursor-pointer"
              >
                <td className="py-2.5 px-4 font-mono font-bold text-slate-900">
                  {c.case_id}
                </td>
                <td className="py-2.5 px-4 capitalize text-slate-800 font-medium">
                  {c.fraud_type.replace(/_/g, ' ')}
                </td>
                <td className="py-2.5 px-4 font-mono font-semibold text-slate-900">
                  ₹{c.fraud_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </td>
                <td className="py-2.5 px-4 text-slate-700">
                  {c.district}, <span className="text-slate-500">{c.state}</span>
                </td>
                <td className="py-2.5 px-4">
                  <StatusBadge status={c.case_status} />
                </td>
                <td className="py-2.5 px-4">
                  {c.risk_level ? (
                    <RiskBadge level={c.risk_level} />
                  ) : (
                    <span className="text-slate-400 font-mono text-[11px]">- PENDING -</span>
                  )}
                </td>
                <td className="py-2.5 px-4 text-right">
                  <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onSelectCase(c)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-medium transition cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Details</span>
                    </button>
                    <button
                      onClick={() => onRunPrediction(c)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-900 text-white text-xs font-medium shadow-xs transition cursor-pointer"
                    >
                      <Play className="w-3 h-3 fill-white" />
                      <span>{hasPrediction ? 'Re-Score' : 'Predict'}</span>
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
