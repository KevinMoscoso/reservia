import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from '../../src/context/AuthContext';

function Probe() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  return <div>{user ? `Usuario: ${user.full_name}` : 'Sin usuario'}</div>;
}

describe('AuthContext', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('auth_context_loads_current_user_on_mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        id: 4,
        email: 'actual@example.com',
        full_name: 'Usuario Actual',
        role: 'provider',
        status: 'active',
      }),
    });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );

    expect(await screen.findByText('Usuario: Usuario Actual')).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      '/api/auth/me',
      expect.objectContaining({ credentials: 'include' })
    );
  });
});