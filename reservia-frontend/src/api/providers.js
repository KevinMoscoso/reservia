import { apiFetch } from './client';

function getMyProfile() {
  return apiFetch('/providers/me/profile');
}
function updateMyProfile(payload) {
  return apiFetch('/providers/me/profile', { method: 'PUT', body: JSON.stringify(payload) });
}
function getMySchedule() {
  return apiFetch('/providers/me/schedule');
}
function addScheduleBlock(payload) {
  return apiFetch('/providers/me/schedule', { method: 'POST', body: JSON.stringify(payload) });
}
function deactivateScheduleBlock(id) {
  return apiFetch(`/providers/me/schedule/${id}/deactivate`, { method: 'PATCH' });
}
function listProviders() {
  return apiFetch('/providers/');
}
function getProviderAvailability(id, fecha) {
  return apiFetch(`/providers/${id}/availability?fecha=${fecha}`);
}
function createCita(id, payload) {
  return apiFetch(`/providers/${id}/citas`, { method: 'POST', body: JSON.stringify(payload) });
}
function listMisCitas(page = 1, pageSize = 20) {
  return apiFetch(`/providers/citas/me?page=${page}&page_size=${pageSize}`);
}
function cancelCita(id) {
  return apiFetch(`/providers/citas/${id}/cancel`, { method: 'PATCH' });
}
function listAllCitas(page = 1, pageSize = 20) {
  return apiFetch(`/providers/citas?page=${page}&page_size=${pageSize}`);
}
function getMyDateBlocks() {
  return apiFetch('/providers/me/date-blocks');
}
function addDateBlock(payload) {
  return apiFetch('/providers/me/date-blocks', { method: 'POST', body: JSON.stringify(payload) });
}
function deactivateDateBlock(id) {
  return apiFetch(`/providers/me/date-blocks/${id}/deactivate`, { method: 'PATCH' });
}

export {
  getMyProfile,
  updateMyProfile,
  getMySchedule,
  addScheduleBlock,
  deactivateScheduleBlock,
  listProviders,
  getProviderAvailability,
  createCita,
  listMisCitas,
  cancelCita,
  listAllCitas,
  getMyDateBlocks,
  addDateBlock,
  deactivateDateBlock,
};