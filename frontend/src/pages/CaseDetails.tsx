import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';
import { Case } from '../types/case';
import { PredictionResult, RankedLocation } from '../types/prediction';
import { StatusBadge } from '../components/common/StatusBadge';
import { RiskBadge } from '../components/common/RiskBadge';
import { RiskMap, MapPoint } from '../components/map/RiskMap';
import { LocationTable } from '../components/tables/LocationTable';
import { LocationDrawer, DrawerLocationData } from '../components/map/LocationDrawer';
import { ShapFactorList } from '../components/explainability/ShapFactorList';
import {
  ArrowLeft,
  Play,
  Clock,
  Building2,
  MapPin,
  Cpu,
  TrendingUp,
  AlertTriangle,
  Network,
  CreditCard,
  ShieldCheck,
  RefreshCw,
  CheckSquare,
  Radio,
  Car
} from 'lucide-react';
import { OutcomeModal } from '../components/outcome/OutcomeModal';
import { PatrolDispatchModal } from '../components/dispatch/PatrolDispatchModal';

interface CaseDetailsProps {
  caseId: string;
  onBack: () => void;
}

export const CaseDetails: React.FC<CaseDetailsProps> = ({ caseId, onBack }) => {
  const [caseItem, setCaseItem] = useState<Case | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [selectedDrawerLocation, setSelectedDrawerLocation] = useState<DrawerLocationData | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [isOutcomeOpen, setIsOutcomeOpen] = useState(false);
  const [isDispatchOpen, setIsDispatchOpen] = useState(false);
  const [activePatrolUnit, setActivePatrolUnit] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchCaseDetails = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const c = await api.getCase(caseId);
      setCaseItem(c);

      if (c.latest_prediction_id) {
        const pred = await api.getPrediction(c.latest_prediction_id);
        setPrediction(pred);
      }
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to load case details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCaseDetails();
  }, [caseId]);

  const handleRunPrediction = async () => {
    if (!caseItem) return;
    setIsPredicting(true);
    try {
      const res = await api.runPrediction(caseItem.case_id, 10);
      setPrediction(res);
      // Refresh case state
      const updatedCase = await api.getCase(caseItem.case_id);
      setCaseItem(updatedCase);
    } catch (err: any) {
      alert('Failed to generate predictive intelligence: ' + (err?.message || 'Unknown error'));
    } finally {
      setIsPredicting(false);
    }
  };

  // Convert prediction locations to MapPoint
  const mapPoints: MapPoint[] = useMemo(() => {
    if (!prediction || !prediction.locations) return [];
    return prediction.locations.map((loc) => ({
      location_id: loc.location_id,
      location_name: loc.location_name,
      location_type: loc.location_type,
      bank: loc.bank_name,
      latitude: loc.latitude,
      longitude: loc.longitude,
      risk_score: loc.risk_score,
      risk_level: loc.risk_level,
      rank: loc.rank,
      district: loc.district,
      state: loc.state
    }));
  }, [prediction]);

  const handleSelectLocation = (loc: any) => {
    const fullLoc = prediction?.locations.find((l) => l.location_id === loc.location_id);
    if (fullLoc) {
      setSelectedDrawerLocation({
        ...fullLoc,
        bank_name: fullLoc.bank_name
      });
    } else {
      setSelectedDrawerLocation({
        ...loc,
        bank_name: loc.bank || loc.bank_name
      });
    }
  };

  if (isLoading) {
    return (
      <div className="p-16 text-center text-slate-500 bg-white rounded-md border border-slate-200">
        Retrieving intelligence dossier for {caseId}...
      </div>
    );
  }

  if (!caseItem) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-md border border-slate-200 space-y-3">
        <p className="text-red-700 font-bold">Case with ID '{caseId}' not found.</p>
        <button
          onClick={onBack}
          className="px-3.5 py-1.5 rounded bg-slate-900 text-white text-xs font-medium cursor-pointer"
        >
          Return to Cases
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button & Top Case Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 shadow-xs transition cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold font-mono text-slate-900">{caseItem.case_id}</h1>
              <StatusBadge status={caseItem.case_status} />
              {caseItem.risk_level && <RiskBadge level={caseItem.risk_level} />}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Complaint Registration: {caseItem.complaint_time || 'Timestamp recorded'} • Jurisdiction: {caseItem.district}, {caseItem.state}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start md:self-auto flex-wrap">
          {prediction && (
            <>
              <button
                onClick={() => setIsDispatchOpen(true)}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded text-xs font-semibold shadow-xs transition cursor-pointer ${
                  caseItem.case_status === 'MONITORED'
                    ? 'bg-blue-100 text-blue-900 border border-blue-300'
                    : 'bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200'
                }`}
              >
                <Radio className="w-3.5 h-3.5 text-blue-700 animate-pulse" />
                <span>{caseItem.case_status === 'MONITORED' ? 'Patrol Dispatched' : 'Dispatch to Nearby Patrol'}</span>
              </button>

              <button
                onClick={() => setIsOutcomeOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold shadow-xs transition cursor-pointer"
              >
                <CheckSquare className="w-4 h-4 text-emerald-700" />
                <span>Record Ground Outcome</span>
              </button>
            </>
          )}
          <button
            onClick={handleRunPrediction}
            disabled={isPredicting}
            className="flex items-center gap-2 px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-white ${isPredicting ? 'animate-spin' : ''}`} />
            <span>{isPredicting ? 'Scoring Candidates...' : 'Run Predictive Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Active Patrol Surveillance Banner (When case is MONITORED) */}
      {(caseItem.case_status === 'MONITORED' || activePatrolUnit) && prediction?.locations?.[0] && (
        <div className="p-3.5 rounded border border-blue-200 bg-blue-50/80 text-xs text-blue-950 flex flex-wrap items-center justify-between gap-3 shadow-xs">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded bg-blue-600 text-white shrink-0">
              <Car className="w-4 h-4" />
            </div>
            <div>
              <p className="font-bold text-slate-900 flex items-center gap-2">
                <span>Active Tactical Patrol Surveillance • {activePatrolUnit || 'PCR-DELTA-04'} Deployed</span>
                <span className="text-[10px] font-mono uppercase bg-blue-200/80 text-blue-900 px-1.5 py-0.5 rounded font-bold">
                  Surveillance Active
                </span>
              </p>
              <p className="text-[11px] text-slate-600 mt-0.5">
                Target: <span className="font-semibold">{prediction.locations[0]?.bank_name} ({prediction.locations[0]?.location_type})</span> • Rank #1 Candidate (ID: <code className="font-mono">{prediction.locations[0]?.location_id}</code>). Field patrol on-site awaiting ground verification.
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsOutcomeOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-900 hover:bg-blue-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <CheckSquare className="w-3.5 h-3.5" />
            <span>Record Ground Verification</span>
          </button>
        </div>
      )}

      {/* Case Overview & Transaction Trail Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Box 1: Financial Disputed Summary */}
        <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <CreditCard className="w-4 h-4 text-slate-600" />
            <span>Complaint Financials</span>
          </div>
          <p className="text-2xl font-bold font-mono text-slate-900">
            ₹{caseItem.fraud_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </p>
          <p className="text-xs text-slate-600 capitalize">
            Modus Operandi: <span className="text-slate-900 font-semibold">{caseItem.fraud_type.replace(/_/g, ' ')}</span>
          </p>
        </div>

        {/* Box 2: Pre-Prediction Activity Snapshot (Strict Boundary T) */}
        <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <Clock className="w-4 h-4 text-slate-600" />
            <span>Last Known Activity (Time T)</span>
          </div>
          <div className="text-xs space-y-1 text-slate-700">
            <p>
              Channel: <span className="font-mono text-slate-900 font-bold">{caseItem.last_activity_channel || 'UPI'}</span>
            </p>
            <p>
              Outflow: <span className="font-mono font-semibold text-slate-900">₹{(caseItem.last_activity_amount || 0).toLocaleString('en-IN')}</span>
            </p>
            <p className="font-mono text-[11px] text-slate-500 truncate">
              Mule Node: ({caseItem.last_activity_latitude?.toFixed(4)}, {caseItem.last_activity_longitude?.toFixed(4)})
            </p>
          </div>
        </div>

        {/* Box 3: Model Operational Horizon */}
        <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase">
            <Cpu className="w-4 h-4 text-slate-600" />
            <span>Predictive Parameters</span>
          </div>
          <div className="text-xs space-y-1 text-slate-700">
            <p>Model Engine: <span className="font-mono font-semibold text-slate-900">LightGBM ({prediction?.model_version || 'v1.0.0'})</span></p>
            <p>Target Horizon: <span className="font-mono text-slate-900 font-bold">Next {caseItem.prediction_window_hours || 6} Hours</span></p>
            {prediction?.urgency_level && (
              <p className="text-[11px] font-semibold text-amber-800">
                Urgency Window: {prediction.urgency_level} ({prediction.remaining_hours?.toFixed(1)}h remaining)
              </p>
            )}
            <p className="text-slate-500 text-[11px]">Strict Zero-Leakage Boundary Enforced</p>
          </div>
        </div>
      </div>

      {/* GIS Surveillance Map for Case Candidates */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-slate-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Candidate ATM / CRM Spatial Risk Grid (20km Jurisdictional Radius)
            </h2>
          </div>
          {prediction && (
            <span className="text-xs font-mono text-slate-600">
              Prediction ID: <span className="font-bold text-slate-900">{prediction.prediction_id}</span>
            </span>
          )}
        </div>

        <RiskMap
          locations={mapPoints}
          selectedLocationId={selectedDrawerLocation?.location_id}
          onSelectLocation={handleSelectLocation}
          height="420px"
        />
      </div>

      {/* Top 10 Scored Locations Table */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-slate-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Ranked Candidate Cash-Out Locations for Immediate LEA Action
            </h2>
          </div>
        </div>

        {prediction?.locations && prediction.locations.length > 0 ? (
          <LocationTable
            locations={prediction.locations}
            onSelectLocation={handleSelectLocation}
            selectedLocationId={selectedDrawerLocation?.location_id}
          />
        ) : (
          <div className="p-8 text-center bg-white rounded-md border border-slate-200 space-y-3">
            <p className="text-slate-500 text-xs">
              No predictive risk scores computed for this complaint yet.
            </p>
            <button
              onClick={handleRunPrediction}
              disabled={isPredicting}
              className="inline-flex items-center gap-2 px-4 py-2 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Run Predictive Analysis Now</span>
            </button>
          </div>
        )}
      </div>

      {/* Selected Location SHAP Explanation Section if available */}
      {prediction?.locations && prediction.locations.length > 0 && (
        <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-slate-700" />
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-900">
                Priority Location Factor Intelligence (Rank #1 Candidate)
              </h3>
            </div>
            <RiskBadge
              level={prediction.locations[0].risk_level}
              score={prediction.locations[0].risk_score}
            />
          </div>

          <ShapFactorList
            factors={prediction.locations[0].top_factors || []}
            locationId={prediction.locations[0].location_id}
            riskScore={prediction.locations[0].risk_score}
          />
        </div>
      )}

      {/* Location Drawer */}
      <LocationDrawer
        location={selectedDrawerLocation}
        onClose={() => setSelectedDrawerLocation(null)}
        predictionWindowHours={caseItem.prediction_window_hours || 6}
      />

      {/* Record Post-Incident Outcome Modal */}
      {prediction && (
        <OutcomeModal
          isOpen={isOutcomeOpen}
          onClose={() => setIsOutcomeOpen(false)}
          caseId={caseItem.case_id}
          predictionId={prediction.prediction_id}
          candidateLocations={prediction.locations}
          onOutcomeSaved={() => {
            fetchCaseDetails();
          }}
        />
      )}

      {/* Tactical Patrol Dispatch Modal */}
      {prediction && (
        <PatrolDispatchModal
          isOpen={isDispatchOpen}
          onClose={() => setIsDispatchOpen(false)}
          caseId={caseItem.case_id}
          fraudAmount={caseItem.fraud_amount}
          fraudType={caseItem.fraud_type}
          topCandidates={prediction.locations}
          onDispatched={(unit) => {
            setActivePatrolUnit(unit);
            fetchCaseDetails();
          }}
        />
      )}
    </div>
  );
};
