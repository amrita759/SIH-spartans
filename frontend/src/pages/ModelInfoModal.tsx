import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ModelInfo } from '../types/prediction';
import { Cpu, ShieldCheck, Database, GitBranch, Layers, CheckCircle2 } from 'lucide-react';

export const ModelInfoModal: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const info = await api.getModelInfo();
        setModelInfo(info);
      } catch (err) {
        console.error('Failed to load model specifications:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchInfo();
  }, []);

  if (isLoading) {
    return (
      <div className="p-16 text-center text-slate-500 bg-white rounded border border-slate-200 shadow-xs animate-pulse">
        Loading ML model architecture and feature contract specifications...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="pb-3 border-b border-slate-200">
        <h1 className="text-base font-bold text-slate-900 tracking-tight">
          ML Architecture &amp; Integration Specifications
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          SIH26184 Production Model Contract • Single Source of Truth for Predictive Intelligence.
        </p>
      </div>

      {/* Primary Spec Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="p-3.5 rounded border border-slate-200 bg-white shadow-xs space-y-1">
          <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold uppercase">
            <Cpu className="w-4 h-4 text-slate-700" />
            <span>Model Classifier</span>
          </div>
          <p className="text-base font-bold font-mono text-slate-900 mt-0.5">LightGBM GBDT</p>
          <p className="text-[11px] text-slate-500">Early stopping on time-split validation</p>
        </div>

        <div className="p-3.5 rounded border border-slate-200 bg-white shadow-xs space-y-1">
          <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold uppercase">
            <GitBranch className="w-4 h-4 text-slate-700" />
            <span>Model Version</span>
          </div>
          <p className="text-base font-bold font-mono text-emerald-700 mt-0.5">{modelInfo?.model_version || 'v1.0.0'}</p>
          <p className="text-[11px] text-slate-500">Trained on 550k Indian transactions</p>
        </div>

        <div className="p-3.5 rounded border border-slate-200 bg-white shadow-xs space-y-1">
          <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold uppercase">
            <Layers className="w-4 h-4 text-slate-700" />
            <span>Feature Count</span>
          </div>
          <p className="text-base font-bold font-mono text-purple-700 mt-0.5">
            {modelInfo?.total_features || 25} Features
          </p>
          <p className="text-[11px] text-slate-500">22 Numerical + 3 Categorical</p>
        </div>

        <div className="p-3.5 rounded border border-slate-200 bg-white shadow-xs space-y-1">
          <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold uppercase">
            <Database className="w-4 h-4 text-slate-700" />
            <span>Surveillance Window</span>
          </div>
          <p className="text-base font-bold font-mono text-amber-700 mt-0.5">Next 6 Hours</p>
          <p className="text-[11px] text-slate-500">Mean Lead Time: 2.63h</p>
        </div>
      </div>

      {/* 25 Feature Contract Schema */}
      <div className="p-4 rounded border border-slate-200 bg-white shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-700" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Exact 25-Feature Schema &amp; Zero-Leakage Contract
            </h2>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 text-[11px] font-mono font-bold border border-emerald-200 w-fit">
            STRICT ZERO-LEAKAGE BOUNDARY T
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {modelInfo?.feature_names.map((feat, idx) => (
            <div
              key={feat}
              className="p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-slate-400 text-[11px] w-5">#{idx + 1}</span>
                <span className="font-mono text-slate-800 text-xs">{feat}</span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                {['fraud_type', 'last_channel', 'population_group'].includes(feat)
                  ? 'Categorical'
                  : 'Numerical'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Verification Principles Banner */}
      <div className="p-4 rounded border border-slate-200 bg-slate-50 text-xs text-slate-600 space-y-2">
        <h3 className="font-bold text-slate-900 uppercase tracking-wide text-xs">
          Operational Engineering Guarantees
        </h3>
        <ul className="list-disc pl-5 space-y-1 text-slate-700 text-[11px] leading-relaxed">
          <li>
            <strong>Single Source of Truth:</strong> The backend wraps and reuses the fitted LightGBM and TreeSHAP artifacts once at application launch via the <code className="bg-slate-200 px-1 py-0.5 rounded text-slate-800">MLModelAdapter</code> singleton.
          </li>
          <li>
            <strong>Deterministic Candidate Generation:</strong> Combines spatial proximity (&le; 20 km) with historical district hotspots across 137,444 Indian ATMs and CRMs.
          </li>
          <li>
            <strong>Continuous Risk Score:</strong> Raw probabilities are calibrated into continuous 0–100 risk scores (5.0 to 98.0) with configurable operational risk levels (CRITICAL, HIGH, MEDIUM, LOW).
          </li>
          <li>
            <strong>Zero Future Knowledge:</strong> All features are computed strictly using data available up to time <span className="font-mono font-semibold">T</span>. Post-<span className="font-mono font-semibold">T</span> activity and ground truth outcomes never enter prediction features.
          </li>
        </ul>
      </div>
    </div>
  );
};
