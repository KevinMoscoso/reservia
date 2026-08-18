import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { downloadReportCsv, getProviderActivityReport } from '../api/reports';
import { defaultDateRange } from '../utils/dateRange';

function ProviderActivityReportPage() {
  const [fechaInicio, setFechaInicio] = useState(() => defaultDateRange().fechaInicio);
  const [fechaFin, setFechaFin] = useState(() => defaultDateRange().fechaFin);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  function fetchReport() {
    setError('');
    return getProviderActivityReport(fechaInicio, fechaFin)
      .then((data) => setItems(data.items))
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
        '/reports/providers',
        fechaInicio,
        fechaFin,
        'actividad_proveedores.csv'
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Actividad de proveedores</h1>

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

      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-gray-300">
            <th className="py-2">Proveedor</th>
            <th className="py-2">Citas confirmadas</th>
            <th className="py-2">Citas canceladas</th>
            <th className="py-2">Total</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.provider_profile_id} className="border-b border-gray-100">
              <td className="py-2">{item.provider_full_name}</td>
              <td className="py-2">{item.citas_confirmadas}</td>
              <td className="py-2">{item.citas_canceladas}</td>
              <td className="py-2">{item.total_citas}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}

export default ProviderActivityReportPage;