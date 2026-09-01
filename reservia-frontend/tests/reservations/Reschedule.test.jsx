import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import ReservarSalaDetailPage from '../../src/pages/ReservarSalaDetailPage';
import MisReservasPage from '../../src/pages/MisReservasPage';

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

describe('Reschedule', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('reschedule_banner_shown_when_reprogramar_param_present', async () => {
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

    render(
      <MemoryRouter initialEntries={['/recursos/salas/1/reservar?reprogramar=42']}>
        <AuthProvider>
          <Routes>
            <Route path="/recursos/salas/:id/reservar" element={<ReservarSalaDetailPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(
      await screen.findByText(
        'Estas reprogramando una reserva existente. Al confirmar, la reserva anterior se cancelara.'
      )
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^reprogramar$/i })).toBeInTheDocument();
  });

  it('reschedule_calls_reschedule_endpoint_not_create_endpoint', async () => {
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
      'PATCH /api/resources/salas/reservas/42/reschedule': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          id: 99,
          sala_id: 1,
          user_id: 1,
          fecha,
          hora_inicio: '09:00:00',
          hora_fin: '09:30:00',
          motivo: 'Reprogramada',
          estado: 'confirmada',
        }),
      }),
    });

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/recursos/salas/1/reservar?reprogramar=42']}>
        <AuthProvider>
          <Routes>
            <Route path="/recursos/salas/:id/reservar" element={<ReservarSalaDetailPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await user.click(await screen.findByText('09:00'));
    await user.type(screen.getByLabelText(/motivo/i), 'Reprogramada');
    await user.click(screen.getByRole('button', { name: /^reprogramar$/i }));

    expect(await screen.findByText('Reserva reprogramada exitosamente.')).toBeInTheDocument();

    expect(
      fetch.mock.calls.some(
        ([url]) =>
          typeof url === 'string' && url.includes('/resources/salas/reservas/42/reschedule')
      )
    ).toBe(true);
    expect(
      fetch.mock.calls.some(
        ([url, options]) =>
          typeof url === 'string' &&
          url === '/api/resources/salas/1/reservas' &&
          options?.method === 'POST'
      )
    ).toBe(false);
  });

  it('mis_reservas_reschedule_button_navigates_to_correct_url', async () => {
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
      'GET /api/resources/salas/reservas/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 7,
              sala_id: 3,
              user_id: 1,
              fecha: '2026-09-01',
              hora_inicio: '09:00:00',
              hora_fin: '09:30:00',
              motivo: 'Reunion',
              estado: 'confirmada',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
      'GET /api/resources/equipos/reservas/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
      }),
      'GET /api/providers/citas/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
      }),
    });

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/mis-reservas']}>
        <AuthProvider>
          <Routes>
            <Route path="/mis-reservas" element={<MisReservasPage />} />
            <Route
              path="/recursos/salas/:id/reservar"
              element={<div>Pagina de reprogramacion de sala</div>}
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByText('Reunion');
    await user.click(screen.getByRole('button', { name: /reprogramar/i }));

    expect(await screen.findByText('Pagina de reprogramacion de sala')).toBeInTheDocument();
  });
});