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
function listMisReservasSalas() {
  return apiFetch('/resources/salas/reservas/me');
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
function listMisReservasEquipos() {
  return apiFetch('/resources/equipos/reservas/me');
}
function cancelReservaEquipo(id) {
  return apiFetch(`/resources/equipos/reservas/${id}/cancel`, { method: 'PATCH' });
}
function listAllReservasSalas() {
  return apiFetch('/resources/salas/reservas');
}
function listAllReservasEquipos() {
  return apiFetch('/resources/equipos/reservas');
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
};