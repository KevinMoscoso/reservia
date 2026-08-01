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

export { getMyProfile, updateMyProfile, getMySchedule, addScheduleBlock, deactivateScheduleBlock };