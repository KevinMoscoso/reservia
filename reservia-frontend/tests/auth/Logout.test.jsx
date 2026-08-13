import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import Layout from '../../src/components/Layout';

const CLIENT_USER = {
  id: 7,
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

function renderWithLayout() {
  return render(
    <MemoryRouter initialEntries={['/client']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route
            path="/client"
            element={
              <Layout>
                <div>Client content</div>
              </Layout>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Logout', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('logout_calls_api_and_redirects_to_login', async () => {
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
      'POST /api/auth/logout': () => ({
        ok: true,
        status: 200,
        json: async () => ({ detail: 'logout ok' }),
      }),
    });

    const user = userEvent.setup();
    renderWithLayout();

    await screen.findByText('Client content');
    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }));

    expect(await screen.findByText('Login page')).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith(
      '/api/auth/logout',
      expect.objectContaining({ method: 'POST' })
    );
  });
});