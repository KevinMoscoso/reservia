import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import SystemActivityReportPage from '../../src/pages/SystemActivityReportPage';
import { defaultDateRange } from '../../src/utils/dateRange';

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
    <MemoryRouter initialEntries={['/admin/reportes/sistema']}>
      <AuthProvider>
        <SystemActivityReportPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('SystemActivityReportPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('system_activity_report_shows_stats', async () => {
    const { fechaInicio, fechaFin } = defaultDateRange();

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
      [`GET /api/reports/system?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          usuarios_activos: 4,
          total_reservas_salas: 10,
          total_reservas_equipos: 5,
          total_citas: 3,
          total_general: 18,
          total_cancelaciones: 2,
          porcentaje_cancelacion: 11.11,
        }),
      }),
    });

    renderPage();

    expect(await screen.findByText('4')).toBeInTheDocument();
    expect(screen.getByText('18')).toBeInTheDocument();
    expect(screen.getByText('11.11%')).toBeInTheDocument();
  });
});