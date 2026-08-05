import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { listSalas } from '../api/resources';

function ReservarSalasPage() {
  const [salas, setSalas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSalas()
      .then((data) => setSalas(data.filter((sala) => sala.estado === 'active')))
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Salas disponibles</h1>
      <ul className="flex flex-col gap-3">
        {salas.map((sala) => (
          <li
            key={sala.id}
            className="flex items-center justify-between rounded border border-gray-200 bg-white p-4"
          >
            <div>
              <p className="font-medium text-gray-800">{sala.nombre}</p>
              <p className="text-sm text-gray-600">
                {sala.ubicacion} · Capacidad: {sala.capacidad}
              </p>
            </div>
            <Link
              to={`/recursos/salas/${sala.id}/reservar`}
              className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
            >
              Reservar
            </Link>
          </li>
        ))}
      </ul>
    </Layout>
  );
}

export default ReservarSalasPage;