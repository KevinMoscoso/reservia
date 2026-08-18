import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import OccupancyReportPage from '../../src/pages/OccupancyReportPage';
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
    <MemoryRouter initialEntries={['/admin/reportes/ocupacion']}>
      <AuthProvider>
        <OccupancyReportPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('OccupancyReportPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('occupancy_report_shows_resource_data', async () => {
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
      [`GET /api/reports/occupancy?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          items: [
            {
              resource_type: 'sala',
              resource_id: 1,
              resource_nombre: 'Sala Reportes',
              reservas_confirmadas: 3,
              bloques_reservados: 6,
              bloques_disponibles: 28,
              porcentaje_ocupacion: 21.43,
            },
          ],
        }),
      }),
    });

    renderPage();

    expect(await screen.findByText('Sala Reportes')).toBeInTheDocument();
    expect(screen.getByText('21.43%')).toBeInTheDocument();
  });

  it('occupancy_report_export_button_calls_correct_endpoint', async () => {
    const { fechaInicio, fechaFin } = defaultDateRange();

    window.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    window.URL.revokeObjectURL = vi.fn();

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
      [`GET /api/reports/occupancy?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({ fecha_inicio: fechaInicio, fecha_fin: fechaFin, items: [] }),
      }),
      [`GET /api/reports/occupancy?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&format=csv`]: () => ({
        ok: true,
        status: 200,
        blob: async () => new Blob(['csv data'], { type: 'text/csv' }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await screen.findByRole('button', { name: /exportar csv/i });
    await user.click(screen.getByRole('button', { name: /exportar csv/i }));

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=csv'),
      expect.any(Object)
    );
  });
});