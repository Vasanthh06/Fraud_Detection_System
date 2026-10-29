/* ShopZone API client — same-origin /api, Bearer token in localStorage. */
const SZ_TOKEN_KEY = 'sz_token';
const SZ_USER_KEY = 'sz_user';

const Auth = {
  get token() { return localStorage.getItem(SZ_TOKEN_KEY) || ''; },
  get user() {
    try { return JSON.parse(localStorage.getItem(SZ_USER_KEY) || 'null'); }
    catch { return null; }
  },
  save(token, user) {
    localStorage.setItem(SZ_TOKEN_KEY, token);
    localStorage.setItem(SZ_USER_KEY, JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem(SZ_TOKEN_KEY);
    localStorage.removeItem(SZ_USER_KEY);
  },
  update(user) { localStorage.setItem(SZ_USER_KEY, JSON.stringify(user)); },
  get isAdmin() { return this.user?.role === 'admin'; },
  get isLogged() { return !!this.token && !!this.user; },
};

async function api(method, path, body, silent = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (Auth.token) headers['Authorization'] = 'Bearer ' + Auth.token;
  const res = await fetch('/api' + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch { /* empty */ }
  if (!res.ok) {
    const detail = (data && data.detail) || `Request failed (${res.status})`;
    const message = typeof detail === 'string' ? detail : 'Request failed';
    if (res.status === 401 && !silent) {
      Auth.clear();
      if (!location.pathname.endsWith('login.html') && location.pathname !== '/login') {
        location.href = '/login?next=' + encodeURIComponent(location.pathname);
        throw new Error(message);
      }
    }
    throw new Error(message);
  }
  return data;
}

const API = {
  get: (p, silent) => api('GET', p, null, silent),
  post: (p, b, silent) => api('POST', p, b, silent),
  put: (p, b, silent) => api('PUT', p, b, silent),
  del: (p, silent) => api('DELETE', p, null, silent),
};
