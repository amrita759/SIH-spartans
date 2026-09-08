import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Cases } from './pages/Cases';
import { CaseDetails } from './pages/CaseDetails';
import { RiskMapPage } from './pages/RiskMapPage';
import { PredictionsPage } from './pages/PredictionsPage';
import { AlertsPage } from './pages/AlertsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ModelInfoModal } from './pages/ModelInfoModal';
import { api } from './services/api';
import { Case } from './types/case';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [activeAlertsCount, setActiveAlertsCount] = useState<number>(0);

  // Poll for active alerts count
  const refreshAlertsBadge = async () => {
    try {
      const alerts = await api.getAlerts('NEW');
      setActiveAlertsCount(alerts.length);
    } catch (err) {
      console.error('Failed to update alerts badge:', err);
    }
  };

  useEffect(() => {
    refreshAlertsBadge();
    const interval = setInterval(refreshAlertsBadge, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setCurrentTab('case-details');
  };

  const handleRunPrediction = async (caseItem: Case) => {
    await api.runPrediction(caseItem.case_id, 10);
    await refreshAlertsBadge();
    setSelectedCaseId(caseItem.case_id);
    setCurrentTab('case-details');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-slate-800 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeAlertsCount={activeAlertsCount}
        onAlertsClick={() => setCurrentTab('alerts')}
        modelVersion="v1.0.0"
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => {
            setCurrentTab(tab);
            if (tab !== 'case-details') {
              setSelectedCaseId(null);
            }
          }}
          alertsBadgeCount={activeAlertsCount}
        />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {currentTab === 'dashboard' && (
            <Dashboard
              onOpenCase={handleOpenCase}
              onNavigateTab={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'cases' && (
            <Cases
              onSelectCase={(c) => handleOpenCase(c.case_id)}
              onRunPrediction={handleRunPrediction}
            />
          )}

          {currentTab === 'case-details' && selectedCaseId && (
            <CaseDetails
              caseId={selectedCaseId}
              onBack={() => setCurrentTab('cases')}
            />
          )}

          {currentTab === 'map' && <RiskMapPage />}

          {currentTab === 'predictions' && (
            <PredictionsPage onOpenCase={handleOpenCase} />
          )}

          {currentTab === 'alerts' && (
            <AlertsPage
              onOpenCase={handleOpenCase}
              onRefreshAlerts={refreshAlertsBadge}
            />
          )}

          {currentTab === 'analytics' && <AnalyticsPage />}

          {currentTab === 'model-info' && <ModelInfoModal />}
        </main>
      </div>
    </div>
  );
}

export default App;
