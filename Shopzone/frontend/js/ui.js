/* Shared UI: navbar, footer, toasts, reveals, formatting, card helpers, product renderer. */

const CAT_EMOJI = {
  Electronics: '📱', Computers: '💻', Fashion: '👗', Furniture: '🛋️', Groceries: '🛒',
  Makeup: '💄', Perfumes: '🌸', 'Face Wash': '🧼', Home: '🏠', Kitchen: '🍳',
  Sports: '⚽', Books: '📚', Toys: '🧸',
};

const inr = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

function toast(message, type = 'ok') {
  let zone = document.querySelector('.toast-zone');
  if (!zone) {
    zone = document.createElement('div');
    zone.className = 'toast-zone';
    document.body.appendChild(zone);
  }
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = message;
  zone.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    el.style.transition = 'all .3s';
    setTimeout(() => el.remove(), 320);
  }, 2600);
}

/* ---- card helpers (same logic as backend, for live UX only) ---- */
function luhnOk(num) {
  let total = 0;
  const rev = num.split('').reverse();
  for (let i = 0; i < rev.length; i++) {
    let n = parseInt(rev[i], 10);
    if (i % 2 === 1) { n *= 2; if (n > 9) n -= 9; }
    total += n;
  }
  return num.length > 0 && total % 10 === 0;
}
function cardTypeOf(num) {
  if (num.startsWith('4')) return 'Visa';
  if (num.startsWith('5')) return 'MasterCard';
  if (num.startsWith('6')) return 'RuPay';
  if (num.startsWith('34') || num.startsWith('37')) return 'American Express';
  return '';
}

/* ---- navbar / footer ---- */
/* ---- theme (dark default, persisted) ---- */
const THEME_KEY = 'sz_theme';
const SUN_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';
const MOON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
function getTheme() {
  try { return localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'; }
  catch { return 'dark'; }
}
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', t === 'light' ? '#f5f7fb' : '#0b1120');
  document.querySelectorAll('.theme-toggle').forEach((b) => {
    b.innerHTML = t === 'light' ? MOON_SVG : SUN_SVG;
    b.title = t === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
    b.setAttribute('aria-label', b.title);
  });
}
function setTheme(t) {
  try { localStorage.setItem(THEME_KEY, t); } catch { /* private mode */ }
  applyTheme(t);
}
function toggleTheme() { setTheme(getTheme() === 'light' ? 'dark' : 'light'); }

function mountNav(active) {
  document.querySelector('header.nav')?.remove();
  const nav = document.createElement('header');
  nav.className = 'nav';
  const user = Auth.user;
  const links = [
    ['/', 'Home', 'home'],
    ['/shop', 'Shop', 'shop'],
    ...(user && user.role === 'user' ? [['/wishlist', 'Wishlist', 'wishlist'], ['/orders', 'My Orders', 'orders']] : []),
    ...(user && user.role === 'admin' ? [['/admin', 'Admin Desk', 'admin']] : []),
  ];
  nav.innerHTML = `
    <div class="nav-in">
      <a class="brand" href="/">
        <span class="bag">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        </span>
        Shop<em>Zone</em>
      </a>
      <nav class="nav-links">
        ${links.map(([href, label, key]) => `<a href="${href}" class="${key === active ? 'active' : ''}">${label}</a>`).join('')}
      </nav>
      <div class="nav-right">
        ${active === 'home' ? '' : `<a class="cart-btn" href="/cart" aria-label="Cart">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
          Cart <span class="cart-count">0</span>
        </a>`}
        <button class="theme-toggle" id="themeBtn" type="button"></button>
        ${user
          ? `<a class="user-chip" href="${user.role === 'user' ? '/profile' : '/admin'}" title="Profile & settings">
               ${user.profile_image
                 ? `<img class="avatar" src="${user.profile_image}" alt="">`
                 : `<span class="avatar ini">${escapeHtml((user.name || user.email || '?').trim().charAt(0).toUpperCase())}</span>`}
               <b>${escapeHtml(user.name || user.email)}</b>
             </a>
             <button class="btn btn-ghost btn-sm" id="logoutBtn">Log out</button>`
          : `<a class="btn btn-ghost btn-sm" href="/login">Sign in</a>
             <a class="btn btn-primary btn-sm" href="/register">Register</a>`}
      </div>
    </div>`;
  document.body.prepend(nav);
  const tb = document.getElementById('themeBtn');
  if (tb) tb.onclick = toggleTheme;
  applyTheme(getTheme());
  const lb = document.getElementById('logoutBtn');
  if (lb) lb.onclick = () => { Auth.clear(); Cart.clear(); location.href = '/'; };
  renderCartCount();
}

function renderCartCount() {
  document.querySelectorAll('.cart-count').forEach((el) => { el.textContent = String(Cart.count()); });
}

function mountThemeFab() {
  const b = document.createElement('button');
  b.className = 'theme-toggle';
  b.type = 'button';
  b.style.cssText = 'position:fixed;top:16px;right:16px;z-index:80;width:40px;height:40px;box-shadow:var(--shadow-soft)';
  document.body.appendChild(b);
  b.onclick = toggleTheme;
  applyTheme(getTheme());
}

function mountFooter() {
  const f = document.createElement('footer');
  f.className = 'footer';
  f.innerHTML = `
    <div class="footer-in">
      <span>© 2026 ShopZone · Secure e-commerce with ML fraud detection</span>
      <span>RandomForest · Luhn · bcrypt · FastAPI</span>
    </div>`;
  document.body.appendChild(f);
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* ---- scroll reveal ---- */
function initReveal() {
  const els = document.querySelectorAll('[data-reveal]:not(.in)');
  if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      // isIntersecting = in view now; top < 0 = already scrolled past (jump-scroll safe)
      if (en.isIntersecting || en.boundingClientRect.top < 0) {
        en.target.classList.add('in'); io.unobserve(en.target);
      }
    });
  }, { threshold: 0.05 });
  els.forEach((e) => io.observe(e));
}

