import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import ProviderDashboardPage from '../../src/pages/ProviderDashboardPage';

const PROVIDER_USER = {
  id: 5,
  email: 'proveedor@example.com',
  full_name: 'Proveedor Uno',
  role: 'provider',
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

function renderProviderDashboard() {
  return render(
    <MemoryRouter initialEntries={['/provider']}>
      <AuthProvider>
        <ProviderDashboardPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

const UNREAD_COUNT_MOCK = {
  'GET /api/notifications/me/unread-count': () => ({
    ok: true,
    status: 200,
    json: async () => ({ count: 0 }),
  }),
};

const EMPTY_DATE_BLOCKS_MOCK = {
  'GET /api/providers/me/date-blocks': () => ({
    ok: true,
    status: 200,
    json: async () => [],
  }),
};

describe('ProviderDashboardPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('provider_dashboard_loads_profile_and_schedule', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            provider_profile_id: 10,
            day_of_week: 'monday',
            start_time: '09:00:00',
            end_time: '10:00:00',
            estado: 'active',
          },
        ],
      }),
      ...EMPTY_DATE_BLOCKS_MOCK,
    });

    renderProviderDashboard();

    expect(await screen.findByDisplayValue('30')).toBeInTheDocument();
    expect(await screen.findByText('09:00 - 10:00')).toBeInTheDocument();
  });

  it('provider_dashboard_updates_slot_duration_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      ...EMPTY_DATE_BLOCKS_MOCK,
      'PUT /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 45 }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    const input = await screen.findByDisplayValue('30');
    fireEvent.change(input, { target: { value: '45' } });

    await user.click(screen.getByRole('button', { name: /guardar/i }));

    expect(await screen.findByText(/perfil actualizado/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('45')).toBeInTheDocument();
  });

  it('provider_dashboard_adds_schedule_block_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      ...EMPTY_DATE_BLOCKS_MOCK,
      'POST /api/providers/me/schedule': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 2,
          provider_profile_id: 10,
          day_of_week: 'tuesday',
          start_time: '11:00:00',
          end_time: '12:00:00',
          estado: 'active',
        }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    await screen.findByRole('button', { name: /agregar bloque/i });

    await user.selectOptions(screen.getByLabelText(/día/i), 'tuesday');
    fireEvent.change(screen.getByLabelText(/hora inicio/i), { target: { value: '11:00' } });
    fireEvent.change(screen.getByLabelText(/hora fin/i), { target: { value: '12:00' } });
    await user.click(screen.getByRole('button', { name: /agregar bloque/i }));

    expect(await screen.findByText('11:00 - 12:00')).toBeInTheDocument();
  });

  it('provider_dashboard_shows_overlap_error_from_api', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      ...EMPTY_DATE_BLOCKS_MOCK,
      'POST /api/providers/me/schedule': () => ({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'el bloque se solapa con uno existente' }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    await screen.findByRole('button', { name: /agregar bloque/i });

    await user.selectOptions(screen.getByLabelText(/día/i), 'wednesday');
    fireEvent.change(screen.getByLabelText(/hora inicio/i), { target: { value: '09:00' } });
    fireEvent.change(screen.getByLabelText(/hora fin/i), { target: { value: '10:00' } });
    await user.click(screen.getByRole('button', { name: /agregar bloque/i }));

    expect(
      await screen.findByText('el bloque se solapa con uno existente')
    ).toBeInTheDocument();
  });

  it('provider_dashboard_deactivates_schedule_block_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 3,
            provider_profile_id: 10,
            day_of_week: 'friday',
            start_time: '08:00:00',
            end_time: '09:00:00',
            estado: 'active',
          },
        ],
      }),
      ...EMPTY_DATE_BLOCKS_MOCK,
      'PATCH /api/providers/me/schedule/3/deactivate': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          id: 3,
          provider_profile_id: 10,
          day_of_week: 'friday',
          start_time: '08:00:00',
          end_time: '09:00:00',
          estado: 'inactive',
        }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    await screen.findByText('08:00 - 09:00');
    await user.click(screen.getByRole('button', { name: /desactivar/i }));

    expect(await screen.findByText('inactive')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /desactivar/i })).not.toBeInTheDocument();
  });

  it('provider_dashboard_adds_date_block_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/me/date-blocks': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'POST /api/providers/me/date-blocks': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 1,
          provider_profile_id: 10,
          fecha: '2026-09-01',
          motivo: 'Vacaciones',
          estado: 'active',
        }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    await screen.findByRole('button', { name: /bloquear fecha/i });

    fireEvent.change(screen.getByLabelText(/^fecha$/i), { target: { value: '2026-09-01' } });
    await user.type(screen.getByLabelText(/motivo \(opcional\)/i), 'Vacaciones');
    await user.click(screen.getByRole('button', { name: /bloquear fecha/i }));

    expect(await screen.findByText('2026-09-01')).toBeInTheDocument();
    expect(screen.getByText('Vacaciones')).toBeInTheDocument();
  });

  it('provider_dashboard_shows_conflict_error_when_blocking_date_with_citas', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => PROVIDER_USER,
      }),
      ...UNREAD_COUNT_MOCK,
      'GET /api/providers/me/profile': () => ({
        ok: true,
        status: 200,
        json: async () => ({ id: 10, user_id: 5, slot_duration_minutes: 30 }),
      }),
      'GET /api/providers/me/schedule': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'GET /api/providers/me/date-blocks': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'POST /api/providers/me/date-blocks': () => ({
        ok: false,
        status: 409,
        json: async () => ({
          detail: 'ya tienes citas confirmadas en esa fecha; cancelalas antes de bloquearla',
        }),
      }),
    });

    const user = userEvent.setup();
    renderProviderDashboard();

    await screen.findByRole('button', { name: /bloquear fecha/i });

    fireEvent.change(screen.getByLabelText(/^fecha$/i), { target: { value: '2026-09-02' } });
    await user.click(screen.getByRole('button', { name: /bloquear fecha/i }));

    expect(
      await screen.findByText(
        'ya tienes citas confirmadas en esa fecha; cancelalas antes de bloquearla'
      )
    ).toBeInTheDocument();
  });
});
