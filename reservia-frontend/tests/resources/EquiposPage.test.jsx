import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import EquiposPage from '../../src/pages/EquiposPage';

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

function renderEquiposPage() {
  return render(
    <MemoryRouter initialEntries={['/admin/equipos']}>
      <AuthProvider>
        <EquiposPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('EquiposPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('equipos_page_lists_existing_equipos', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/resources/equipos/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Proyector', codigo: 'EQ-001', categoria: 'AV', estado: 'active' },
        ],
      }),
    });

    renderEquiposPage();

    expect(await screen.findByText('Proyector')).toBeInTheDocument();
    expect(screen.getByText('EQ-001')).toBeInTheDocument();
  });

  it('equipos_page_creates_new_equipo_success', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/resources/equipos/': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'POST /api/resources/equipos/': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 2,
          nombre: 'Laptop',
          codigo: 'EQ-002',
          categoria: 'Computo',
          estado: 'active',
        }),
      }),
    });

    const user = userEvent.setup();
    renderEquiposPage();

    await screen.findByRole('button', { name: /crear equipo/i });

    await user.type(screen.getByLabelText(/nombre/i), 'Laptop');
    await user.type(screen.getByLabelText(/código/i), 'EQ-002');
    await user.type(screen.getByLabelText(/categoría/i), 'Computo');
    await user.click(screen.getByRole('button', { name: /crear equipo/i }));

    expect(await screen.findByText('Laptop')).toBeInTheDocument();
  });

  it('equipos_page_shows_duplicate_codigo_error_from_api', async () => {
    mockFetchRoutes({
      'GET /api/auth/me': () => ({
        ok: true,
        status: 200,
        json: async () => ADMIN_USER,
      }),
      'GET /api/resources/equipos/': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'POST /api/resources/equipos/': () => ({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'codigo ya registrado' }),
      }),
    });

    const user = userEvent.setup();
    renderEquiposPage();

    await screen.findByRole('button', { name: /crear equipo/i });

    await user.type(screen.getByLabelText(/nombre/i), 'Laptop Duplicada');
    await user.type(screen.getByLabelText(/código/i), 'EQ-DUP');
    await user.type(screen.getByLabelText(/categoría/i), 'Computo');
    await user.click(screen.getByRole('button', { name: /crear equipo/i }));

    expect(await screen.findByText('codigo ya registrado')).toBeInTheDocument();
  });
});