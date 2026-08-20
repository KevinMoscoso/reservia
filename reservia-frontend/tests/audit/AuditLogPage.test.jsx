import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import AuditLogPage from '../../src/pages/AuditLogPage';
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
    <MemoryRouter initialEntries={['/admin/auditoria']}>
      <AuthProvider>
        <AuditLogPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('AuditLogPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('audit_log_page_shows_entries', async () => {
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
      [`GET /api/audit/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&page=1&page_size=20`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 1,
              actor_user_id: 5,
              actor_full_name: 'Admin Uno',
              action: 'system.bootstrap_completed',
              entity_type: 'user',
              entity_id: 5,
              metadata: null,
              created_at: '2026-08-10T09:00:00',
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

    expect(await screen.findByText('Admin Uno')).toBeInTheDocument();
    expect(screen.getByText('system.bootstrap_completed')).toBeInTheDocument();
    expect(screen.getByText('user #5')).toBeInTheDocument();
  });

  it('audit_log_pagination_next_button_fetches_next_page', async () => {
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
      [`GET /api/audit/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&page=1&page_size=20`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 1,
              actor_user_id: 5,
              actor_full_name: 'Admin Uno',
              action: 'system.bootstrap_completed',
              entity_type: 'user',
              entity_id: 5,
              metadata: null,
              created_at: '2026-08-10T09:00:00',
            },
          ],
          total: 21,
          page: 1,
          page_size: 20,
          total_pages: 2,
        }),
      }),
      [`GET /api/audit/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&page=2&page_size=20`]: () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 21,
              actor_user_id: null,
              actor_full_name: null,
              action: 'user.login_failed',
              entity_type: 'user',
              entity_id: null,
              metadata: null,
              created_at: '2026-08-10T10:00:00',
            },
          ],
          total: 21,
          page: 2,
          page_size: 20,
          total_pages: 2,
        }),
      }),
    });

    const user = userEvent.setup();
    renderPage();

    await screen.findByText('Admin Uno');
    await user.click(screen.getByRole('button', { name: /siguiente/i }));

    expect(
      fetch.mock.calls.some(([url]) =>
        typeof url === 'string' && url.includes('page=2')
      )
    ).toBe(true);
  });
});