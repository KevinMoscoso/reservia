import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import MisReservasPage from '../../src/pages/MisReservasPage';

const CLIENT_USER = {
  id: 1,
  email: 'cliente@example.com',
  full_name: 'Cliente Uno',
  role: 'client',
  status: 'active',
};

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
    <MemoryRouter initialEntries={['/mis-reservas']}>
      <AuthProvider>
        <MisReservasPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('MisReservasPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('mis_reservas_lists_salas_equipos_and_citas', async () => {
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
              id: 1,
              sala_id: 10,
              user_id: 1,
              fecha: '2026-08-10',
              hora_inicio: '09:00:00',
              hora_fin: '09:30:00',
              motivo: 'Reunion de sala',
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
        json: async () => ({
          items: [
            {
              id: 2,
              equipo_id: 20,
              user_id: 1,
              fecha: '2026-08-11',
              hora_inicio: '10:00:00',
              hora_fin: '10:30:00',
              motivo: 'Prestamo de equipo',
              estado: 'confirmada',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
      'GET /api/providers/citas/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 3,
              provider_profile_id: 30,
              user_id: 1,
              fecha: '2026-08-12',
              hora_inicio: '11:00:00',
              hora_fin: '11:30:00',
              motivo: 'Consulta',
              estado: 'confirmada',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
    });

    renderPage();

    expect(await screen.findByText('Reunion de sala')).toBeInTheDocument();
    expect(screen.getByText('Prestamo de equipo')).toBeInTheDocument();
    expect(screen.getByText('Consulta')).toBeInTheDocument();
  });

  it('mis_reservas_cancels_reserva_sala_success', async () => {
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
              id: 1,
              sala_id: 10,
              user_id: 1,
              fecha: '2026-08-10',
              hora_inicio: '09:00:00',
              hora_fin: '09:30:00',
              motivo: 'Reunion de sala',
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
      'PATCH /api/resources/salas/reservas/1/cancel': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          id: 1,
          sala_id: 10,
          user_id: 1,
          fecha: '2026-08-10',
          hora_inicio: '09:00:00',
          hora_fin: '09:30:00',
          motivo: 'Reunion de sala',
          estado: 'cancelada',
        }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await screen.findByText('Reunion de sala');
    await user.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(await screen.findByText('cancelada')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
  });

  it('mis_reservas_shows_empty_state_when_no_reservations', async () => {
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
        json: async () => ({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
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

    renderPage();

    expect(await screen.findByText('No tienes reservas de salas.')).toBeInTheDocument();
    expect(screen.getByText('No tienes reservas de equipos.')).toBeInTheDocument();
    expect(screen.getByText('No tienes citas.')).toBeInTheDocument();
  });

  it('mis_reservas_salas_pagination_next_button_fetches_next_page', async () => {
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
              id: 1,
              sala_id: 10,
              user_id: 1,
              fecha: '2026-08-10',
              hora_inicio: '09:00:00',
              hora_fin: '09:30:00',
              motivo: 'Reunion de sala',
              estado: 'confirmada',
            },
          ],
          total: 21,
          page: 1,
          page_size: 20,
          total_pages: 2,
        }),
      }),
      'GET /api/resources/salas/reservas/me?page=2&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 21,
              sala_id: 10,
              user_id: 1,
              fecha: '2026-08-20',
              hora_inicio: '09:00:00',
              hora_fin: '09:30:00',
              motivo: 'Reunion pagina dos',
              estado: 'confirmada',
            },
          ],
          total: 21,
          page: 2,
          page_size: 20,
          total_pages: 2,
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
    renderPage();

    await screen.findByText('Reunion de sala');

    const siguienteButtons = screen.getAllByRole('button', { name: /siguiente/i });
    await user.click(siguienteButtons[0]);

    expect(
      fetch.mock.calls.some(
        ([url]) =>
          typeof url === 'string' &&
          url.includes('salas/reservas/me') &&
          url.includes('page=2')
      )
    ).toBe(true);
  });
});