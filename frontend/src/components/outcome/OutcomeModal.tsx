import React, { useState } from 'react';
import { api } from '../../services/api';
import { RankedLocation, OutcomeResponse } from '../../types/prediction';
import { X, CheckCircle, AlertTriangle, ShieldCheck, Clock, FileCheck } from 'lucide-react';

interface OutcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
  predictionId: string;
  candidateLocations: RankedLocation[];
  onOutcomeSaved?: (res: OutcomeResponse) => void;
}

export const OutcomeModal: React.FC<OutcomeModalProps> = ({
  isOpen,
  onClose,
  caseId,
  predictionId,
  candidateLocations,
  onOutcomeSaved
}) => {
  const [actualLocationId, setActualLocationId] = useState(
    candidateLocations.length > 0 ? candidateLocations[0].location_id : ''
  );
  const [customLocationId, setCustomLocationId] = useState('');
  const [useCustomLocation, setUseCustomLocation] = useState(false);
  const [actualWithdrawalTime, setActualWithdrawalTime] = useState(
    new Date().toISOString().slice(0, 16)
  );
  const [withdrawalOccurred, setWithdrawalOccurred] = useState(true);
  const [apprehended, setApprehended] = useState(false);
  const [notes, setNotes] = useState('Ground verification confirmed by patrol team.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [outcomeResult, setOutcomeResult] = useState<OutcomeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalLocationId = useCustomLocation ? customLocationId.trim() : actualLocationId;
    if (!finalLocationId) {
      setError('Please select or specify the actual ATM/CRM location ID.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await api.recordOutcome({
        case_id: caseId,
        prediction_id: predictionId,
        actual_location_id: finalLocationId,
        actual_withdrawal_time: actualWithdrawalTime ? new Date(actualWithdrawalTime).toISOString() : undefined,
        withdrawal_occurred: withdrawalOccurred,
        apprehended: apprehended,
        notes: notes
      });
      setOutcomeResult(res);
      if (onOutcomeSaved) {
        onOutcomeSaved(res);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to record outcome.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
      <div className="relative w-full max-w-xl bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <FileCheck className="w-5 h-5 text-slate-800" />
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Record Post-Incident Outcome
              </h2>
              <p className="text-[11px] text-slate-500 font-mono">
                Case: {caseId} • Prediction: {predictionId}
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

        {/* Modal Body */}
        <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
          {error && (
            <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {outcomeResult ? (
            <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-3 animate-in fade-in">
              <div className="flex items-center gap-2 text-emerald-700">
                <CheckCircle className="w-5 h-5 shrink-0" />
                <span className="text-sm font-bold text-slate-900">{outcomeResult.message}</span>
              </div>

              <div className="p-3.5 rounded bg-white border border-slate-200 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Actual Location Terminal:</span>
                  <span className="font-mono font-bold text-slate-900">{outcomeResult.actual_location_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Retrospective Prediction Rank:</span>
                  <span className="font-mono font-bold text-slate-900">
                    {outcomeResult.rank_of_actual ? `#${outcomeResult.rank_of_actual}` : 'Not in Top 10'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Hit Accuracy Tier:</span>
                  <span className="font-semibold text-slate-900">
                    {outcomeResult.in_top_3 ? 'Top 3 Hit' : outcomeResult.in_top_5 ? 'Top 5 Hit' : outcomeResult.in_top_10 ? 'Top 10 Hit' : 'Outside Top 10'}
                  </span>
                </div>
                {outcomeResult.lead_time_hours !== undefined && outcomeResult.lead_time_hours !== null && (
                  <div className="flex justify-between">
                    <span className="text-slate-500">Actionable Lead Time:</span>
                    <span className="font-mono font-bold text-slate-900">{outcomeResult.lead_time_hours.toFixed(2)} hours in advance</span>
                  </div>
                )}
              </div>

              <p className="text-[11px] text-slate-500">
                Outcome logged to central audit repository. Used for ground truth accuracy auditing and offline drift tracking.
              </p>

              <button
                onClick={onClose}
                className="w-full py-2 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
              >
                Close
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Actual Cash-Out Terminal Location:
                </label>
                <div className="space-y-2">
                  <select
                    disabled={useCustomLocation}
                    value={actualLocationId}
                    onChange={(e) => setActualLocationId(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-slate-800 disabled:opacity-40"
                  >
                    {candidateLocations.map((loc) => (
                      <option key={loc.location_id} value={loc.location_id}>
                        Rank #{loc.rank} - {loc.location_id} ({loc.bank_name || 'ATM'} - {loc.location_type})
                      </option>
                    ))}
                  </select>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="customLocCheck"
                      checked={useCustomLocation}
                      onChange={(e) => setUseCustomLocation(e.target.checked)}
                      className="rounded border-slate-300 text-slate-900 focus:ring-0 cursor-pointer"
                    />
                    <label htmlFor="customLocCheck" className="text-[11px] text-slate-600 cursor-pointer">
                      Location was outside forecasted Top candidates (Specify custom Terminal ID)
                    </label>
                  </div>

                  {useCustomLocation && (
                    <input
                      type="text"
                      value={customLocationId}
                      onChange={(e) => setCustomLocationId(e.target.value)}
                      placeholder="e.g. 00010ATM00000A7B"
                      className="w-full px-3 py-2 rounded bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-slate-800 font-mono"
                    />
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Actual Withdrawal Timestamp:
                </label>
                <input
                  type="datetime-local"
                  value={actualWithdrawalTime}
                  onChange={(e) => setActualWithdrawalTime(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <label className="flex items-center gap-2 p-2.5 rounded bg-slate-50 border border-slate-200 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={withdrawalOccurred}
                    onChange={(e) => setWithdrawalOccurred(e.target.checked)}
                    className="rounded border-slate-300 text-slate-900"
                  />
                  <span className="text-xs text-slate-700">Cash Withdrawal Occurred</span>
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded bg-slate-50 border border-slate-200 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={apprehended}
                    onChange={(e) => setApprehended(e.target.checked)}
                    className="rounded border-slate-300 text-slate-900"
                  />
                  <span className="text-xs text-slate-700">Mule / Courier Apprehended</span>
                </label>
              </div>

              {/* Patrol Team Ground Verification Section */}
              <div className="p-3 rounded bg-blue-50/60 border border-blue-200 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-xs font-semibold text-blue-950 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notes.toLowerCase().includes('ground verification')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNotes((prev) =>
                            prev.includes('Ground verification done by patrol team.')
                              ? prev
                              : `Ground verification done by patrol team. ${prev}`.trim()
                          );
                        } else {
                          setNotes((prev) =>
                            prev.replace(/Ground verification (done|confirmed) by patrol team\.\s*/gi, '').trim()
                          );
                        }
                      }}
                      className="rounded border-blue-300 text-blue-600 focus:ring-0"
                    />
                    <span>Ground verification done by patrol team</span>
                  </label>
                  <span className="text-[10px] font-mono uppercase bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded border border-blue-200">
                    Field Action
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
                  <span className="text-[10px] text-slate-500 self-center">Quick tags:</span>
                  {[
                    'Ground verification done by patrol team.',
                    'Patrol intercepted courier with stolen cards.',
                    'Cash withdrawal thwarted by patrol unit.',
                    'CCTV verified - suspect fled prior to arrival.'
                  ].map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => setNotes(tag)}
                      className="px-2 py-0.5 rounded bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-[10px] transition cursor-pointer"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Investigator &amp; Patrol Operational Notes:
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Verification details, CCTV findings, or interception remarks..."
                  className="w-full p-2.5 rounded bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-slate-800"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3.5 py-1.5 rounded text-slate-600 hover:text-slate-900 text-xs cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
                >
                  {isSubmitting ? 'Recording Outcome...' : 'Save Feedback Outcome'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
