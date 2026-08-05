import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { listProviders } from '../api/providers';

function ProveedoresPage() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProviders()
      .then((data) => setProviders(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Proveedores</h1>
      <ul className="flex flex-col gap-3">
        {providers.map((provider) => (
          <li
            key={provider.id}
            className="flex items-center justify-between rounded border border-gray-200 bg-white p-4"
          >
            <div>
              <p className="font-medium text-gray-800">{provider.full_name}</p>
              <p className="text-sm text-gray-600">
                Duración de cita: {provider.slot_duration_minutes} min
              </p>
            </div>
            <Link
              to={`/proveedores/${provider.id}/agendar`}
              className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
            >
              Agendar cita
            </Link>
          </li>
        ))}
      </ul>
    </Layout>
  );
}

export default ProveedoresPage;