const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('merkato_token');
  const headers = { ...(options.body instanceof FormData ? {} : {'Content-Type': 'application/json'}), ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE_URL}${path}`, {...options, headers});
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!response.ok) throw new Error(data?.detail || data?.message || 'Request failed');
  return data;
}

async function apiUpload(file) {
  const form = new FormData();
  form.append('file', file);
  return apiFetch('/api/upload', { method: 'POST', body: form });
}

export { API_BASE_URL, apiFetch, apiUpload };
