import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import AdminReservasPage from '../../src/pages/AdminReservasPage';

const ADMIN_USER = {
  id: 1,
  email: 'admin@example.com',
  full_name: 'Admin Uno',
  role: 'admin',
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
    <MemoryRouter initialEntries={['/admin/reservas']}>
      <AuthProvider>
        <AdminReservasPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('AdminReservasPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('admin_reservas_lists_all_salas_equipos_and_citas', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            sala_id: 10,
            sala_nombre: 'Sala A',
            user_id: 2,
            user_full_name: 'Cliente A',
            user_email: 'clientea@example.com',
            fecha: '2026-08-10',
            hora_inicio: '09:00:00',
            hora_fin: '09:30:00',
            motivo: 'Reunion',
            estado: 'confirmada',
          },
        ],
      }),
      'GET /api/resources/equipos/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 2,
            equipo_id: 20,
            equipo_nombre: 'Proyector',
            user_id: 3,
            user_full_name: 'Cliente B',
            user_email: 'clienteb@example.com',
            fecha: '2026-08-11',
            hora_inicio: '10:00:00',
            hora_fin: '10:30:00',
            motivo: 'Prestamo',
            estado: 'confirmada',
          },
        ],
      }),
      'GET /api/providers/citas': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 3,
            provider_profile_id: 30,
            provider_full_name: 'Proveedor Uno',
            user_id: 4,
            user_full_name: 'Cliente C',
            user_email: 'clientec@example.com',
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

    expect(await screen.findByText('Sala A')).toBeInTheDocument();
    expect(screen.getByText('Proyector')).toBeInTheDocument();
    expect(screen.getByText('Proveedor Uno')).toBeInTheDocument();
    expect(screen.getByText('Cliente A')).toBeInTheDocument();
    expect(screen.getByText('clientea@example.com')).toBeInTheDocument();
  });

  it('admin_reservas_cancels_reserva_sala_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            sala_id: 10,
            sala_nombre: 'Sala A',
            user_id: 2,
            user_full_name: 'Cliente A',
            user_email: 'clientea@example.com',
            fecha: '2026-08-10',
            hora_inicio: '09:00:00',
            hora_fin: '09:30:00',
            motivo: 'Reunion',
            estado: 'confirmada',
          },
        ],
      }),
      'GET /api/resources/equipos/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/citas': () => ({
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
          sala_nombre: 'Sala A',
          user_id: 2,
          user_full_name: 'Cliente A',
          user_email: 'clientea@example.com',
          fecha: '2026-08-10',
          hora_inicio: '09:00:00',
          hora_fin: '09:30:00',
          motivo: 'Reunion',
          estado: 'cancelada',
        }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await screen.findByText('Sala A');
    await user.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(await screen.findByText('cancelada')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
  });

  it('admin_reservas_citas_are_read_only', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 0 }),
      }),
      'GET /api/resources/salas/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/resources/equipos/reservas': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/citas': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 3,
            provider_profile_id: 30,
            provider_full_name: 'Proveedor Uno',
            user_id: 4,
            user_full_name: 'Cliente C',
            user_email: 'clientec@example.com',
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

    await screen.findByText('Proveedor Uno');
    expect(screen.queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
  });
});