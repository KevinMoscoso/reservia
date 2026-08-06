import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import {
  cancelReservaEquipo,
  cancelReservaSala,
  listAllReservasEquipos,
  listAllReservasSalas,
} from '../api/resources';
import { listAllCitas } from '../api/providers';

function ReservasTable({ items, resourceLabel, resourceKeyGetter, onCancel, emptyMessage, readOnly }) {
  if (items.length === 0) {
    return <p className="text-sm text-gray-600">{emptyMessage}</p>;
  }

  return (
    <table className="w-full border-collapse text-left text-sm">
      <thead>
        <tr className="border-b border-gray-300">
          <th className="py-2">{resourceLabel}</th>
          <th className="py-2">Usuario</th>
          <th className="py-2">Fecha</th>
          <th className="py-2">Horario</th>
          <th className="py-2">Motivo</th>
          <th className="py-2">Estado</th>
          {!readOnly && <th className="py-2">Acciones</th>}
        </tr>
      </thead>
      <tbody>
        {items.map((item) => {
          const isCancelled = item.estado === 'cancelada';
          return (
            <tr
              key={item.id}
              className={`border-b border-gray-100 ${isCancelled ? 'text-gray-400' : ''}`}
            >
              <td className="py-2">{resourceKeyGetter(item)}</td>
              <td className="py-2">
                <div>{item.user_full_name}</div>
                <div className="text-xs text-gray-500">{item.user_email}</div>
              </td>
              <td className="py-2">{item.fecha}</td>
              <td className="py-2">
                {item.hora_inicio.slice(0, 5)} - {item.hora_fin.slice(0, 5)}
              </td>
              <td className="py-2">{item.motivo}</td>
              <td className="py-2">{item.estado}</td>
              {!readOnly && (
                <td className="py-2">
                  {item.estado === 'confirmada' && (
                    <button
                      onClick={() => onCancel(item.id)}
                      className="rounded bg-red-600 px-2 py-1 text-white"
                    >
                      Cancelar
                    </button>
                  )}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function AdminReservasPage() {
  const [loading, setLoading] = useState(true);
  const [reservasSalas, setReservasSalas] = useState([]);
  const [reservasEquipos, setReservasEquipos] = useState([]);
  const [citas, setCitas] = useState([]);

  useEffect(() => {
    Promise.all([listAllReservasSalas(), listAllReservasEquipos(), listAllCitas()])
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

  if (loading) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Todas las reservas</h1>

      <section className="mb-8">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Todas las reservas de salas</h2>
        <ReservasTable
          items={reservasSalas}
          resourceLabel="Sala"
          resourceKeyGetter={(item) => item.sala_nombre}
          onCancel={handleCancelSala}
          emptyMessage="No hay reservas de salas registradas."
          readOnly={false}
        />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Todas las reservas de equipos</h2>
        <ReservasTable
          items={reservasEquipos}
          resourceLabel="Equipo"
          resourceKeyGetter={(item) => item.equipo_nombre}
          onCancel={handleCancelEquipo}
          emptyMessage="No hay reservas de equipos registradas."
          readOnly={false}
        />
      </section>

      <section>
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Todas las citas</h2>
        <ReservasTable
          items={citas}
          resourceLabel="Proveedor"
          resourceKeyGetter={(item) => item.provider_full_name}
          onCancel={undefined}
          emptyMessage="No hay citas registradas."
          readOnly
        />
      </section>
    </Layout>
  );
}

export default AdminReservasPage;