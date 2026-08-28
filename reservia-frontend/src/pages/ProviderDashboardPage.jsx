import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import {
  addDateBlock,
  addScheduleBlock,
  deactivateDateBlock,
  deactivateScheduleBlock,
  getMyDateBlocks,
  getMyProfile,
  getMySchedule,
  updateMyProfile,
} from '../api/providers';
import { DAY_LABELS, DAY_ORDER } from '../utils/dayOfWeekLabels';

function isSlotDurationValid(value) {
  const num = Number(value);
  return Number.isInteger(num) && num >= 5 && num <= 480;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function ProviderDashboardPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [schedule, setSchedule] = useState([]);
  const [dateBlocks, setDateBlocks] = useState([]);

  const [slotDuration, setSlotDuration] = useState('');
  const [profileError, setProfileError] = useState('');
  const [profileSuccess, setProfileSuccess] = useState('');

  const [day, setDay] = useState(DAY_ORDER[0]);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [scheduleError, setScheduleError] = useState('');

  const [fechaBloqueo, setFechaBloqueo] = useState(todayISO());
  const [motivoBloqueo, setMotivoBloqueo] = useState('');
  const [dateBlockError, setDateBlockError] = useState('');

  useEffect(() => {
    Promise.all([getMyProfile(), getMySchedule(), getMyDateBlocks()])
      .then(([profileData, scheduleData, dateBlocksData]) => {
        setSlotDuration(String(profileData.slot_duration_minutes));
        setSchedule(scheduleData);
        setDateBlocks(dateBlocksData);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSaveProfile(event) {
    event.preventDefault();
    setProfileError('');
    setProfileSuccess('');

    if (!isSlotDurationValid(slotDuration)) {
      setProfileError('La duración debe ser un entero entre 5 y 480.');
      return;
    }

    try {
      const actualizado = await updateMyProfile({
        slot_duration_minutes: Number(slotDuration),
      });
      setSlotDuration(String(actualizado.slot_duration_minutes));
      setProfileSuccess('Perfil actualizado.');
    } catch (err) {
      setProfileError(err.message);
    }
  }

  async function handleAddScheduleBlock(event) {
    event.preventDefault();
    setScheduleError('');

    if (!(endTime > startTime)) {
      setScheduleError('La hora de fin debe ser mayor a la hora de inicio.');
      return;
    }

    try {
      const nuevoBloque = await addScheduleBlock({
        day_of_week: day,
        start_time: startTime,
        end_time: endTime,
      });
      setSchedule((prev) => [...prev, nuevoBloque]);
      setStartTime('');
      setEndTime('');
    } catch (err) {
      setScheduleError(err.message);
    }
  }

  async function handleDeactivateBlock(id) {
    const actualizado = await deactivateScheduleBlock(id);
    setSchedule((prev) => prev.map((block) => (block.id === id ? actualizado : block)));
  }

  async function handleAddDateBlock(event) {
    event.preventDefault();
    setDateBlockError('');

    try {
      const nuevoBloqueo = await addDateBlock({
        fecha: fechaBloqueo,
        motivo: motivoBloqueo || null,
      });
      setDateBlocks((prev) => [nuevoBloqueo, ...prev]);
      setFechaBloqueo(todayISO());
      setMotivoBloqueo('');
    } catch (err) {
      setDateBlockError(err.message);
    }
  }

  async function handleDeactivateDateBlock(id) {
    const actualizado = await deactivateDateBlock(id);
    setDateBlocks((prev) => prev.map((block) => (block.id === id ? actualizado : block)));
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">
        Bienvenido, {user?.full_name}
      </h1>

      <section className="mb-8 max-w-sm">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Perfil</h2>

        {profileSuccess && <p className="mb-2 text-sm text-green-600">{profileSuccess}</p>}
        {profileError && <p className="mb-2 text-sm text-red-600">{profileError}</p>}

        <form onSubmit={handleSaveProfile} className="flex items-end gap-3">
          <div>
            <label htmlFor="slot_duration_minutes" className="mb-1 block text-sm text-gray-700">
              Duración del slot (minutos)
            </label>
            <input
              id="slot_duration_minutes"
              type="number"
              value={slotDuration}
              onChange={(e) => setSlotDuration(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <button
            type="submit"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Guardar
          </button>
        </form>
      </section>

      <section className="mb-8">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Horario semanal</h2>

        {DAY_ORDER.map((dayKey) => {
          const bloquesDelDia = schedule.filter((block) => block.day_of_week === dayKey);

          return (
            <div key={dayKey} className="mb-4">
              <h3 className="font-medium text-gray-700">{DAY_LABELS[dayKey]}</h3>
              {bloquesDelDia.length === 0 && (
                <p className="text-sm text-gray-400">Sin bloques configurados.</p>
              )}
              <ul>
                {bloquesDelDia.map((block) => {
                  const isActive = block.estado === 'active';
                  return (
                    <li
                      key={block.id}
                      className={`flex items-center gap-3 text-sm ${
                        !isActive ? 'text-gray-400' : ''
                      }`}
                    >
                      <span>
                        {block.start_time.slice(0, 5)} - {block.end_time.slice(0, 5)}
                      </span>
                      <span>{block.estado}</span>
                      {isActive && (
                        <button
                          onClick={() => handleDeactivateBlock(block.id)}
                          className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        >
                          Desactivar
                        </button>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}

        <form onSubmit={handleAddScheduleBlock} className="mt-4 flex flex-wrap items-end gap-3">
          {scheduleError && <p className="w-full text-sm text-red-600">{scheduleError}</p>}

          <div>
            <label htmlFor="day_of_week" className="mb-1 block text-sm text-gray-700">
              Día
            </label>
            <select
              id="day_of_week"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              className="rounded border border-gray-300 px-3 py-2"
            >
              {DAY_ORDER.map((dayKey) => (
                <option key={dayKey} value={dayKey}>
                  {DAY_LABELS[dayKey]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="start_time" className="mb-1 block text-sm text-gray-700">
              Hora inicio
            </label>
            <input
              id="start_time"
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="rounded border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <div>
            <label htmlFor="end_time" className="mb-1 block text-sm text-gray-700">
              Hora fin
            </label>
            <input
              id="end_time"
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="rounded border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <button
            type="submit"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Agregar bloque
          </button>
        </form>
      </section>

      <section className="mb-8">
        <h2 className="mb-2 text-lg font-semibold text-gray-800">Fechas bloqueadas</h2>

        {dateBlocks.length === 0 && (
          <p className="text-sm text-gray-400">No tienes fechas bloqueadas.</p>
        )}

        <ul className="flex flex-col gap-2">
          {dateBlocks.map((block) => {
            const isActive = block.estado === 'active';
            return (
              <li
                key={block.id}
                className={`flex items-center gap-3 text-sm ${!isActive ? 'text-gray-400' : ''}`}
              >
                <span>{block.fecha}</span>
                <span>{block.motivo || 'Sin motivo especificado'}</span>
                <span>{block.estado}</span>
                {isActive && (
                  <button
                    onClick={() => handleDeactivateDateBlock(block.id)}
                    className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                  >
                    Desbloquear
                  </button>
                )}
              </li>
            );
          })}
        </ul>

        <form onSubmit={handleAddDateBlock} className="mt-4 flex flex-wrap items-end gap-3">
          {dateBlockError && <p className="w-full text-sm text-red-600">{dateBlockError}</p>}

          <div>
            <label htmlFor="fecha_bloqueo" className="mb-1 block text-sm text-gray-700">
              Fecha
            </label>
            <input
              id="fecha_bloqueo"
              type="date"
              min={todayISO()}
              value={fechaBloqueo}
              onChange={(e) => setFechaBloqueo(e.target.value)}
              className="rounded border border-gray-300 px-3 py-2"
            />
          </div>

          <div>
            <label htmlFor="motivo_bloqueo" className="mb-1 block text-sm text-gray-700">
              Motivo (opcional)
            </label>
            <input
              id="motivo_bloqueo"
              type="text"
              value={motivoBloqueo}
              onChange={(e) => setMotivoBloqueo(e.target.value)}
              className="rounded border border-gray-300 px-3 py-2"
            />
          </div>

          <button
            type="submit"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Bloquear fecha
          </button>
        </form>
      </section>

      <section className="mt-8">
        <Link to="/reportes/proveedores" className="text-blue-600 hover:underline">
          Ver mi actividad
        </Link>
      </section>
    </Layout>
  );
}

export default ProviderDashboardPage;