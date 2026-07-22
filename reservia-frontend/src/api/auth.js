import { apiFetch } from './client';

function registerClient(payload) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

function setupAdmin(payload) {
  return apiFetch('/auth/setup', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

function login(payload) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

function logout() {
  return apiFetch('/auth/logout', {
    method: 'POST',
  });
}

function getMe() {
  return apiFetch('/auth/me', {
    method: 'GET',
  });
}

function createProvider(payload) {
  return apiFetch('/admin/providers', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export { registerClient, setupAdmin, login, logout, getMe, createProvider };