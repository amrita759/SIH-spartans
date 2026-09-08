import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Case } from '../types/case';
import { PredictionResult } from '../types/prediction';
import { RiskBadge } from '../components/common/RiskBadge';
import { LocationTable } from '../components/tables/LocationTable';
import { LocationDrawer, DrawerLocationData } from '../components/map/LocationDrawer';
import { Target, Clock, Cpu, Eye, RefreshCw, FolderOpen } from 'lucide-react';

interface PredictionsPageProps {
  onOpenCase: (caseId: string) => void;
}

export const PredictionsPage: React.FC<PredictionsPageProps> = ({ onOpenCase }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionResult | null>(null);
  const [selectedDrawerLoc, setSelectedDrawerLoc] = useState<DrawerLocationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const allCases = await api.getCases();
      setCases(allCases);

      const predictedCase = allCases.find((c) => c.latest_prediction_id);
      if (predictedCase?.latest_prediction_id) {
        const pred = await api.getPrediction(predictedCase.latest_prediction_id);
        setSelectedPrediction(pred);
      }
    } catch (err) {
      console.error('Failed to load predictions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectCasePrediction = async (predictionId: string) => {
    try {
      const pred = await api.getPrediction(predictionId);
      setSelectedPrediction(pred);
    } catch (err) {
      console.error('Failed to load prediction:', err);
    }
  };

  const predictedCases = cases.filter((c) => c.prediction_status === 'COMPLETED' && c.latest_prediction_id);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h1 className="text-base font-bold text-slate-900 tracking-tight">
            Predictive Analysis Audit Trail
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable log of LightGBM risk predictions, scored candidate sets, and operational horizons.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-slate-600' : 'text-slate-500'}`} />
          <span>Refresh Logs</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: Scored Predictions List */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-slate-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Scored Cases Registry ({predictedCases.length})
            </h2>
          </div>

          {predictedCases.length === 0 ? (
            <div className="p-8 text-center bg-white rounded border border-slate-200 text-xs text-slate-500">
              No completed predictions found in database. Run a predictive analysis on an active case.
            </div>
          ) : (
            <div className="space-y-2">
              {predictedCases.map((c) => {
                const isSelected = selectedPrediction?.prediction_id === c.latest_prediction_id;
                return (
                  <div
                    key={c.case_id}
                    onClick={() => c.latest_prediction_id && handleSelectCasePrediction(c.latest_prediction_id)}
                    className={`p-3.5 rounded border transition cursor-pointer shadow-xs ${
                      isSelected
                        ? 'border-slate-900 bg-slate-50 ring-1 ring-slate-900'
                        : 'border-slate-200 bg-white hover:bg-slate-50/80'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="font-mono text-xs font-bold text-slate-900">{c.case_id}</span>
                        <p className="text-xs text-slate-700 font-medium capitalize mt-0.5">{c.fraud_type.replace(/_/g, ' ')}</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          Jurisdiction: {c.district}, {c.state}
                        </p>
                      </div>
                      {c.risk_level && <RiskBadge level={c.risk_level} />}
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
                      <span className="font-mono text-slate-400">ID: {c.latest_prediction_id}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenCase(c.case_id);
                        }}
                        className="text-slate-700 hover:text-slate-900 font-medium flex items-center gap-1 cursor-pointer"
                      >
                        <FolderOpen className="w-3 h-3 text-slate-500" />
                        <span>Case Dossier</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Selected Prediction Details & Scored Candidate Table */}
        <div className="lg:col-span-2 space-y-3">
          {selectedPrediction ? (
            <>
              {/* Header Card */}
              <div className="p-3.5 rounded border border-slate-200 bg-white shadow-xs flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-900">
                      {selectedPrediction.prediction_id}
                    </span>
                    <span className="text-slate-400">•</span>
                    <span className="font-mono text-xs text-slate-700 font-medium">
                      Case: {selectedPrediction.case_id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Prediction Snapshot T: {selectedPrediction.prediction_time} • Engine: {selectedPrediction.model_version}
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <div className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-slate-700">
                    <span className="text-slate-500">Window:</span> Next {selectedPrediction.prediction_window_hours}h
                  </div>
                  <div className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-slate-700">
                    <span className="text-slate-500">Candidates:</span> {selectedPrediction.total_candidates_scored} scored
                  </div>
                </div>
              </div>

              {/* Candidates Table */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                  Scored &amp; Ranked Cash-Out Terminals (Top-K)
                </h3>
                <LocationTable
                  locations={selectedPrediction.locations || []}
                  onSelectLocation={(loc) => {
                    setSelectedDrawerLoc({
                      ...loc,
                      bank_name: loc.bank_name
                    });
                  }}
                  selectedLocationId={selectedDrawerLoc?.location_id}
                />
              </div>
            </>
          ) : (
            <div className="p-16 text-center bg-white rounded border border-slate-200 text-slate-500 text-xs">
              Select a scored prediction to inspect candidate rankings and TreeSHAP attributions.
            </div>
          )}
        </div>
      </div>

      {/* Location Drawer */}
      <LocationDrawer
        location={selectedDrawerLoc}
        onClose={() => setSelectedDrawerLoc(null)}
        predictionWindowHours={selectedPrediction?.prediction_window_hours || 6}
      />
    </div>
  );
};
