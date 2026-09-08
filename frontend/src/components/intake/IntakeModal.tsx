import React, { useState } from 'react';
import { api } from '../../services/api';
import { Case } from '../../types/case';
import { ComplaintParseResponse } from '../../types/prediction';
import { X, Sparkles, CheckCircle, FileText, ArrowRight, AlertCircle } from 'lucide-react';

interface IntakeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCaseCreated: (newCase: Case) => void;
}

export const IntakeModal: React.FC<IntakeModalProps> = ({ isOpen, onClose, onCaseCreated }) => {
  const [complaintText, setComplaintText] = useState(
    'Victim reported that after clicking on a fraudulent electricity bill update link, Rs. 1,25,000 was debited via UPI to mule account. Incident occurred in Mumbai Suburban, Maharashtra. Suspect was reported attempting ATM cash withdrawal.'
  );
  const [isParsing, setIsParsing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [parseResult, setParseResult] = useState<ComplaintParseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleParse = async () => {
    if (!complaintText.trim()) return;
    setIsParsing(true);
    setError(null);
    try {
      const res = await api.parseComplaint(complaintText);
      setParseResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to parse complaint text.');
    } finally {
      setIsParsing(false);
    }
  };

  const handleCreateCase = async () => {
    if (!parseResult) return;
    setIsCreating(true);
    setError(null);
    try {
      const casePayload: Partial<Case> = {
        case_id: parseResult.complaint_id,
        case_status: 'NEW',
        fraud_type: parseResult.detected_fraud_type,
        fraud_amount: parseResult.detected_amount,
        complaint_time: new Date().toISOString(),
        prediction_time: new Date().toISOString(),
        prediction_window_hours: 6,
        prediction_status: 'PENDING',
        state: parseResult.detected_state,
        district: parseResult.detected_district,
        victim_latitude: parseResult.suggested_latitude,
        victim_longitude: parseResult.suggested_longitude,
        last_activity_channel: parseResult.detected_channel,
        last_activity_amount: parseResult.detected_amount,
        last_activity_latitude: parseResult.suggested_latitude,
        last_activity_longitude: parseResult.suggested_longitude
      };
      const created = await api.createCase(casePayload);
      onCaseCreated(created);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to create case.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
      <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-slate-800" />
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                New Cybercrime Complaint Intake
              </h2>
              <p className="text-[11px] text-slate-500">
                Deterministic NLP parameter extraction from raw FIR or 1930 portal narrative
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
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">
              Unstructured Complaint Narrative (FIR / 1930 Portal Excerpt):
            </label>
            <textarea
              rows={4}
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              placeholder="Paste complaint statement, transaction messages, or FIR excerpt..."
              className="w-full p-3 rounded bg-white border border-slate-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-800 font-sans"
            />
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleParse}
              disabled={isParsing || !complaintText.trim()}
              className="flex items-center gap-2 px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
            >
              <Sparkles className={`w-3.5 h-3.5 ${isParsing ? 'animate-spin' : ''}`} />
              <span>{isParsing ? 'Analyzing Narrative...' : 'Parse with Deterministic NLP'}</span>
            </button>
          </div>

          {/* Parsed Result Preview */}
          {parseResult && (
            <div className="p-4 rounded bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span className="text-xs font-bold text-slate-900">
                    Extracted Intelligence Parameters
                  </span>
                </div>
                <span className="font-mono text-[11px] text-slate-700 font-bold">
                  {parseResult.complaint_id}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2.5 text-xs">
                <div className="p-2.5 rounded bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block uppercase font-semibold">Modus Operandi</span>
                  <span className="font-semibold text-slate-900 capitalize">
                    {parseResult.detected_fraud_type.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block uppercase font-semibold">Defrauded Sum</span>
                  <span className="font-semibold font-mono text-slate-900">
                    ₹{parseResult.detected_amount.toLocaleString('en-IN')}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block uppercase font-semibold">Payment Channel</span>
                  <span className="font-semibold text-slate-900 font-mono">
                    {parseResult.detected_channel}
                  </span>
                </div>
                <div className="p-2.5 rounded bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block uppercase font-semibold">Jurisdiction</span>
                  <span className="font-semibold text-slate-900 truncate block">
                    {parseResult.detected_district}, {parseResult.detected_state}
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-slate-600 flex items-center justify-between pt-1">
                <span>
                  Coordinates: {parseResult.suggested_latitude.toFixed(4)}, {parseResult.suggested_longitude.toFixed(4)}
                </span>
                {parseResult.detected_bank && (
                  <span>Bank Entity: <strong className="text-slate-800">{parseResult.detected_bank}</strong></span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-3.5 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded text-slate-600 hover:text-slate-900 text-xs font-medium cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleCreateCase}
            disabled={!parseResult || isCreating}
            className="flex items-center gap-1.5 px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <span>{isCreating ? 'Registering...' : 'Register Complaint Dossier'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
