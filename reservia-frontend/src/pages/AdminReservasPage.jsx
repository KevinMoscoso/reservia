import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import {
  cancelReservaEquipo,
  cancelReservaSala,
  listAllReservasEquipos,
  listAllReservasSalas,
} from '../api/resources';
import { listAllCitas } from '../api/providers';

const EMPTY_PAGE = { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 };

function ReservasTable({
  items,
  resourceLabel,
  resourceKeyGetter,
  onCancel,
  emptyMessage,
  readOnly,
  page,
  totalPages,
  onPrev,
  onNext,
}) {
  if (items.length === 0) {
    return <p className="text-sm text-gray-600">{emptyMessage}</p>;
  }

  return (
    <>
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
      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={onPrev}
          disabled={page <= 1}
          className="rounded bg-gray-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        >
          Anterior
        </button>
        <span className="text-sm text-gray-700">
          Página {page} de {totalPages}
        </span>
        <button
          onClick={onNext}
          disabled={page >= totalPages}
          className="rounded bg-gray-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        >
          Siguiente
        </button>
      </div>
    </>
  );
}

function AdminReservasPage() {
  const [pageSalas, setPageSalas] = useState(1);
  const [dataSalas, setDataSalas] = useState(EMPTY_PAGE);
  const [loadingSalas, setLoadingSalas] = useState(true);

  const [pageEquipos, setPageEquipos] = useState(1);
  const [dataEquipos, setDataEquipos] = useState(EMPTY_PAGE);
  const [loadingEquipos, setLoadingEquipos] = useState(true);

  const [pageCitas, setPageCitas] = useState(1);
  const [dataCitas, setDataCitas] = useState(EMPTY_PAGE);
  const [loadingCitas, setLoadingCitas] = useState(true);

  useEffect(() => {
    listAllReservasSalas(pageSalas).then(setDataSalas).finally(() => setLoadingSalas(false));
  }, [pageSalas]);

  useEffect(() => {
    listAllReservasEquipos(pageEquipos).then(setDataEquipos).finally(() => setLoadingEquipos(false));
  }, [pageEquipos]);

  useEffect(() => {
    listAllCitas(pageCitas).then(setDataCitas).finally(() => setLoadingCitas(false));
  }, [pageCitas]);

  async function handleCancelSala(id) {
    const actualizada = await cancelReservaSala(id);
    setDataSalas((prev) => ({ ...prev, items: prev.items.map((r) => (r.id === id ? actualizada : r)) }));
  }

  async function handleCancelEquipo(id) {
    const actualizada = await cancelReservaEquipo(id);
    setDataEquipos((prev) => ({ ...prev, items: prev.items.map((r) => (r.id === id ? actualizada : r)) }));
  }

  if (loadingSalas || loadingEquipos || loadingCitas) {
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
          items={dataSalas.items}
          resourceLabel="Sala"
          resourceKeyGetter={(item) => item.sala_nombre}
          onCancel={handleCancelSala}
          emptyMessage="No hay reservas de salas registradas."
          readOnly={false}
          page={dataSalas.page}
          totalPages={dataSalas.total_pages}
          onPrev={() => setPageSalas((p) => p - 1)}
          onNext={() => setPageSalas((p) => p + 1)}
        />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Todas las reservas de equipos</h2>
        <ReservasTable
          items={dataEquipos.items}
          resourceLabel="Equipo"
          resourceKeyGetter={(item) => item.equipo_nombre}
          onCancel={handleCancelEquipo}
          emptyMessage="No hay reservas de equipos registradas."
          readOnly={false}
          page={dataEquipos.page}
          totalPages={dataEquipos.total_pages}
          onPrev={() => setPageEquipos((p) => p - 1)}
          onNext={() => setPageEquipos((p) => p + 1)}
        />
      </section>

      <section>
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Todas las citas</h2>
        <ReservasTable
          items={dataCitas.items}
          resourceLabel="Proveedor"
          resourceKeyGetter={(item) => item.provider_full_name}
          onCancel={undefined}
          emptyMessage="No hay citas registradas."
          readOnly
          page={dataCitas.page}
          totalPages={dataCitas.total_pages}
          onPrev={() => setPageCitas((p) => p - 1)}
          onNext={() => setPageCitas((p) => p + 1)}
        />
      </section>
    </Layout>
  );
}

export default AdminReservasPage;