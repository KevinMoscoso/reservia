import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { downloadReportCsv, getSystemActivityReport } from '../api/reports';
import { defaultDateRange } from '../utils/dateRange';

function SystemActivityReportPage() {
  const [fechaInicio, setFechaInicio] = useState(() => defaultDateRange().fechaInicio);
  const [fechaFin, setFechaFin] = useState(() => defaultDateRange().fechaFin);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  function fetchReport() {
    setError('');
    return getSystemActivityReport(fechaInicio, fechaFin)
      .then((data) => setStats(data))
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    fetchReport().finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleGenerar(event) {
    event.preventDefault();
    await fetchReport();
  }

  async function handleExport() {
    try {
      await downloadReportCsv(
        '/reports/system',
        fechaInicio,
        fechaFin,
        'actividad_sistema.csv'
      );
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Actividad del sistema</h1>

      <form onSubmit={handleGenerar} className="mb-4 flex flex-wrap items-end gap-3">
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
          Generar
        </button>

        <button
          type="button"
          onClick={handleExport}
          className="rounded bg-gray-600 px-4 py-2 text-white hover:bg-gray-700"
        >
          Exportar CSV
        </button>
      </form>

      {stats && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Usuarios activos</p>
            <p className="text-xl font-semibold text-gray-800">{stats.usuarios_activos}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Total reservas salas</p>
            <p className="text-xl font-semibold text-gray-800">{stats.total_reservas_salas}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Total reservas equipos</p>
            <p className="text-xl font-semibold text-gray-800">{stats.total_reservas_equipos}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Total citas</p>
            <p className="text-xl font-semibold text-gray-800">{stats.total_citas}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Total general</p>
            <p className="text-xl font-semibold text-gray-800">{stats.total_general}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">Total cancelaciones</p>
            <p className="text-xl font-semibold text-gray-800">{stats.total_cancelaciones}</p>
          </div>
          <div className="rounded border border-gray-200 bg-white p-4">
            <p className="text-sm text-gray-600">% Cancelación</p>
            <p className="text-xl font-semibold text-gray-800">{stats.porcentaje_cancelacion}%</p>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default SystemActivityReportPage;