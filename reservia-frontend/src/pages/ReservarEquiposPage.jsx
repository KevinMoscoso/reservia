import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { listEquipos } from '../api/resources';

function ReservarEquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listEquipos()
      .then((data) => setEquipos(data.filter((equipo) => equipo.estado === 'active')))
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Equipos disponibles</h1>
      <ul className="flex flex-col gap-3">
        {equipos.map((equipo) => (
          <li
            key={equipo.id}
            className="flex items-center justify-between rounded border border-gray-200 bg-white p-4"
          >
            <div>
              <p className="font-medium text-gray-800">{equipo.nombre}</p>
              <p className="text-sm text-gray-600">
                {equipo.codigo} · {equipo.categoria}
              </p>
            </div>
            <Link
              to={`/recursos/equipos/${equipo.id}/reservar`}
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

export default ReservarEquiposPage;