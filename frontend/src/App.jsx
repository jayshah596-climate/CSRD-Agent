import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import useAuthStore from "./store/authStore";

// Auth pages
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";

// Layout
import AppLayout from "./components/Layout/AppLayout";

// Dashboard
import Dashboard from "./pages/Dashboard";

// Projects
import ProjectsList from "./pages/Projects/ProjectsList";
import ProjectDetail from "./pages/Projects/ProjectDetail";
import NewProject from "./pages/Projects/NewProject";

// Data Collection
import DataCollection from "./pages/DataCollection";

// Materiality
import MaterialityAssessment from "./pages/Materiality";

// Emissions
import EmissionsPage from "./pages/Emissions";

// IRO
import IROPage from "./pages/IRO";

// Scenarios
import ScenariosPage from "./pages/Scenarios";

// Reports
import ReportsPage from "./pages/Reports";

// Company Settings
import CompanySettings from "./pages/Settings/CompanySettings";


function PrivateRoute({ children }) {
  const token = useAuthStore((s) => s.token);
  return token ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const token = useAuthStore((s) => s.token);
  return !token ? children : <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={<PublicRoute><Login /></PublicRoute>}
        />
        <Route
          path="/register"
          element={<PublicRoute><Register /></PublicRoute>}
        />

        {/* Private routes */}
        <Route
          path="/"
          element={<PrivateRoute><AppLayout /></PrivateRoute>}
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="projects" element={<ProjectsList />} />
          <Route path="projects/new" element={<NewProject />} />
          <Route path="projects/:projectId" element={<ProjectDetail />} />
          <Route path="projects/:projectId/data" element={<DataCollection />} />
          <Route path="projects/:projectId/materiality" element={<MaterialityAssessment />} />
          <Route path="projects/:projectId/emissions" element={<EmissionsPage />} />
          <Route path="projects/:projectId/iro" element={<IROPage />} />
          <Route path="projects/:projectId/scenarios" element={<ScenariosPage />} />
          <Route path="projects/:projectId/reports" element={<ReportsPage />} />
          <Route path="settings/company" element={<CompanySettings />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
