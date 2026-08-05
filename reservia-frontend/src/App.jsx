import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ROLE_HOME } from './utils/roleRoutes';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SetupAdminPage from './pages/SetupAdminPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import CreateProviderPage from './pages/CreateProviderPage';
import SalasPage from './pages/SalasPage';
import EquiposPage from './pages/EquiposPage';
import ProviderDashboardPage from './pages/ProviderDashboardPage';
import ClientDashboardPage from './pages/ClientDashboardPage';
import ReservarSalasPage from './pages/ReservarSalasPage';
import ReservarSalaDetailPage from './pages/ReservarSalaDetailPage';
import ReservarEquiposPage from './pages/ReservarEquiposPage';
import ReservarEquipoDetailPage from './pages/ReservarEquipoDetailPage';
import ProveedoresPage from './pages/ProveedoresPage';
import AgendarCitaPage from './pages/AgendarCitaPage';
import MisReservasPage from './pages/MisReservasPage';

function RootRedirect() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={ROLE_HOME[user.role]} replace />;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/setup" element={<SetupAdminPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/providers/new"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <CreateProviderPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/salas"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <SalasPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/equipos"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <EquiposPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/provider"
            element={
              <ProtectedRoute allowedRoles={['provider']}>
                <ProviderDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/client"
            element={
              <ProtectedRoute allowedRoles={['client']}>
                <ClientDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recursos/salas"
            element={
              <ProtectedRoute>
                <ReservarSalasPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recursos/salas/:id/reservar"
            element={
              <ProtectedRoute>
                <ReservarSalaDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recursos/equipos"
            element={
              <ProtectedRoute>
                <ReservarEquiposPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recursos/equipos/:id/reservar"
            element={
              <ProtectedRoute>
                <ReservarEquipoDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/proveedores"
            element={
              <ProtectedRoute>
                <ProveedoresPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/proveedores/:id/agendar"
            element={
              <ProtectedRoute>
                <AgendarCitaPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mis-reservas"
            element={
              <ProtectedRoute>
                <MisReservasPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;