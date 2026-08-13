import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import SalasPage from '../../src/pages/SalasPage';

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

function renderSalasPage() {
  return render(
    <MemoryRouter initialEntries={['/admin/salas']}>
      <AuthProvider>
        <SalasPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('SalasPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('salas_page_lists_existing_salas', async () => {
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
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 1, nombre: 'Sala A', ubicacion: 'Piso 1', capacidad: 10, estado: 'active' },
        ],
      }),
    });

    renderSalasPage();

    expect(await screen.findByText('Sala A')).toBeInTheDocument();
    expect(screen.getByText('Piso 1')).toBeInTheDocument();
  });

  it('salas_page_creates_new_sala_success', async () => {
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
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
      'POST /api/resources/salas/': () => ({
        ok: true,
        status: 201,
        json: async () => ({
          id: 2,
          nombre: 'Sala Nueva',
          ubicacion: 'Piso 2',
          capacidad: 5,
          estado: 'active',
        }),
      }),
    });

    const user = userEvent.setup();
    renderSalasPage();

    await screen.findByRole('button', { name: /crear sala/i });

    await user.type(screen.getByLabelText(/nombre/i), 'Sala Nueva');
    await user.type(screen.getByLabelText(/ubicación/i), 'Piso 2');
    await user.type(screen.getByLabelText(/capacidad/i), '5');
    await user.click(screen.getByRole('button', { name: /crear sala/i }));

    expect(await screen.findByText('Sala Nueva')).toBeInTheDocument();
  });

  it('salas_page_blocks_invalid_capacity_before_api_call', async () => {
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
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    });

    const user = userEvent.setup();
    renderSalasPage();

    await screen.findByRole('button', { name: /crear sala/i });

    await user.type(screen.getByLabelText(/nombre/i), 'Sala Invalida');
    await user.type(screen.getByLabelText(/ubicación/i), 'Piso 3');
    await user.type(screen.getByLabelText(/capacidad/i), '0');
    await user.click(screen.getByRole('button', { name: /crear sala/i }));

    expect(
      await screen.findByText(/la capacidad debe ser un número entero mayor a 0/i)
    ).toBeInTheDocument();

    expect(fetch).not.toHaveBeenCalledWith(
      '/api/resources/salas/',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('salas_page_deactivates_sala_success', async () => {
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
      'GET /api/resources/salas/': () => ({
        ok: true,
        status: 200,
        json: async () => [
          { id: 3, nombre: 'Sala B', ubicacion: 'Piso 4', capacidad: 8, estado: 'active' },
        ],
      }),
      'PATCH /api/resources/salas/3/deactivate': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          id: 3,
          nombre: 'Sala B',
          ubicacion: 'Piso 4',
          capacidad: 8,
          estado: 'inactive',
        }),
      }),
    });

    const user = userEvent.setup();
    renderSalasPage();

    await screen.findByText('Sala B');
    await user.click(screen.getByRole('button', { name: /desactivar/i }));

    expect(await screen.findByText('inactive')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /desactivar/i })).not.toBeInTheDocument();
  });
});