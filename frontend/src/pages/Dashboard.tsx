import React, { useEffect, useState, useMemo } from 'react';
import { api } from '../services/api';
import { Case } from '../types/case';
import { RankedLocation, PredictionResult } from '../types/prediction';
import { Alert } from '../types/alert';
import { AnalyticsSummary } from '../types/analytics';
import { MetricCard } from '../components/cards/MetricCard';
import { RiskBadge } from '../components/common/RiskBadge';
import { RiskMap, MapPoint } from '../components/map/RiskMap';
import { LocationTable } from '../components/tables/LocationTable';
import { LocationDrawer, DrawerLocationData } from '../components/map/LocationDrawer';
import {
  FolderOpen,
  AlertTriangle,
  Target,
  Clock,
  ShieldCheck,
  ChevronRight,
  TrendingUp,
  Cpu,
  RefreshCw
} from 'lucide-react';

interface DashboardProps {
  onOpenCase: (caseId: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onOpenCase, onNavigateTab }) => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [latestPrediction, setLatestPrediction] = useState<PredictionResult | null>(null);
  const [selectedDrawerLocation, setSelectedDrawerLocation] = useState<DrawerLocationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [analyticsData, casesData, alertsData] = await Promise.all([
        api.getAnalytics(),
        api.getCases(),
        api.getAlerts()
      ]);
      setAnalytics(analyticsData);
      setCases(casesData);
      setAlerts(alertsData);

      // If any case has a latest_prediction_id, load it
      const predictedCase = casesData.find((c) => c.latest_prediction_id);
      if (predictedCase?.latest_prediction_id) {
        const pred = await api.getPrediction(predictedCase.latest_prediction_id);
        setLatestPrediction(pred);
      } else if (casesData.length > 0) {
        // Run initial prediction for CASE-001 if no prediction exists yet
        const defaultCase = casesData[0];
        const res = await api.runPrediction(defaultCase.case_id, 10);
        setLatestPrediction(res);
        // Refresh cases to show updated status
        const updatedCases = await api.getCases();
        setCases(updatedCases);
      }
    } catch (err) {
      console.error('Failed to load dashboard telemetry:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Prepare map points from the latest prediction
  const mapPoints: MapPoint[] = useMemo(() => {
    if (!latestPrediction || !latestPrediction.locations) return [];
    return latestPrediction.locations.map((loc) => ({
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
  }, [latestPrediction]);

  const handleSelectLocation = (loc: any) => {
    // Look up full location details including SHAP factors
    const fullLoc = latestPrediction?.locations.find((l) => l.location_id === loc.location_id);
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

  const highRiskPredictionsCount = useMemo(() => {
    return alerts.filter((a) => a.risk_level === 'CRITICAL' || a.risk_level === 'HIGH').length;
  }, [alerts]);

  return (
    <div className="space-y-6">
      {/* Top Header & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
            Command Center Overview
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational Cybercrime Cash-Out Surveillance • Real-Time LightGBM & TreeSHAP Scoring
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchDashboardData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-slate-600' : ''}`} />
            <span>Refresh Telemetry</span>
          </button>
          <button
            onClick={() => onNavigateTab('cases')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
          >
            <FolderOpen className="w-3.5 h-3.5" />
            <span>Investigate Cases</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <MetricCard
          title="Active Cases"
          value={analytics?.kpis.active_cases ?? cases.length}
          subtitle="Under active surveillance"
          variant="cyan"
          icon={<FolderOpen className="w-4 h-4" />}
        />
        <MetricCard
          title="High Risk Cases"
          value={highRiskPredictionsCount}
          subtitle="Risk &ge; 60.0"
          variant="red"
          icon={<AlertTriangle className="w-4 h-4" />}
        />
        <MetricCard
          title="Predictions Generated"
          value={analytics?.kpis.total_predictions ?? (latestPrediction ? 1 : 0)}
          subtitle="Chronological inference"
          variant="purple"
          icon={<Target className="w-4 h-4" />}
        />
        <MetricCard
          title="Operational Lead Time"
          value="2.63h"
          subtitle="Mean lead time to cash-out"
          variant="emerald"
          icon={<Clock className="w-4 h-4" />}
        />
        <MetricCard
          title="Priority Alerts"
          value={alerts.filter((a) => a.status === 'NEW').length}
          subtitle={`${alerts.length} total dispatched`}
          variant="amber"
          icon={<AlertTriangle className="w-4 h-4" />}
        />
      </div>

      {/* Main Content: Map & Intelligence Feeds */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: GIS Map */}
        <div className="lg:col-span-2 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-800" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Spatial Cash-Out Risk Visualization (Candidate ATMs / CRMs)
              </h2>
            </div>
            {latestPrediction && (
              <span className="text-xs font-mono text-slate-600">
                Active Case: <span className="text-slate-900 font-bold">{latestPrediction.case_id}</span>
              </span>
            )}
          </div>

          <RiskMap
            locations={mapPoints}
            selectedLocationId={selectedDrawerLocation?.location_id}
            onSelectLocation={handleSelectLocation}
            height="460px"
          />
        </div>

        {/* Right: Recent High-Risk Predictions & Active Alerts */}
        <div className="space-y-4">
          {/* Active Alerts Panel */}
          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <h3 className="text-xs font-bold uppercase tracking-wide text-slate-900">
                  Priority Alerts Queue
                </h3>
              </div>
              <button
                onClick={() => onNavigateTab('alerts')}
                className="text-[11px] text-slate-600 hover:text-slate-900 font-medium hover:underline flex items-center gap-0.5 cursor-pointer"
              >
                <span>View All</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            {alerts.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No active alerts generated.</p>
            ) : (
              <div className="space-y-2 max-h-[190px] overflow-y-auto pr-1">
                {alerts.slice(0, 3).map((a) => (
                  <div
                    key={a.alert_id}
                    onClick={() => onOpenCase(a.case_id)}
                    className="p-2.5 rounded bg-slate-50 border border-slate-200 hover:border-slate-300 hover:bg-slate-100/60 transition cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-slate-900">{a.case_id}</span>
                      <RiskBadge level={a.risk_level} score={a.risk_score} />
                    </div>
                    <p className="text-[11px] text-slate-600 mt-1 truncate">
                      Terminal: {a.location_id} ({a.bank_name || 'Bank'})
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Model Operational Intelligence Card */}
          <div className="p-4 rounded-md bg-white border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center gap-2 text-slate-900">
              <Cpu className="w-4 h-4 text-slate-700" />
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-900">
                Inference Specification
              </h3>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Core Engine:</span>
                <span className="font-mono text-slate-900 font-bold">LightGBM GBDT (v1.0.0)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Spatial Index:</span>
                <span className="font-mono text-slate-900 font-bold">137,444 ATMs/CRMs</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Explainability:</span>
                <span className="font-mono text-slate-900 font-bold">TreeSHAP Signed Factors</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Benchmark Hit@10:</span>
                <span className="font-mono text-emerald-700 font-bold">43.8% (Out-of-Time Test)</span>
              </div>
            </div>
            <button
              onClick={() => onNavigateTab('model-info')}
              className="w-full mt-2 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer"
            >
              Inspect Model Artifacts & Contracts
            </button>
          </div>
        </div>
      </div>

      {/* Bottom: Top Predicted Locations Table */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-slate-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Top-10 Predicted Cash-Out Terminals for Active Investigation
            </h2>
          </div>
          {latestPrediction && (
            <span className="text-xs font-mono text-slate-500">
              Scored {latestPrediction.total_candidates_scored} candidate locations in 20km radius
            </span>
          )}
        </div>

        <LocationTable
          locations={latestPrediction?.locations || []}
          onSelectLocation={handleSelectLocation}
          selectedLocationId={selectedDrawerLocation?.location_id}
        />
      </div>

      {/* Detail Inspection Drawer */}
      <LocationDrawer
        location={selectedDrawerLocation}
        onClose={() => setSelectedDrawerLocation(null)}
        predictionWindowHours={latestPrediction?.prediction_window_hours || 6}
      />
    </div>
  );
};
