import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import AgendarCitaPage from '../../src/pages/AgendarCitaPage';

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
    <MemoryRouter initialEntries={['/proveedores/1/agendar']}>
      <AuthProvider>
        <Routes>
          <Route path="/proveedores/:id/agendar" element={<AgendarCitaPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('AgendarCitaPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('agendar_cita_shows_provider_availability', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/providers/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, user_id: 2, full_name: 'Proveedor Uno', slot_duration_minutes: 30 },
        ],
      }),
      [`GET /api/providers/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
        ],
      }),
    });

    renderPage();

    expect(await screen.findByText('09:00')).toBeInTheDocument();
  });

  it('agendar_cita_creates_booking_success', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/providers/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, user_id: 2, full_name: 'Proveedor Uno', slot_duration_minutes: 30 },
        ],
      }),
      [`GET /api/providers/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [
          { hora_inicio: '09:00:00', hora_fin: '09:30:00', disponible: true },
        ],
      }),
      'POST /api/providers/1/citas': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 9,
          provider_profile_id: 1,
          user_id: 1,
          fecha,
          hora_inicio: '09:00:00',
          hora_fin: '09:30:00',
          motivo: 'Consulta',
          estado: 'confirmada',
        }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByText('09:00'));
    await user.type(screen.getByLabelText(/motivo/i), 'Consulta');
    await user.click(screen.getByRole('button', { name: /agendar cita/i }));

    expect(await screen.findByText('Cita agendada exitosamente.')).toBeInTheDocument();
  });

  it('agendar_cita_shows_empty_schedule_message_when_no_blocks', async () => {
    const fecha = todayISO();
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => CLIENT_USER,
      }),
      'GET /api/providers/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, user_id: 2, full_name: 'Proveedor Uno', slot_duration_minutes: 30 },
        ],
      }),
      [`GET /api/providers/1/availability?fecha=${fecha}`]: () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    });

    renderPage();

    expect(
      await screen.findByText('El proveedor no tiene horario disponible este dia.')
    ).toBeInTheDocument();
  });
});