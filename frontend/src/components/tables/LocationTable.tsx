import React from 'react';
import { RankedLocation } from '../../types/prediction';
import { RiskBadge } from '../common/RiskBadge';
import { Eye } from 'lucide-react';

interface LocationTableProps {
  locations: RankedLocation[];
  onSelectLocation: (loc: RankedLocation) => void;
  selectedLocationId?: string | null;
}

export const LocationTable: React.FC<LocationTableProps> = ({
  locations,
  onSelectLocation,
  selectedLocationId
}) => {
  if (!locations || locations.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-md border border-slate-200">
        No candidate locations scored yet. Select an active complaint and run predictive analysis.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-slate-200 bg-white shadow-xs">
      <table className="w-full text-left border-collapse text-xs">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 uppercase tracking-wider font-semibold text-[11px]">
            <th className="py-2.5 px-4">Rank</th>
            <th className="py-2.5 px-4">Terminal Code</th>
            <th className="py-2.5 px-4">Type</th>
            <th className="py-2.5 px-4">Bank</th>
            <th className="py-2.5 px-4">District / State</th>
            <th className="py-2.5 px-4">Risk Level</th>
            <th className="py-2.5 px-4">Top Model Factor</th>
            <th className="py-2.5 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 font-sans">
          {locations.map((loc) => {
            const isSelected = selectedLocationId === loc.location_id;
            const topFactor = loc.top_factors?.[0]?.description || 'Proximity and velocity alignment';

            return (
              <tr
                key={loc.location_id}
                onClick={() => onSelectLocation(loc)}
                className={`transition-colors cursor-pointer ${
                  isSelected
                    ? 'bg-slate-100/90'
                    : 'hover:bg-slate-50/80'
                }`}
              >
                <td className="py-2.5 px-4 font-mono font-bold text-slate-900">
                  <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold">
                    #{loc.rank}
                  </span>
                </td>
                <td className="py-2.5 px-4 font-mono font-bold text-slate-900">
                  {loc.location_id}
                </td>
                <td className="py-2.5 px-4">
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                    {loc.location_type || 'ATM'}
                  </span>
                </td>
                <td className="py-2.5 px-4 font-medium text-slate-800">
                  {loc.bank_name || 'Bank Terminal'}
                </td>
                <td className="py-2.5 px-4 text-slate-600">
                  {loc.district}, {loc.state}
                </td>
                <td className="py-2.5 px-4">
                  <RiskBadge level={loc.risk_level} score={loc.risk_score} />
                </td>
                <td className="py-2.5 px-4 text-slate-600 max-w-xs truncate" title={topFactor}>
                  {topFactor}
                </td>
                <td className="py-2.5 px-4 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectLocation(loc);
                    }}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-medium transition cursor-pointer"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Dossier</span>
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
