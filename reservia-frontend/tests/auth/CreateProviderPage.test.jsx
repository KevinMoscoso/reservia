import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import CreateProviderPage from '../../src/pages/CreateProviderPage';

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

function renderCreateProviderPage() {
  return render(
    <MemoryRouter initialEntries={['/admin/providers/new']}>
      <AuthProvider>
        <CreateProviderPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('CreateProviderPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('create_provider_shows_success_confirmation', async () => {
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
      'POST /api/admin/providers': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 6,
          email: 'proveedor@example.com',
          full_name: 'Proveedor Uno',
          role: 'provider',
          status: 'active',
        }),
      }),
    });

    const user = userEvent.setup();
    renderCreateProviderPage();

    await user.type(screen.getByLabelText(/nombre completo/i), 'Proveedor Uno');
    await user.type(screen.getByLabelText(/email/i), 'proveedor@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'Secret123');
    await user.click(screen.getByRole('button', { name: /crear proveedor/i }));

    expect(
      await screen.findByText('Proveedor creado exitosamente')
    ).toBeInTheDocument();
  });
});