import { apiFetch } from './client';

function listMyNotifications(page = 1, pageSize = 20) {
  return apiFetch(`/notifications/me?page=${page}&page_size=${pageSize}`);
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