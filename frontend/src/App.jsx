import React from 'react';
import { AppProvider } from './context/AppContext';
import { DashboardPage } from './pages/Dashboard/DashboardPage';

export default function App() {
  return (
    <AppProvider>
      <DashboardPage />
    </AppProvider>
  );
}
