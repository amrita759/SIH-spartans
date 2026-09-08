import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { RiskBadge } from '../common/RiskBadge';
import { Layers } from 'lucide-react';

export interface MapPoint {
  location_id: string;
  location_name?: string;
  location_type?: string;
  bank?: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: string;
  rank?: number;
  district?: string;
  state?: string;
}

interface RiskMapProps {
  locations: MapPoint[];
  selectedLocationId?: string | null;
  onSelectLocation?: (location: MapPoint) => void;
  center?: [number, number];
  zoom?: number;
  height?: string;
}

// Controller to smoothly pan & zoom map when coordinates change
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2 });
  }, [center, zoom, map]);
  return null;
};

// Create custom crisp SVG markers for risk bands
const createRiskIcon = (level: string, rank?: number, isSelected: boolean = false) => {
  const norm = (level || 'LOW').toUpperCase();
  let color = '#2563eb'; // LOW blue

  if (norm === 'CRITICAL') {
    color = '#dc2626'; // Red
  } else if (norm === 'HIGH') {
    color = '#ea580c'; // Orange
  } else if (norm === 'MEDIUM') {
    color = '#d97706'; // Amber
  }

  const border = isSelected ? '#0f172a' : '#ffffff';
  const size = isSelected ? 30 : 24;

  const html = `
    <div class="custom-risk-marker" style="width: ${size}px; height: ${size}px;">
      <div style="
        background-color: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid ${border};
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: ui-monospace, monospace;
        font-size: ${size > 26 ? '11px' : '10px'};
        font-weight: 700;
      ">
        ${rank !== undefined ? rank : ''}
      </div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-risk-marker',
    html: html,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
};

export const RiskMap: React.FC<RiskMapProps> = ({
  locations,
  selectedLocationId,
  onSelectLocation,
  center = [19.0760, 72.8777], // Default Mumbai
  zoom = 12,
  height = '500px'
}) => {
  const [basemapStyle, setBasemapStyle] = useState<'carto-light' | 'osm-daylight' | 'carto-dark'>('carto-light');

  const cartoApiKey =
    import.meta.env.VITE_CARTO_API_KEY || 'cb1_31yj_1_1eadb8a3d9cfa35d572a63b6';

  const tileConfig = useMemo(() => {
    if (basemapStyle === 'osm-daylight') {
      return {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        className: ''
      };
    }
    if (basemapStyle === 'carto-dark') {
      return {
        url: `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png?key=${cartoApiKey}`,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        className: ''
      };
    }
    // Default: CARTO Positron Light with ?key=
    return {
      url: `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png?key=${cartoApiKey}`,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      className: ''
    };
  }, [basemapStyle, cartoApiKey]);

  // Dynamically recalculate center if locations exist
  const effectiveCenter = useMemo<[number, number]>(() => {
    if (locations.length > 0) {
      const valid = locations.filter(
        (l) => l.latitude && l.longitude && !isNaN(l.latitude) && !isNaN(l.longitude)
      );
      if (valid.length > 0) {
        return [valid[0].latitude, valid[0].longitude];
      }
    }
    return center;
  }, [locations, center]);

  return (
    <div className="relative isolate z-0 w-full rounded-md overflow-hidden border border-slate-200 bg-white shadow-xs" style={{ height }}>
      {/* Risk Legend Overlay */}
      <div className="absolute top-3 right-3 z-[1000] bg-white/95 backdrop-blur-xs border border-slate-200 rounded-md p-2.5 text-xs text-slate-700 shadow-sm space-y-1 pointer-events-auto">
        <p className="font-bold text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-1">
          OPERATIONAL RISK BANDS
        </p>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-600" />
          <span className="font-mono text-[11px] text-slate-800">CRITICAL (&ge; 80.0)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-600" />
          <span className="font-mono text-[11px] text-slate-800">HIGH (60 - 79.9)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-600" />
          <span className="font-mono text-[11px] text-slate-800">MEDIUM (30 - 59.9)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
          <span className="font-mono text-[11px] text-slate-800">LOW (&lt; 30.0)</span>
        </div>
      </div>

      {/* Basemap Style Switcher */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs border border-slate-200 rounded-md p-1 flex items-center gap-1 text-[11px] shadow-sm pointer-events-auto">
        <div className="flex items-center gap-1 text-slate-500 px-1.5 py-0.5">
          <Layers className="w-3.5 h-3.5 text-slate-600" />
          <span className="hidden sm:inline font-semibold">Map:</span>
        </div>
        <button
          onClick={() => setBasemapStyle('carto-light')}
          className={`px-2 py-0.5 rounded font-medium transition cursor-pointer ${
            basemapStyle === 'carto-light'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          CARTO Daylight
        </button>
        <button
          onClick={() => setBasemapStyle('osm-daylight')}
          className={`px-2 py-0.5 rounded font-medium transition cursor-pointer ${
            basemapStyle === 'osm-daylight'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          OSM (Keyless)
        </button>
        <button
          onClick={() => setBasemapStyle('carto-dark')}
          className={`px-2 py-0.5 rounded font-medium transition cursor-pointer ${
            basemapStyle === 'carto-dark'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Dark Matter
        </button>
      </div>

      <MapContainer
        center={effectiveCenter}
        zoom={zoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <MapController center={effectiveCenter} zoom={zoom} />
        <TileLayer
          key={basemapStyle}
          attribution={tileConfig.attribution}
          url={tileConfig.url}
          className={tileConfig.className}
        />

        {locations.map((loc) => {
          const isSelected = selectedLocationId === loc.location_id;
          return (
            <Marker
              key={loc.location_id}
              position={[loc.latitude, loc.longitude]}
              icon={createRiskIcon(loc.risk_level, loc.rank, isSelected)}
              eventHandlers={{
                click: () => {
                  if (onSelectLocation) onSelectLocation(loc);
                }
              }}
            >
              <Popup>
                <div className="p-1 min-w-[200px] text-xs">
                  <div className="flex items-center justify-between gap-2 mb-1.5 pb-1 border-b border-slate-100">
                    <span className="font-bold text-slate-900 font-mono">
                      #{loc.rank || '-'} {loc.location_id}
                    </span>
                    <RiskBadge level={loc.risk_level} score={loc.risk_score} />
                  </div>
                  <p className="text-slate-900 font-semibold">{loc.bank || 'Banking Terminal'}</p>
                  <p className="text-slate-600 text-[11px] mt-0.5">
                    Type: <span className="font-mono font-medium text-slate-800">{loc.location_type || 'ATM'}</span>
                  </p>
                  <p className="text-slate-600 text-[11px]">
                    {loc.district}, {loc.state}
                  </p>
                  <div className="mt-2 pt-1 border-t border-slate-100 text-[10px] text-slate-500 font-mono">
                    Coord: ({loc.latitude.toFixed(4)}, {loc.longitude.toFixed(4)})
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
