const API_BASE = '/api';

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return data;
}

function extractErrorMessage(data) {
  if (!data || data.detail === undefined) {
    return 'Error inesperado. Intenta nuevamente.';
  }
  if (typeof data.detail === 'string') {
    return data.detail;
  }
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg).join(' ');
  }
  return 'Error inesperado. Intenta nuevamente.';
}

export { apiFetch };