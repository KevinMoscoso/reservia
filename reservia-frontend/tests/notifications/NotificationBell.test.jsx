import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import NotificationBell from '../../src/components/NotificationBell';

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

describe('NotificationBell', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('notification_bell_shows_unread_count', async () => {
    mockFetchRoutes({
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 3 }),
      }),
    });

    render(<NotificationBell />);

    expect(await screen.findByText('3')).toBeInTheDocument();
  });

  it('notification_bell_lists_notifications_on_open', async () => {
    mockFetchRoutes({
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 1 }),
      }),
      'GET /api/notifications/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 1,
              tipo: 'reserva_confirmada',
              mensaje: 'Tu reserva fue confirmada.',
              entity_type: 'reserva_sala',
              entity_id: 10,
              leida: false,
              created_at: '2026-08-06T10:00:00',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
    });

    const user = userEvent.setup();
    render(<NotificationBell />);

    await user.click(screen.getByLabelText(/notificaciones/i));

    expect(await screen.findByText('Tu reserva fue confirmada.')).toBeInTheDocument();
  });

  it('notification_bell_marks_notification_as_read', async () => {
    mockFetchRoutes({
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 1 }),
      }),
      'GET /api/notifications/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 1,
              tipo: 'reserva_confirmada',
              mensaje: 'Tu reserva fue confirmada.',
              entity_type: 'reserva_sala',
              entity_id: 10,
              leida: false,
              created_at: '2026-08-06T10:00:00',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
      'PATCH /api/notifications/1/read': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          id: 1,
          tipo: 'reserva_confirmada',
          mensaje: 'Tu reserva fue confirmada.',
          entity_type: 'reserva_sala',
          entity_id: 10,
          leida: true,
          created_at: '2026-08-06T10:00:00',
        }),
      }),
    });

    const user = userEvent.setup();
    render(<NotificationBell />);

    await user.click(screen.getByLabelText(/notificaciones/i));
    await screen.findByText('Tu reserva fue confirmada.');

    await user.click(screen.getByText('Tu reserva fue confirmada.'));

    expect(screen.queryByText('1')).not.toBeInTheDocument();
  });

  it('notification_bell_uses_items_from_paginated_response', async () => {
    mockFetchRoutes({
      'GET /api/notifications/me/unread-count': () => ({
        ok: true,
        status: 200,
        json: async () => ({ count: 2 }),
      }),
      'GET /api/notifications/me?page=1&page_size=20': () => ({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: 5,
              tipo: 'cita_confirmada',
              mensaje: 'Tu cita fue confirmada por el proveedor.',
              entity_type: 'cita',
              entity_id: 40,
              leida: false,
              created_at: '2026-08-15T08:00:00',
            },
          ],
          total: 12,
          page: 1,
          page_size: 20,
          total_pages: 1,
        }),
      }),
    });

    const user = userEvent.setup();
    render(<NotificationBell />);

    await user.click(screen.getByLabelText(/notificaciones/i));

    expect(
      await screen.findByText('Tu cita fue confirmada por el proveedor.')
    ).toBeInTheDocument();
  });
});