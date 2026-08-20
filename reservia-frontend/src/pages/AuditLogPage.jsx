import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { getAuditLog } from '../api/audit';
import { defaultDateRange } from '../utils/dateRange';

const PAGE_SIZE = 20;

function AuditLogPage() {
  const [fechaInicio, setFechaInicio] = useState(() => defaultDateRange().fechaInicio);
  const [fechaFin, setFechaFin] = useState(() => defaultDateRange().fechaFin);
  const [page, setPage] = useState(1);
  const [searchTrigger, setSearchTrigger] = useState(0);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setError('');
    getAuditLog(fechaInicio, fechaFin, page, PAGE_SIZE)
      .then((result) => setData(result))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, searchTrigger]);

  function handleBuscar(event) {
    event.preventDefault();
    setPage(1);
    setSearchTrigger((t) => t + 1);
  }

  if (loading && !data) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Auditoría del sistema</h1>

      <form onSubmit={handleBuscar} className="mb-4 flex flex-wrap items-end gap-3">
        {error && <p className="w-full text-sm text-red-600">{error}</p>}

        <div>
          <label htmlFor="fecha_inicio" className="mb-1 block text-sm text-gray-700">
            Fecha inicio
          </label>
          <input
            id="fecha_inicio"
            type="date"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
            className="rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="fecha_fin" className="mb-1 block text-sm text-gray-700">
            Fecha fin
          </label>
          <input
            id="fecha_fin"
            type="date"
            value={fechaFin}
            onChange={(e) => setFechaFin(e.target.value)}
            className="rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Buscar
        </button>
      </form>

      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-gray-300">
            <th className="py-2">Fecha/Hora</th>
            <th className="py-2">Usuario</th>
            <th className="py-2">Acción</th>
            <th className="py-2">Entidad</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map((item) => (
            <tr key={item.id} className="border-b border-gray-100">
              <td className="py-2">{new Date(item.created_at).toLocaleString()}</td>
              <td className="py-2">{item.actor_full_name ?? 'Sistema'}</td>
              <td className="py-2">{item.action}</td>
              <td className="py-2">
                {item.entity_id != null ? `${item.entity_type} #${item.entity_id}` : item.entity_type}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {data && (
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={() => setPage((p) => p - 1)}
            disabled={page <= 1}
            className="rounded bg-gray-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
          >
            Anterior
          </button>
          <span className="text-sm text-gray-700">
            Página {page} de {data.total_pages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= data.total_pages}
            className="rounded bg-gray-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
          >
            Siguiente
          </button>
        </div>
      )}
    </Layout>
  );
}

export default AuditLogPage;