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
      <Link to="/admin/providers/new" className="text-blue-600 hover:underline">
        Crear nuevo proveedor
      </Link>
    </Layout>
  );
}

export default AdminDashboardPage;