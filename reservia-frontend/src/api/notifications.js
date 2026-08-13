import { apiFetch } from './client';

function listMyNotifications() {
  return apiFetch('/notifications/me');
}
function getUnreadCount() {
  return apiFetch('/notifications/me/unread-count');
}
function markAsRead(id) {
  return apiFetch(`/notifications/${id}/read`, { method: 'PATCH' });
}
function markAllAsRead() {
  return apiFetch('/notifications/me/read-all', { method: 'PATCH' });
}

export { listMyNotifications, getUnreadCount, markAsRead, markAllAsRead };