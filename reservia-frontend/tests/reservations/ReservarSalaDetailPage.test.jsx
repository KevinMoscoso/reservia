import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import ReservarSalaDetailPage from '../../src/pages/ReservarSalaDetailPage';

const CLIENT_USER = {
  id: 1,
  email: 'cliente@example.com',
  full_name: 'Cliente Uno',
  role: 'client',
  status: 'active',
};

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function mockFetchRoutes(routes) {
  global.fetch = vi.fn((url, options = {}) => {
    const method = options.method || 'GET';
    const key = `${method} ${url}`;
    const handler = routes[key];

    if (!handler) {
      return Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({ detail: `no mock for ${key}` }),
      });
    }

    return Promise.resolve(handler());
  });
}

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/recursos/salas/1/reservar']}>
      <AuthProvider>
        <Routes>
          <Route path="/recursos/salas/:id/reservar" element={<ReservarSalaDetailPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('ReservarSalaDetailPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('reserva_sala_detail_shows_availability_blocks', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Sala A', ubicacion: 'Piso 1', capacidad: 10, estado: 'active' },
        ],
      }),
      [`GET /api/resources/salas/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
          { hora_inicio: '09:30:00', hora_fin: '10:00:00', disponible: false },
        ],
      }),
    });

    renderPage();

    expect(await screen.findByText('09:00')).toBeInTheDocument();
    expect(screen.getByText('09:30')).toBeInTheDocument();
  });

  it('reserva_sala_detail_creates_booking_success', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Sala A', ubicacion: 'Piso 1', capacidad: 10, estado: 'active' },
        ],
      }),
      [`GET /api/resources/salas/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
        ],
      }),
      'POST /api/resources/salas/1/reservas': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 5,
          sala_id: 1,
          user_id: 1,
          fecha,
          hora_inicio: '09:00:00',
          hora_fin: '09:30:00',
          motivo: 'Reunion',
          estado: 'confirmada',
        }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByText('09:00'));
    await user.type(screen.getByLabelText(/motivo/i), 'Reunion');
    await user.click(screen.getByRole('button', { name: /^reservar$/i }));

    expect(await screen.findByText('Reserva creada exitosamente.')).toBeInTheDocument();
  });

  it('reserva_sala_detail_shows_overlap_error_from_api', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Sala A', ubicacion: 'Piso 1', capacidad: 10, estado: 'active' },
        ],
      }),
      [`GET /api/resources/salas/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
        ],
      }),
      'POST /api/resources/salas/1/reservas': () => ({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'el horario solicitado se solapa con una reserva existente' }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByText('09:00'));
    await user.type(screen.getByLabelText(/motivo/i), 'Reunion');
    await user.click(screen.getByRole('button', { name: /^reservar$/i }));

    expect(
      await screen.findByText('el horario solicitado se solapa con una reserva existente')
    ).toBeInTheDocument();
  });

  it('reserva_sala_detail_submit_disabled_without_selection', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Sala A', ubicacion: 'Piso 1', capacidad: 10, estado: 'active' },
        ],
      }),
      [`GET /api/resources/salas/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
        ],
      }),
    });

    renderPage();

    await screen.findByText('09:00');
    expect(screen.getByRole('button', { name: /^reservar$/i })).toBeDisabled();
  });
});