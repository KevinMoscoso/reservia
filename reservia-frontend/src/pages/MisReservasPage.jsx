import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import {
  cancelReservaEquipo,
  cancelReservaSala,
  listMisReservasEquipos,
  listMisReservasSalas,
} from '../api/resources';
import { cancelCita, listMisCitas } from '../api/providers';

const EMPTY_PAGE = { items: [], total: 0, page: 1, page_size: 20, total_pages: 1 };

function ReservationSection({ title, items, page, totalPages, emptyMessage, onCancel, onPrev, onNext }) {
  return (
    <section className="mb-8">
      <h2 className="mb-2 text-lg font-semibold text-gray-800">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-600">{emptyMessage}</p>
      ) : (
        <>
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
      )}
    </section>
  );
}

function MisReservasPage() {
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
    listMisReservasSalas(pageSalas).then(setDataSalas).finally(() => setLoadingSalas(false));
  }, [pageSalas]);

  useEffect(() => {
    listMisReservasEquipos(pageEquipos).then(setDataEquipos).finally(() => setLoadingEquipos(false));
  }, [pageEquipos]);

  useEffect(() => {
    listMisCitas(pageCitas).then(setDataCitas).finally(() => setLoadingCitas(false));
  }, [pageCitas]);

  async function handleCancelSala(id) {
    const actualizada = await cancelReservaSala(id);
    setDataSalas((prev) => ({ ...prev, items: prev.items.map((r) => (r.id === id ? actualizada : r)) }));
  }

  async function handleCancelEquipo(id) {
    const actualizada = await cancelReservaEquipo(id);
    setDataEquipos((prev) => ({ ...prev, items: prev.items.map((r) => (r.id === id ? actualizada : r)) }));
  }

  async function handleCancelCita(id) {
    const actualizada = await cancelCita(id);
    setDataCitas((prev) => ({ ...prev, items: prev.items.map((c) => (c.id === id ? actualizada : c)) }));
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Mis reservas</h1>

      <ReservationSection
        title="Mis reservas de salas"
        items={dataSalas.items}
        page={dataSalas.page}
        totalPages={dataSalas.total_pages}
        emptyMessage="No tienes reservas de salas."
        onCancel={handleCancelSala}
        onPrev={() => setPageSalas((p) => p - 1)}
        onNext={() => setPageSalas((p) => p + 1)}
      />

      <ReservationSection
        title="Mis reservas de equipos"
        items={dataEquipos.items}
        page={dataEquipos.page}
        totalPages={dataEquipos.total_pages}
        emptyMessage="No tienes reservas de equipos."
        onCancel={handleCancelEquipo}
        onPrev={() => setPageEquipos((p) => p - 1)}
        onNext={() => setPageEquipos((p) => p + 1)}
      />

      <ReservationSection
        title="Mis citas"
        items={dataCitas.items}
        page={dataCitas.page}
        totalPages={dataCitas.total_pages}
        emptyMessage="No tienes citas."
        onCancel={handleCancelCita}
        onPrev={() => setPageCitas((p) => p - 1)}
        onNext={() => setPageCitas((p) => p + 1)}
      />
    </Layout>
  );
}

export default MisReservasPage;