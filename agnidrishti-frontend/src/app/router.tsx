import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppShell } from './AppShell'
import AlertsPage from '../pages/AlertsPage'
import AnomalyPage from '../pages/AnomalyPage'
import AssessmentPage from '../pages/AssessmentPage'
import DashboardPage from '../pages/DashboardPage'
import DataLayersPage from '../pages/DataLayersPage'
import InvestigationPage from '../pages/InvestigationPage'
import LoginPage from '../pages/LoginPage'
import ReportsPage from '../pages/ReportsPage'
import SearchPage from '../pages/SearchPage'
import SystemPage from '../pages/SystemPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'investigation/:sourceId?', element: <InvestigationPage /> },
      { path: 'assessment', element: <AssessmentPage /> },
      { path: 'anomaly', element: <AnomalyPage /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'alerts', element: <AlertsPage /> },
      { path: 'data-layers', element: <DataLayersPage /> },
      { path: 'system', element: <SystemPage /> },
      { path: 'login', element: <LoginPage /> },
    ],
  },
])
