import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../src/context/AuthContext';
import RegisterPage from '../../src/pages/RegisterPage';
import LoginPage from '../../src/pages/LoginPage';

function renderRegisterPage() {
  return render(
    <MemoryRouter initialEntries={['/register']}>
      <AuthProvider>
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('RegisterPage', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('register_success_redirects_to_login_with_message', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'No autenticado' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          id: 2,
          email: 'nuevo@example.com',
          full_name: 'Nuevo Cliente',
          role: 'client',
          status: 'active',
        }),
      });

    const user = userEvent.setup();
    renderRegisterPage();

    await user.type(screen.getByLabelText(/nombre completo/i), 'Nuevo Cliente');
    await user.type(screen.getByLabelText(/email/i), 'nuevo@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'Secret123');
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(
      await screen.findByText('Registro exitoso. Ahora inicia sesión.')
    ).toBeInTheDocument();
  });

  it('register_shows_duplicate_email_error_from_api', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'No autenticado' }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({ detail: 'email ya registrado' }),
      });

    const user = userEvent.setup();
    renderRegisterPage();

    await user.type(screen.getByLabelText(/nombre completo/i), 'Cliente Repetido');
    await user.type(screen.getByLabelText(/email/i), 'repetido@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'Secret123');
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(await screen.findByText('email ya registrado')).toBeInTheDocument();
  });

  it('register_blocks_weak_password_before_calling_api', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'No autenticado' }),
    });

    const user = userEvent.setup();
    renderRegisterPage();

    await user.type(screen.getByLabelText(/nombre completo/i), 'Cliente Debil');
    await user.type(screen.getByLabelText(/email/i), 'debil@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), '1234567');
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(
      await screen.findByText(/al menos 8 caracteres y un dígito/i)
    ).toBeInTheDocument();

    expect(fetch).toHaveBeenCalledTimes(1);
  });
});