import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import AvailabilityGrid from '../components/AvailabilityGrid';
import {
  createReservaEquipo,
  getEquipoAvailability,
  listEquipos,
  rescheduleReservaEquipo,
} from '../api/resources';

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function ReservarEquipoDetailPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const reprogramarId = searchParams.get('reprogramar');

  const [equipo, setEquipo] = useState(null);
  const [loadingEquipo, setLoadingEquipo] = useState(true);

  const [fecha, setFecha] = useState(todayISO());
  const [blocks, setBlocks] = useState([]);
  const [selectedStart, setSelectedStart] = useState(null);

  const [numBloques, setNumBloques] = useState('1');
  const [motivo, setMotivo] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    listEquipos()
      .then((data) => {
        const found = data.find((e) => String(e.id) === String(id));
        setEquipo(found || null);
      })
      .finally(() => setLoadingEquipo(false));
  }, [id]);

  function loadAvailability() {
    getEquipoAvailability(id, fecha).then((data) => setBlocks(data));
  }

  useEffect(() => {
    loadAvailability();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, fecha]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setSuccess('');

    const payload = {
      fecha,
      hora_inicio: selectedStart,
      num_bloques: Number(numBloques),
      motivo,
    };

    try {
      if (reprogramarId) {
        await rescheduleReservaEquipo(reprogramarId, payload);
        setSuccess('Reserva reprogramada exitosamente.');
      } else {
        await createReservaEquipo(id, payload);
        setSuccess('Reserva creada exitosamente.');
      }
      setSelectedStart(null);
      setMotivo('');
      loadAvailability();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loadingEquipo) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  if (!equipo) {
    return (
      <Layout>
        <p>Equipo no encontrado</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Reservar {equipo.nombre}</h1>

      {reprogramarId && (
        <div className="mb-4 rounded border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-800">
          Estas reprogramando una reserva existente. Al confirmar, la reserva anterior se cancelara.
        </div>
      )}

      <div className="mb-4">
        <label htmlFor="fecha" className="mb-1 block text-sm text-gray-700">
          Fecha
        </label>
        <input
          id="fecha"
          type="date"
          min={todayISO()}
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2"
        />
      </div>

      <AvailabilityGrid blocks={blocks} selectedStart={selectedStart} onSelect={setSelectedStart} />

      <form onSubmit={handleSubmit} className="mt-6 flex max-w-sm flex-col gap-3">
        {success && <p className="text-sm text-green-600">{success}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        <div>
          <label htmlFor="num_bloques" className="mb-1 block text-sm text-gray-700">
            Número de bloques consecutivos
          </label>
          <input
            id="num_bloques"
            type="number"
            value={numBloques}
            onChange={(e) => setNumBloques(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="motivo" className="mb-1 block text-sm text-gray-700">
            Motivo
          </label>
          <textarea
            id="motivo"
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <button
          type="submit"
          disabled={!selectedStart}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          {reprogramarId ? 'Reprogramar' : 'Reservar'}
        </button>
      </form>
    </Layout>
  );
}

export default ReservarEquipoDetailPage;