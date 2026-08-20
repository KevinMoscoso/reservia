import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

function AdminDashboardPage() {
  const { user } = useAuth();

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">
        Bienvenido, {user?.full_name}
      </h1>
      <div className="flex flex-col gap-2">
        <Link to="/admin/providers/new" className="text-blue-600 hover:underline">
          Crear nuevo proveedor
        </Link>
        <Link to="/admin/salas" className="text-blue-600 hover:underline">
          Gestionar salas
        </Link>
        <Link to="/admin/equipos" className="text-blue-600 hover:underline">
          Gestionar equipos
        </Link>
        <Link to="/admin/reservas" className="text-blue-600 hover:underline">
          Ver todas las reservas
        </Link>
        <Link to="/admin/reportes/ocupacion" className="text-blue-600 hover:underline">
          Reporte de ocupación
        </Link>
        <Link to="/admin/reportes/proveedores" className="text-blue-600 hover:underline">
          Actividad de proveedores
        </Link>
        <Link to="/admin/reportes/sistema" className="text-blue-600 hover:underline">
          Actividad del sistema
        </Link>
        <Link to="/admin/auditoria" className="text-blue-600 hover:underline">
          Ver auditoria del sistema
        </Link>
      </div>
    </Layout>
  );
}

export default AdminDashboardPage;