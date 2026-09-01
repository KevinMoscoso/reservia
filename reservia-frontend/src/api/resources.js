import { apiFetch } from './client';

function listSalas() {
  return apiFetch('/resources/salas/');
}
function createSala(payload) {
  return apiFetch('/resources/salas/', { method: 'POST', body: JSON.stringify(payload) });
}
function updateSala(id, payload) {
  return apiFetch(`/resources/salas/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
}
function deactivateSala(id) {
  return apiFetch(`/resources/salas/${id}/deactivate`, { method: 'PATCH' });
}
function listEquipos() {
  return apiFetch('/resources/equipos/');
}
function createEquipo(payload) {
  return apiFetch('/resources/equipos/', { method: 'POST', body: JSON.stringify(payload) });
}
function updateEquipo(id, payload) {
  return apiFetch(`/resources/equipos/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
}
function deactivateEquipo(id) {
  return apiFetch(`/resources/equipos/${id}/deactivate`, { method: 'PATCH' });
}
function getSalaAvailability(id, fecha) {
  return apiFetch(`/resources/salas/${id}/availability?fecha=${fecha}`);
}
function createReservaSala(id, payload) {
  return apiFetch(`/resources/salas/${id}/reservas`, { method: 'POST', body: JSON.stringify(payload) });
}
function listMisReservasSalas(page = 1, pageSize = 20) {
  return apiFetch(`/resources/salas/reservas/me?page=${page}&page_size=${pageSize}`);
}
function cancelReservaSala(id) {
  return apiFetch(`/resources/salas/reservas/${id}/cancel`, { method: 'PATCH' });
}
function getEquipoAvailability(id, fecha) {
  return apiFetch(`/resources/equipos/${id}/availability?fecha=${fecha}`);
}
function createReservaEquipo(id, payload) {
  return apiFetch(`/resources/equipos/${id}/reservas`, { method: 'POST', body: JSON.stringify(payload) });
}
function listMisReservasEquipos(page = 1, pageSize = 20) {
  return apiFetch(`/resources/equipos/reservas/me?page=${page}&page_size=${pageSize}`);
}
function cancelReservaEquipo(id) {
  return apiFetch(`/resources/equipos/reservas/${id}/cancel`, { method: 'PATCH' });
}
function listAllReservasSalas(page = 1, pageSize = 20) {
  return apiFetch(`/resources/salas/reservas?page=${page}&page_size=${pageSize}`);
}
function listAllReservasEquipos(page = 1, pageSize = 20) {
  return apiFetch(`/resources/equipos/reservas?page=${page}&page_size=${pageSize}`);
}
function rescheduleReservaSala(id, payload) {
  return apiFetch(`/resources/salas/reservas/${id}/reschedule`, { method: 'PATCH', body: JSON.stringify(payload) });
}
function rescheduleReservaEquipo(id, payload) {
  return apiFetch(`/resources/equipos/reservas/${id}/reschedule`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export {
  listSalas,
  createSala,
  updateSala,
  deactivateSala,
  listEquipos,
  createEquipo,
  updateEquipo,
  deactivateEquipo,
  getSalaAvailability,
  createReservaSala,
  listMisReservasSalas,
  cancelReservaSala,
  getEquipoAvailability,
  createReservaEquipo,
  listMisReservasEquipos,
  cancelReservaEquipo,
  listAllReservasSalas,
  listAllReservasEquipos,
  rescheduleReservaSala,
  rescheduleReservaEquipo,
};