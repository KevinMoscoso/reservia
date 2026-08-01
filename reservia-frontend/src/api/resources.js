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

export { listSalas, createSala, updateSala, deactivateSala, listEquipos, createEquipo, updateEquipo, deactivateEquipo };