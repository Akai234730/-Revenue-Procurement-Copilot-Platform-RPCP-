import { Navigate, Route, Routes } from 'react-router-dom';

import { getAccessToken } from './lib/api';
import { useAuth } from './auth/AuthContext';
import { AppShell } from './shell/AppShell';
import { DashboardPage } from './views/DashboardPage';
import { KnowledgePage } from './views/KnowledgePage';
import { LeadsPage } from './views/LeadsPage';
import { LoginPage } from './views/LoginPage';
import { OperationsPage } from './views/OperationsPage';
import { ProcurementPage } from './views/ProcurementPage';
import { ProposalsPage } from './views/ProposalsPage';
import { SettingsPage } from './views/SettingsPage';
import { SuppliersPage } from './views/SuppliersPage';

export function App() {
  const { isAuthenticated, bootstraping } = useAuth();
  const hasToken = Boolean(getAccessToken());

  if (bootstraping && hasToken) {
    return <div className="loading-screen">正在恢复登录状态...</div>;
  }

  if (bootstraping) {
    return <div className="loading-screen">正在初始化平台...</div>;
  }

  if (!isAuthenticated && !hasToken) {
    return <LoginPage />;
  }

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/leads" element={<LeadsPage />} />
        <Route path="/proposals" element={<ProposalsPage />} />
        <Route path="/procurement" element={<ProcurementPage />} />
        <Route path="/suppliers" element={<SuppliersPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppShell>
  );
}
