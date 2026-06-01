import React from 'react';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuthContext } from './context/AuthContext';
import { LoadingOverlay } from './components/common/LoadingOverlay';
import { SidebarNavigation } from './components/navigation/SidebarNavigation';
import { AuthPage } from './pages/Auth/AuthPage';
import { AnalyticsPage } from './pages/Analytics/AnalyticsPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { QuestionsPage } from './pages/Questions/QuestionsPage';

const ROUTES = {
  HOME: '/home',
  QUESTIONS: '/questions',
  DASHBOARD: '/dashboard'
};

function normalizePath(pathname) {
  if (pathname === '/' || pathname === '') {
    return ROUTES.HOME;
  }

  if (pathname.startsWith(ROUTES.QUESTIONS)) {
    return ROUTES.QUESTIONS;
  }

  if (pathname.startsWith(ROUTES.DASHBOARD)) {
    return ROUTES.DASHBOARD;
  }

  return ROUTES.HOME;
}

function AppShell() {
  const { logout, user } = useAuthContext();
  const [currentPath, setCurrentPath] = React.useState(() => normalizePath(window.location.pathname));

  React.useEffect(() => {
    const onPopState = () => {
      setCurrentPath(normalizePath(window.location.pathname));
    };

    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = React.useCallback((path) => {
    const normalizedPath = normalizePath(path);
    if (normalizedPath === currentPath) {
      return;
    }
    window.history.pushState({}, '', normalizedPath);
    setCurrentPath(normalizedPath);
  }, [currentPath]);

  let page = <DashboardPage />;
  if (currentPath === ROUTES.QUESTIONS) {
    page = <QuestionsPage />;
  } else if (currentPath === ROUTES.DASHBOARD) {
    page = <AnalyticsPage />;
  }

  return (
    <div className="app-shell">
      <SidebarNavigation
        currentPath={currentPath}
        onLogout={logout}
        onNavigate={navigate}
        user={user}
      />
      <main className="app-shell-main">
        {page}
      </main>
    </div>
  );
}

function AppContent() {
  const { isAuthenticated, isAuthReady } = useAuthContext();

  if (!isAuthReady) {
    return <LoadingOverlay message="Restoring your session..." />;
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <AppProvider>
      <AppShell />
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
