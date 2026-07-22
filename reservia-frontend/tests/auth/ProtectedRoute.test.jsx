import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import ProtectedRoute from '../../src/components/ProtectedRoute';

function renderProtected(initialEntries) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route path="/admin" element={<div>Admin dashboard</div>} />
          <Route path="/client" element={<div>Client dashboard</div>} />
          <Route
            path="/protected"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <div>Protected admin content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('protected_route_redirects_unauthenticated_user_to_login', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'No autenticado' }),
    });

    renderProtected(['/protected']);

    expect(await screen.findByText('Login page')).toBeInTheDocument();
  });

  it('protected_route_redirects_wrong_role_to_own_dashboard', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        id: 3,
        email: 'cliente@example.com',
        full_name: 'Cliente Uno',
        role: 'client',
        status: 'active',
      }),
    });

    renderProtected(['/protected']);

    expect(await screen.findByText('Client dashboard')).toBeInTheDocument();
  });
});