/* ---- product card ---- */
function productCard(p, revealIdx) {
  const emoji = CAT_EMOJI[p.category] || '🛍️';
  const d = revealIdx != null ? ` data-reveal data-d="${Math.min(4, revealIdx % 4 + 1)}"` : '';
  const badge = p.badge === 'sale' ? '<span class="badge sale">Sale</span>'
    : p.badge === 'new' ? '<span class="badge new">New</span>' : '';
  const old = p.old_price && p.old_price > p.price ? `<small>${inr(p.old_price)}</small>` : '';
  return `
  <article class="card"${d}>
    <div class="card-img">
      ${badge}
      <button class="wish-btn" data-wish="${p.id}" type="button" title="Save to wishlist" aria-label="Save to wishlist">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
      </button>
      <div class="ph">${emoji}</div>
      <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" loading="lazy"
           onload="this.previousElementSibling.style.display='none'" onerror="this.remove()">
    </div>
    <div class="card-body">
      <span class="card-cat">${escapeHtml(p.category)}</span>
      <b class="card-name">${escapeHtml(p.name)}</b>
      <span class="card-desc">${escapeHtml(p.desc)}</span>
      <span class="card-rate">★ ${escapeHtml(p.rating)}</span>
      <div class="card-foot">
        <span class="price">${inr(p.price)}${old}</span>
        <button class="add-btn" data-add="${p.id}">Add +</button>
      </div>
    </div>
  </article>`;
}

function bindAddButtons(root) {
  root.querySelectorAll('[data-add]').forEach((btn) => {
    btn.onclick = () => {
      Cart.add(Number(btn.dataset.add));
      const p = productById(Number(btn.dataset.add));
      toast(`Added to cart: ${p ? p.name : 'item'}`, 'ok');
    };
  });
}

function bindWishButtons(root, wishSet) {
  const set = wishSet || new Set();
  const sync = () => root.querySelectorAll('[data-wish]').forEach((b) => {
    b.classList.toggle('on', set.has(Number(b.dataset.wish)));
  });
  sync();
  root.querySelectorAll('[data-wish]').forEach((btn) => {
    btn.onclick = async (e) => {
      e.preventDefault(); e.stopPropagation();
      const id = Number(btn.dataset.wish);
      if (!Auth.user || Auth.user.role !== 'user') {
        toast('Sign in to save favourites', 'err');
        setTimeout(() => { location.href = '/login?next=' + encodeURIComponent(location.pathname); }, 900);
        return;
      }
      const p = productById(id);
      try {
        if (set.has(id)) {
          await API.del('/me/wishlist/' + id);
          set.delete(id);
          if (root.dataset.unwishRemove) btn.closest('.card')?.remove();
          toast(`Removed from wishlist: ${p ? p.name : 'item'}`);
        } else {
          await API.post('/me/wishlist', { product_id: id });
          set.add(id);
          toast(`Saved to wishlist: ${p ? p.name : 'item'} ❤`, 'ok');
        }
        sync();
      } catch (err) { toast(err.message, 'err'); }
    };
  });
  return set;
}

async function loadWishSet() {
  if (!Auth.user || Auth.user.role !== 'user') return new Set();
  try {
    const d = await API.get('/me/wishlist');
    return new Set(d.items.map((i) => i.id));
  } catch { return new Set(); }
}

/* ---- validation rules (mirror backend policy) ---- */
function emailSuffixOk(v) {
  const at = v.lastIndexOf('@');
  if (at < 0) return false;
  return /\.(com|in|org)$/i.test(v.slice(at + 1));
}
function inPhoneOk(v) { return /^[6-9]\d{9}$/.test(v.replace(/\D/g, '').replace(/^91/, '')); }
function pwRules(pw) {
  return [
    { label: 'At least 8 characters', ok: pw.length >= 8 },
    { label: 'An uppercase letter (A–Z)', ok: /[A-Z]/.test(pw) },
    { label: 'A lowercase letter (a–z)', ok: /[a-z]/.test(pw) },
    { label: 'A number (0–9)', ok: /\d/.test(pw) },
    { label: 'A special character (!@#…)', ok: /[^A-Za-z0-9]/.test(pw) },
  ];
}
function pwOk(pw) { return pwRules(pw).every((r) => r.ok); }
function renderPwChecklist(host, pw) {
  host.innerHTML = pwRules(pw).map((r) =>
    `<span class="pw-rule ${r.ok ? 'ok' : ''}">${r.ok ? '✓' : '○'} ${r.label}</span>`).join('');
}
function bindEye(input, btn) {
  btn.onclick = () => {
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.classList.toggle('seeing', show);
    btn.innerHTML = show ? EYE_OFF_SVG : EYE_SVG;
    btn.title = show ? 'Hide password' : 'Show password';
  };
}
const EYE_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYE_OFF_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.4 10.4 0 0 1 12 5c6.5 0 10 7 10 7a13.2 13.2 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.5 13.5 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>';

/* ---- guards ---- */
function requireAuth() {
  if (!Auth.isLogged) {
    location.href = '/login?next=' + encodeURIComponent(location.pathname);
    return false;
  }
  return true;
}
function requireAdmin() {
  if (!Auth.isLogged) { location.href = '/login?next=' + encodeURIComponent(location.pathname); return false; }
  if (!Auth.isAdmin) { location.href = '/'; toast('Admin desk only', 'err'); return false; }
  return true;
}
