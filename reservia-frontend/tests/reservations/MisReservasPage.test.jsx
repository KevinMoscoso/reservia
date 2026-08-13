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
      'GET /api/resources/salas/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [
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
      }),
      'GET /api/resources/equipos/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [
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
      }),
      'GET /api/providers/citas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [
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
      'GET /api/resources/salas/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [
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
      }),
      'GET /api/resources/equipos/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/citas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [],
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
      'GET /api/resources/salas/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/resources/equipos/reservas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/citas/me': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    });

    renderPage();

    expect(await screen.findByText('No tienes reservas de salas.')).toBeInTheDocument();
    expect(screen.getByText('No tienes reservas de equipos.')).toBeInTheDocument();
    expect(screen.getByText('No tienes citas.')).toBeInTheDocument();
  });
});
