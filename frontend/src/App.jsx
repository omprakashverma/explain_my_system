import React from 'react';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuthContext } from './context/AuthContext';
import { LoadingOverlay } from './components/common/LoadingOverlay';
import { AuthPage } from './pages/Auth/AuthPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';

function AppContent() {
  const { authBusy, isAuthenticated, isAuthReady } = useAuthContext();

  if (!isAuthReady) {
    return <LoadingOverlay message="Restoring your session..." />;
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <AppProvider>
      <DashboardPage />
    </AppProvider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
