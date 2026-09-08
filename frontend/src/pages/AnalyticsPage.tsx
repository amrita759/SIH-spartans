import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AnalyticsSummary } from '../types/analytics';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  BarChart3,
  Cpu,
  ShieldCheck,
  Building2,
  MapPin,
  Clock,
  Layers,
  Award,
  RefreshCw
} from 'lucide-react';

const RISK_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#d97706',
  LOW: '#2563eb'
};

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (isLoading) {
    return (
      <div className="p-16 text-center text-slate-500 bg-white rounded border border-slate-200 shadow-xs animate-pulse">
        Aggregating system-wide cybercrime analytics and validated model performance...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-12 text-center text-slate-500 bg-white rounded border border-slate-200">
        Analytics telemetry unavailable.
      </div>
    );
  }

  // Format Risk Distribution for Bar Chart
  const riskPieData = Object.entries(data.risk_distribution).map(([level, count]) => ({
    name: level,
    value: count
  }));

  const tooltipStyle = {
    backgroundColor: '#ffffff',
    borderColor: '#cbd5e1',
    borderRadius: '4px',
    boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
    color: '#0f172a',
    fontSize: '12px'
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h1 className="text-base font-bold text-slate-900 tracking-tight">
            Cybercrime Predictive Analytics &amp; Model Benchmarks
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational risk distributions, banking network exposure, and out-of-time test set evaluation.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Model Performance Validation Benchmarks (Section 21 & 30) */}
      <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-slate-900">
            <Award className="w-4 h-4 text-blue-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Validated Out-of-Time Test Set Benchmarks (Held-Out Evaluation)
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-500">
            Evaluated on 459 Held-Out Cases (2023 H2 - 2024) • 11,475 Candidates
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">Hit@10</p>
            <p className="text-lg font-mono font-bold text-blue-700 mt-0.5">
              {(data.model_performance.hit_at_10 * 100).toFixed(1)}%
            </p>
            <p className="text-[9px] text-slate-400">Top-10 Recall</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">Hit@5</p>
            <p className="text-lg font-mono font-bold text-blue-600 mt-0.5">
              {(data.model_performance.hit_at_5 * 100).toFixed(1)}%
            </p>
            <p className="text-[9px] text-slate-400">Top-5 Recall</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">Hit@3</p>
            <p className="text-lg font-mono font-bold text-slate-800 mt-0.5">
              {(data.model_performance.hit_at_3 * 100).toFixed(1)}%
            </p>
            <p className="text-[9px] text-slate-400">Top-3 Recall</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">Hit@1</p>
            <p className="text-lg font-mono font-bold text-slate-800 mt-0.5">
              {(data.model_performance.hit_at_1 * 100).toFixed(1)}%
            </p>
            <p className="text-[9px] text-slate-400">Rank #1 Precision</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">MRR</p>
            <p className="text-lg font-mono font-bold text-purple-700 mt-0.5">
              {data.model_performance.mrr.toFixed(4)}
            </p>
            <p className="text-[9px] text-slate-400">Reciprocal Rank</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">PR-AUC</p>
            <p className="text-lg font-mono font-bold text-emerald-700 mt-0.5">
              {data.model_performance.pr_auc.toFixed(4)}
            </p>
            <p className="text-[9px] text-slate-400">Precision-Recall AUC</p>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-center">
            <p className="text-[10px] uppercase font-bold text-slate-500">Lead Time</p>
            <p className="text-lg font-mono font-bold text-amber-700 mt-0.5">
              {data.kpis.mean_lead_time_hours}h
            </p>
            <p className="text-[9px] text-slate-400">Mean T to Cashout</p>
          </div>
        </div>

        <div className="p-2.5 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-600 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <span>
            <strong>Statistical Protocol:</strong> Benchmarks are derived from historical out-of-time test partitions strictly prior to withdrawal timestamps.
          </span>
          <span className="font-mono text-slate-700 font-semibold shrink-0">
            Engine: LightGBM v1.0.0
          </span>
        </div>
      </div>

      {/* Visual Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Risk Distribution Breakdown */}
        <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Operational Risk Distribution (CRITICAL / HIGH / MED / LOW)
            </h3>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskPieData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                  {riskPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#2563eb'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Predictions by State */}
        <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Geographic Cash-Out Hotspots by State
            </h3>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.predictions_by_state.slice(0, 6)}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 40, bottom: 0 }}
              >
                <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                <YAxis dataKey="state" type="category" stroke="#94a3b8" fontSize={10} width={80} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" fill="#2563eb" radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Average Risk by Bank */}
        <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Vulnerability Index by Banking Network (Avg Risk Score)
            </h3>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.risk_by_bank.slice(0, 5)}
                margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
              >
                <XAxis dataKey="bank" stroke="#94a3b8" fontSize={9} interval={0} angle={-15} textAnchor="end" />
                <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="avg_risk" fill="#ea580c" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Terminal Type (ATM vs CRM) */}
        <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Disbursement Point Breakdown (ATM vs CRM)
            </h3>
          </div>

          <div className="h-60 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.location_type_distribution}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }: { name?: string; percent?: number }) =>
                    `${name || 'ATM'}: ${((percent || 0) * 100).toFixed(0)}%`
                  }
                >
                  {data.location_type_distribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.type === 'CRM' ? '#7c3aed' : '#0284c7'}
                    />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
