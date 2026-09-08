import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';
import { RiskLocation } from '../types/location';
import { RiskMap, MapPoint } from '../components/map/RiskMap';
import { LocationDrawer, DrawerLocationData } from '../components/map/LocationDrawer';
import {
  MapPin,
  Filter,
  RefreshCw,
  SlidersHorizontal,
  Building2
} from 'lucide-react';

export const RiskMapPage: React.FC = () => {
  const [locations, setLocations] = useState<RiskLocation[]>([]);
  const [selectedDrawerLocation, setSelectedDrawerLocation] = useState<DrawerLocationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [bankFilter, setBankFilter] = useState('');

  const fetchRiskLocations = async () => {
    setIsLoading(true);
    try {
      const res = await api.getRiskLocations({ limit: 100 });
      setLocations(res.locations || []);
    } catch (err) {
      console.error('Failed to load risk locations for GIS:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskLocations();
  }, []);

  // Filtered map locations
  const filteredLocations = useMemo(() => {
    return locations.filter((loc) => {
      const matchesRisk = riskFilter === 'ALL' || loc.risk_level === riskFilter;
      const matchesType = typeFilter === 'ALL' || loc.location_type === typeFilter;
      const matchesState = stateFilter === 'ALL' || loc.state === stateFilter;
      const matchesBank =
        !bankFilter || loc.bank.toLowerCase().includes(bankFilter.toLowerCase());

      return matchesRisk && matchesType && matchesState && matchesBank;
    });
  }, [locations, riskFilter, typeFilter, stateFilter, bankFilter]);

  // Unique states
  const availableStates = useMemo(() => {
    const s = Array.from(new Set(locations.map((l) => l.state).filter(Boolean)));
    return s.sort();
  }, [locations]);

  // Transform to MapPoint
  const mapPoints: MapPoint[] = useMemo(() => {
    return filteredLocations.map((l) => ({
      location_id: l.location_id,
      bank: l.bank,
      location_type: l.location_type,
      latitude: l.latitude,
      longitude: l.longitude,
      risk_score: l.risk_score,
      risk_level: l.risk_level,
      rank: l.rank,
      district: l.district,
      state: l.state
    }));
  }, [filteredLocations]);

  const handleSelectLocation = (loc: MapPoint) => {
    setSelectedDrawerLocation({
      location_id: loc.location_id,
      bank_name: loc.bank,
      location_type: loc.location_type,
      latitude: loc.latitude,
      longitude: loc.longitude,
      district: loc.district,
      state: loc.state,
      risk_score: loc.risk_score,
      risk_level: loc.risk_level,
      rank: loc.rank
    });
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h1 className="text-base font-bold text-slate-900 tracking-tight">
            GIS Risk Surveillance Center
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Geospatial intelligence overlay displaying predicted cybercrime cash-out vulnerabilities across India.
          </p>
        </div>

        <button
          onClick={fetchRiskLocations}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-300 shadow-xs transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-slate-600' : 'text-slate-500'}`} />
          <span>Refresh Surveillance GIS</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="p-3 rounded border border-slate-200 bg-white shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Risk Band Filter */}
          <div className="flex items-center gap-1.5 text-slate-600">
            <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium">Risk Band:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-slate-800 text-xs focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              <option value="ALL">All Risk Bands</option>
              <option value="CRITICAL">CRITICAL (&ge; 80)</option>
              <option value="HIGH">HIGH (60 - 79)</option>
              <option value="MEDIUM">MEDIUM (30 - 59)</option>
              <option value="LOW">LOW (&lt; 30)</option>
            </select>
          </div>

          {/* Terminal Type (ATM vs CRM) */}
          <div className="flex items-center gap-1.5 text-slate-600">
            <span className="font-medium">Terminal Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-slate-800 text-xs focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              <option value="ALL">ATM + CRM</option>
              <option value="ATM">ATM (Cash Dispenser)</option>
              <option value="CRM">CRM (Cash Recycler)</option>
            </select>
          </div>

          {/* State Filter */}
          <div className="flex items-center gap-1.5 text-slate-600">
            <span className="font-medium">State:</span>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-slate-800 text-xs focus:outline-none focus:ring-1 focus:ring-slate-900"
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

        {/* Bank Name Search */}
        <div className="flex items-center gap-1.5 text-slate-600">
          <Building2 className="w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={bankFilter}
            onChange={(e) => setBankFilter(e.target.value)}
            placeholder="Search bank name..."
            className="px-2.5 py-1 bg-slate-50 border border-slate-300 rounded text-slate-800 placeholder-slate-400 text-xs focus:outline-none focus:ring-1 focus:ring-slate-900"
          />
        </div>
      </div>

      {/* Map View */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            Visualizing <strong className="text-slate-900 font-mono">{filteredLocations.length}</strong> active risk terminals
          </span>
          <span className="font-mono text-[11px] text-slate-400">
            Click any circular marker to open investigative dossier
          </span>
        </div>

        <RiskMap
          locations={mapPoints}
          selectedLocationId={selectedDrawerLocation?.location_id}
          onSelectLocation={handleSelectLocation}
          height="620px"
        />
      </div>

      {/* Location Drawer */}
      <LocationDrawer
        location={selectedDrawerLocation}
        onClose={() => setSelectedDrawerLocation(null)}
      />
    </div>
  );
};
