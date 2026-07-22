import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

function ProviderDashboardPage() {
  const { user } = useAuth();

  return (
    <Layout>
      <p className="text-gray-700">
        Bienvenido, {user?.full_name}. Próximamente verás aquí tu calendario de citas.
      </p>
    </Layout>
  );
}

export default ProviderDashboardPage;