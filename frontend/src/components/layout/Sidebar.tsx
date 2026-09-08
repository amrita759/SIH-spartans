import React from 'react';
import {
  LayoutDashboard,
  FolderOpen,
  Target,
  MapPin,
  Bell,
  BarChart3,
  Cpu,
  ShieldCheck
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  alertsBadgeCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  alertsBadgeCount = 0
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Command Center', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'cases', label: 'Active Complaints', icon: <FolderOpen className="w-4 h-4" /> },
    { id: 'map', label: 'GIS Risk Map', icon: <MapPin className="w-4 h-4" /> },
    { id: 'predictions', label: 'Prediction Logs', icon: <Target className="w-4 h-4" /> },
    {
      id: 'alerts',
      label: 'Priority Alerts',
      icon: <Bell className="w-4 h-4" />,
      badge: alertsBadgeCount > 0 ? alertsBadgeCount : null
    },
    { id: 'analytics', label: 'Cyber Intelligence', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'model-info', label: 'Model Specifications', icon: <Cpu className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-57px)] p-3 flex flex-col justify-between hidden md:flex">
      <div className="space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          OPERATIONAL LEDGER
        </div>
        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs font-semibold tracking-normal transition cursor-pointer ${
                isActive
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className={isActive ? 'text-white' : 'text-slate-400'}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              {item.badge !== null && item.badge !== undefined && (
                <span className="px-1.5 py-0.2 text-[10px] font-bold bg-red-600 text-white rounded">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Grounding & Ethics Footer */}
      <div className="p-3 rounded bg-slate-50 border border-slate-200 text-slate-600 space-y-1">
        <div className="flex items-center gap-1.5 text-slate-900 font-semibold text-xs">
          <ShieldCheck className="w-3.5 h-3.5 text-slate-700" />
          <span>Zero Data Leakage Boundary</span>
        </div>
        <p className="text-[10px] text-slate-500 leading-normal">
          Strict chronological boundaries enforced at time $T$. Model attributions reflect validated predictive risk factors.
        </p>
      </div>
    </aside>
  );
};
