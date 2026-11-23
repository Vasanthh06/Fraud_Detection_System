/* Cart store — localStorage lines {id, qty}; prices always come from the server catalog. */
const SZ_CART_KEY = 'sz_cart';
const SZ_CATALOG_KEY = 'sz_catalog';

const Cart = {
  lines() {
    try { return JSON.parse(localStorage.getItem(SZ_CART_KEY) || '[]'); }
    catch { return []; }
  },
  save(lines) {
    localStorage.setItem(SZ_CART_KEY, JSON.stringify(lines));
    if (typeof renderCartCount === 'function') renderCartCount();
  },
  add(id, qty = 1) {
    const lines = this.lines();
    const line = lines.find((l) => l.id === id);
    if (line) line.qty = Math.min(20, line.qty + qty);
    else lines.push({ id, qty });
    this.save(lines);
  },
  setQty(id, qty) {
    let lines = this.lines();
    if (qty <= 0) lines = lines.filter((l) => l.id !== id);
    else lines = lines.map((l) => (l.id === id ? { ...l, qty: Math.min(20, qty) } : l));
    this.save(lines);
  },
  remove(id) { this.setQty(id, 0); },
  clear() { this.save([]); },
  count() { return this.lines().reduce((n, l) => n + l.qty, 0); },
};

let SZ_CATALOG = null;
async function catalog() {
  if (SZ_CATALOG) return SZ_CATALOG;
  try {
    const cached = sessionStorage.getItem(SZ_CATALOG_KEY);
    if (cached) { SZ_CATALOG = JSON.parse(cached); return SZ_CATALOG; }
  } catch { /* ignore */ }
  const data = await API.get('/products');
  SZ_CATALOG = data.products;
  try { sessionStorage.setItem(SZ_CATALOG_KEY, JSON.stringify(SZ_CATALOG)); } catch { /* ignore */ }
  return SZ_CATALOG;
}

function productById(id, list) { return (list || SZ_CATALOG || []).find((p) => p.id === id); }

function cartTotal(list) {
  return Cart.lines().reduce((sum, l) => {
    const p = productById(l.id, list);
    return sum + (p ? p.price * l.qty : 0);
  }, 0);
}
