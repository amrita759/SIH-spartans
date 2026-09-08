import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';
import { Case } from '../types/case';
import { CaseTable } from '../components/tables/CaseTable';
import {
  FolderOpen,
  Search,
  Filter,
  Play,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sparkles,
  Plus
} from 'lucide-react';
import { IntakeModal } from '../components/intake/IntakeModal';

interface CasesProps {
  onSelectCase: (caseItem: Case) => void;
  onRunPrediction: (caseItem: Case) => void;
}

export const Cases: React.FC<CasesProps> = ({ onSelectCase, onRunPrediction }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isIntakeOpen, setIsIntakeOpen] = useState(false);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const data = await api.getCases();
      setCases(data);
    } catch (err) {
      console.error('Failed to load cases:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleRunPrediction = async (caseItem: Case) => {
    setActionMessage(`Executing LightGBM cash-out location scoring for ${caseItem.case_id}...`);
    try {
      await onRunPrediction(caseItem);
      setActionMessage(`Scoring complete! Top cash-out locations ranked for ${caseItem.case_id}.`);
      await fetchCases();
    } catch (err) {
      setActionMessage(`Inference failed for ${caseItem.case_id}.`);
    } finally {
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  // Unique states for filtering
  const availableStates = useMemo(() => {
    const states = Array.from(new Set(cases.map((c) => c.state).filter(Boolean)));
    return states.sort();
  }, [cases]);

  // Filtered cases
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const matchesSearch =
        c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.fraud_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.district?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'ALL' || c.case_status === statusFilter;
      const matchesState = stateFilter === 'ALL' || c.state === stateFilter;

      return matchesSearch && matchesStatus && matchesState;
    });
  }, [cases, searchTerm, statusFilter, stateFilter]);

  return (
    <div className="space-y-6">
      {/* Header & Demo Tag */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
              Active Cybercrime Complaints
            </h1>
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-semibold border border-slate-200">
              SYNTHETIC / DEMONSTRATION DATA
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-world grounded incident dossiers prepared strictly at prediction boundary time $T$.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => setIsIntakeOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Complaint Intake</span>
          </button>
          <button
            onClick={fetchCases}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-slate-600' : ''}`} />
            <span>Refresh Complaints</span>
          </button>
        </div>
      </div>

      {/* Action Notification Banner */}
      {actionMessage && (
        <div className="p-3 rounded bg-slate-900 text-white text-xs flex items-center justify-between shadow-xs animate-in fade-in">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400 animate-spin" />
            <span>{actionMessage}</span>
          </div>
        </div>
      )}

      {/* Filters Bar */}
      <div className="p-3.5 rounded-md bg-white border border-slate-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by Case ID, Modus Operandi, District..."
            className="w-full pl-9 pr-3 py-1.5 rounded bg-white border border-slate-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-800"
          />
        </div>

        {/* Dropdown Filters */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-xs text-slate-600">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-white border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 focus:outline-none focus:border-slate-800"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">NEW</option>
              <option value="PREDICTION_READY">PREDICTION READY</option>
              <option value="UNDER_REVIEW">UNDER REVIEW</option>
              <option value="MONITORED">MONITORED</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-600">
            <span>State:</span>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="bg-white border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 focus:outline-none focus:border-slate-800"
            >
              <option value="ALL">All States</option>
              {availableStates.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Cases Table */}
      <CaseTable
        cases={filteredCases}
        onSelectCase={onSelectCase}
        onRunPrediction={handleRunPrediction}
        isLoading={isLoading}
      />

      {/* New Complaint Intake Modal */}
      <IntakeModal
        isOpen={isIntakeOpen}
        onClose={() => setIsIntakeOpen(false)}
        onCaseCreated={(newCase) => {
          setActionMessage(`Registered complaint dossier for ${newCase.case_id}. Initializing prediction...`);
          fetchCases();
        }}
      />
    </div>
  );
};
