import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import LoginPage from '../../src/pages/LoginPage';

function renderLoginPage(initialEntries = ['/login']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/admin" element={<div>Admin dashboard</div>} />
          <Route path="/provider" element={<div>Provider dashboard</div>} />
          <Route path="/client" element={<div>Client dashboard</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('login_page_renders_email_and_password_fields', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'No autenticado' }),
    });

    renderLoginPage();

    expect(await screen.findByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it('login_success_redirects_to_role_dashboard', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'No autenticado' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          id: 1,
          email: 'admin@example.com',
          full_name: 'Admin Uno',
          role: 'admin',
          status: 'active',
        }),
      });

    const user = userEvent.setup();
    renderLoginPage();

    await screen.findByLabelText(/email/i);
    await user.type(screen.getByLabelText(/email/i), 'admin@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'Secret123');
    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(await screen.findByText('Admin dashboard')).toBeInTheDocument();
  });

  it('login_shows_api_error_message_on_invalid_credentials', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'No autenticado' }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Credenciales inválidas' }),
      });

    const user = userEvent.setup();
    renderLoginPage();

    await screen.findByLabelText(/email/i);
    await user.type(screen.getByLabelText(/email/i), 'wrong@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'WrongPass1');
    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(await screen.findByText('Credenciales inválidas')).toBeInTheDocument();
  });

  it('login_shows_api_error_message_on_account_locked', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'No autenticado' }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 423,
        json: async () => ({ detail: 'Cuenta bloqueada temporalmente' }),
      });

    const user = userEvent.setup();
    renderLoginPage();

    await screen.findByLabelText(/email/i);
    await user.type(screen.getByLabelText(/email/i), 'locked@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'Secret123');
    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(
      await screen.findByText('Cuenta bloqueada temporalmente')
    ).toBeInTheDocument();
  });
});