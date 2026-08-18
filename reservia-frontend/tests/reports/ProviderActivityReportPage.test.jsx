import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import ProviderActivityReportPage from '../../src/pages/ProviderActivityReportPage';
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
    <MemoryRouter initialEntries={['/reportes/proveedores']}>
      <AuthProvider>
        <ProviderActivityReportPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('ProviderActivityReportPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('provider_activity_report_shows_data', async () => {
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
      [`GET /api/reports/providers?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          items: [
            {
              provider_profile_id: 1,
              provider_full_name: 'Proveedor Uno',
              citas_confirmadas: 5,
              citas_canceladas: 1,
              total_citas: 6,
            },
          ],
        }),
      }),
    });

    renderPage();

    expect(await screen.findByText('Proveedor Uno')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
  });
});