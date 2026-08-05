import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import {
  cancelReservaEquipo,
  cancelReservaSala,
  listMisReservasEquipos,
  listMisReservasSalas,
} from '../api/resources';
import { cancelCita, listMisCitas } from '../api/providers';

function ReservationSection({ title, items, emptyMessage, onCancel }) {
  return (
    <section className="mb-8">
      <h2 className="mb-2 text-lg font-semibold text-gray-800">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-600">{emptyMessage}</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((item) => {
            const isCancelled = item.estado === 'cancelada';
            return (
              <li
                key={item.id}
                className={`flex items-center justify-between rounded border border-gray-200 bg-white p-3 text-sm ${
                  isCancelled ? 'text-gray-400' : ''
                }`}
              >
                <div>
                  <p>
                    {item.fecha} · {item.hora_inicio.slice(0, 5)} - {item.hora_fin.slice(0, 5)}
                  </p>
                  <p>{item.motivo}</p>
                  <p>{item.estado}</p>
                </div>
                {item.estado === 'confirmada' && (
                  <button
                    onClick={() => onCancel(item.id)}
                    className="rounded bg-red-600 px-3 py-1.5 text-white hover:bg-red-700"
                  >
                    Cancelar
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

function MisReservasPage() {
  const [loading, setLoading] = useState(true);
  const [reservasSalas, setReservasSalas] = useState([]);
  const [reservasEquipos, setReservasEquipos] = useState([]);
  const [citas, setCitas] = useState([]);

  useEffect(() => {
    Promise.all([listMisReservasSalas(), listMisReservasEquipos(), listMisCitas()])
      .then(([salasData, equiposData, citasData]) => {
        setReservasSalas(salasData);
        setReservasEquipos(equiposData);
        setCitas(citasData);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleCancelSala(id) {
    const actualizada = await cancelReservaSala(id);
    setReservasSalas((prev) => prev.map((r) => (r.id === id ? actualizada : r)));
  }

  async function handleCancelEquipo(id) {
    const actualizada = await cancelReservaEquipo(id);
    setReservasEquipos((prev) => prev.map((r) => (r.id === id ? actualizada : r)));
  }

  async function handleCancelCita(id) {
    const actualizada = await cancelCita(id);
    setCitas((prev) => prev.map((c) => (c.id === id ? actualizada : c)));
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Mis reservas</h1>

      <ReservationSection
        title="Mis reservas de salas"
        items={reservasSalas}
        emptyMessage="No tienes reservas de salas."
        onCancel={handleCancelSala}
      />

      <ReservationSection
        title="Mis reservas de equipos"
        items={reservasEquipos}
        emptyMessage="No tienes reservas de equipos."
        onCancel={handleCancelEquipo}
      />

      <ReservationSection
        title="Mis citas"
        items={citas}
        emptyMessage="No tienes citas."
        onCancel={handleCancelCita}
      />
    </Layout>
  );
}

export default MisReservasPage;