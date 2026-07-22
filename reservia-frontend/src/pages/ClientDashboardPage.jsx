import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

function ClientDashboardPage() {
  const { user } = useAuth();

  return (
    <Layout>
      <p className="text-gray-700">
        Bienvenido, {user?.full_name}. Próximamente verás aquí tus reservas.
      </p>
    </Layout>
  );
}

export default ClientDashboardPage;