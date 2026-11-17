# 🛍️ ShopZone — Secure E‑Commerce Store with Real‑Time Fraud Detection

**ShopZone** is a complete, professional e‑commerce web application whose payment gateway is
protected by a real‑time **credit / debit card fraud detection engine** (rule‑based scoring +
a trained **RandomForest** machine‑learning model). Every payment attempt — approved, flagged
or blocked — is scored, explained and logged to an auditable SQLite database, and an
administrator desk visualises the full risk picture live.

This project is a **full professional rebuild** of the original *Fraud_Detection_System*
(Streamlit-based). The fraud-detection **dataset, models and algorithms are identical** to the
original — only the presentation layer was rebuilt:

| Original (Streamlit)                     | ShopZone (this rebuild)                                   |
| ---------------------------------------- | --------------------------------------------------------- |
| Streamlit multi-page UI + Streamlit "API" | **FastAPI** REST API + hand-crafted HTML/CSS/JS storefront |
| OTP / email sending in forgot-password    | **Removed** — direct email-or-phone password reset (no OTP, no external SMS/email service) |
| Session-state auth                        | **JWT (HS256, 12 h)** + **bcrypt** password hashing        |
| `streamlit run app.py`                    | `uvicorn app.main:app` — **one port serves API + website** |
| Dataset, ML models, rule weights, thresholds | **Unchanged — ported 1:1**                              |

---

## ✨ Features

**Storefront**
- **Light / dark theme toggle** — persisted per browser, one-click switch in the navbar (floating toggle on auth pages)
- Animated landing page (pure CSS/SVG — drifting gradients, floating product tiles, live risk meter)
- Curated **Shop by category** showcase on the landing page, deep-linking into the catalog (`/shop?cat=…`)
- 117-product catalog across 13 categories with search, category chips and sorting
- Persistent shopping cart (localStorage; prices always recomputed **server-side** from the catalog)
- User accounts: register / sign in / reset password by **email or phone**
- "My Orders" page: every payment attempt with its risk score, tier and status
- **User profile dashboard** (`/profile`): profile photo upload, name, email, **+91 mobile**,
  location, and a password-change panel with a **live strength checklist + show/hide eye toggles**
- **Wishlist** (`/wishlist`): heart any product card — favourites are stored per account
  server-side and shown in the admin registry
- **Professional navigation**: back buttons on every inner page (shop ← home, cart ← shop,
  checkout ← cart, orders ← shop, profile/wishlist ← shop, auth pages ← home) plus forward
  CTAs at each step of the purchase funnel

**Payment gateway (the fraud engine)**
- Live card formatting with instant card-network detection (Visa / MasterCard / RuPay / Amex)
- Three-layer detection: **structure check → Luhn checksum → hybrid risk scoring**
- Hybrid score = `max(rule_engine_score, ML_probability)` — thresholds identical to the original
- Animated "running fraud checks" pipeline while the engine scores the transaction
- Verdict screens with a risk meter, per-rule signal breakdown and transaction ID
- **3-strike lockout**: three consecutive malformed/Luhn failures suspend the account
  (original message: *"Access Violations Triggered…"*)

**Admin desk** (`/admin`) — includes the **full user registry** (name, email, +91 phone,
location, order count, wishlist count, payment strikes, join date): everything the store
knows about every shopper, saved and auditable
- Totals: transactions, success / suspicious / fraud counts, ₹ volume, success rate
- CSS bar charts: transaction categories and risk-tier distribution
  (Low ≤ 25 · Medium ≤ 50 · High ≤ 75 · Critical ≤ 100)
- High-risk alert table (score ≥ 80) and the 50 most recent transactions
- ML model health indicator (loaded / rule-only fallback)

---

## 🧠 How the fraud detection works

The engine is a faithful port of the original `pages/payment.py` logic into
`backend/app/fraud.py` + `backend/app/routers/shop.py`.

### Layer 1 — Structural validation
The PAN must contain exactly **16 digits** after cleaning. Anything else is declined with the
original reason string: `Malformed Input: Lockout [n/3]`.

### Layer 2 — Luhn checksum
The card number must pass the **Luhn (mod-10) algorithm** — the same checksum real card
networks use. Failure ⇒ `Luhn Check Failed: Strike [n/3]` (risk recorded as 100%).

### Layer 3 — Hybrid risk scoring
Two scores are computed and the **maximum** is used:

**Rule engine** (weights identical to the original):

| Signal                                    | Points |
| ----------------------------------------- | -----: |
| Repeated failed attempts (streak ≥ 2)     |    +40 |
| Late-night transaction (hour 1–5 AM)      |    +20 |
| Unrecognised card network (not Visa/MC/RuPay/Amex) | +30 |
| High-value order (> ₹50,000)              |    +25 |
| Very high-value order (> ₹1,00,000)       |    +40 |

**ML model** — `models/ecommerce_fraud_model.pkl`:
RandomForest(200 estimators, seed 42) trained on `dataset/ecommerce_fraud.csv`
(features: `amount`, `country`, `transaction_hour`, `failed_attempts` → `is_fraud`).
Country strings are encoded with `models/ecommerce_encoder.pkl` (LabelEncoder).
`ml_risk = predict_proba(fraud) × 100`. If the model *predicts* class 1, the final
score is raised to at least 85 (original behaviour).

**Verdict thresholds** (identical to the original):

| Final risk score | Verdict       | Outcome                                   |
| ---------------: | ------------- | ----------------------------------------- |
| ≥ 80             | **Fraud**     | Blocked, strike recorded, card masked in logs |
| ≥ 50             | **Suspicious**| Order placed **and** flagged for review   |
| < 50             | **Success**   | Order placed, streak reset                |

**3-strike lockout** — three consecutive failed attempts suspend the account; further
payments return HTTP 403 with the original suspension message.

> A second academic model, `models/fraud_model.pkl` (RandomForest + StandardScaler + SMOTE
> trained on the Kaggle **creditcard.csv** dataset), ships in `models/` exactly as in the
> original project. It is used by the training/EDA scripts for academic comparison; the
> runtime gateway uses `ecommerce_fraud_model.pkl` (same as the original app).

---

## 📬 Automatic transactional email (Resend)

Every lifecycle event emails the user **automatically** — no manual step, no OTP:

| Event | Email |
| ----- | ----- |
| Registration | “Welcome to ShopZone 🎉” with account summary |
| Purchase (Success / Suspicious) | Branded receipt: items, amount, txn id, card mask, risk verdict |
| Fraud blocked | 🚨 Security alert with the blocked attempt details |
| Password changed | Confirmation + “wasn’t you?” recovery advice |
| “Email me a reset link” | Single-use link, valid 60 minutes (`/reset?token=…`) |

Set `RESEND_API_KEY` (+ optional verified `RESEND_FROM` domain) and delivery is live via the
Resend API. **Without a key** (local dev) every email is written to `data/outbox/*.eml` so
you can open and inspect exactly what users would receive. Setup: **DEPLOY.md Part 1**.

## 🗄️ Database — SQLite locally, Neon Postgres in production

- Default: zero-config **SQLite** (`data/shopzone.db`, self-healing schema).
- Set `DATABASE_URL` (Neon connection string) and the same code runs on **Postgres** —
  schema auto-created on boot (users, transactions, wishlist, reset_tokens).
  Both engines use 100% parameterised SQL. Setup: **DEPLOY.md Part 2**.

## 🗂️ Project structure

```
Shopzone/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI app — serves /api + the whole website on one port
│       ├── config.py          # env settings, admin credentials, JWT secret
│       ├── db.py              # SQLite schema (original tables) + safe additive migration
│       ├── security.py        # bcrypt hashing + JWT create/verify + role guards
│       ├── fraud.py           # ★ the detection engine (Luhn, card types, rules, ML)
│       ├── products.json      # 117-product catalog extracted from the original app
│       └── routers/
│           ├── auth.py        # register / login / reset / me
│           ├── shop.py        # products / pay / my transactions
│           └── admin.py       # admin statistics desk
├── frontend/
│   ├── index.html             # animated landing page
│   ├── shop.html  cart.html  checkout.html
│   ├── login.html  register.html  reset.html
│   ├── orders.html  admin.html
│   ├── profile.html  wishlist.html
│   ├── css/styles.css         # full design system + animations
│   └── js/api.js store.js ui.js
├── models/                    # original .pkl files (unchanged)
│   ├── ecommerce_fraud_model.pkl   ecommerce_encoder.pkl
│   ├── fraud_model.pkl             scaler.pkl
├── dataset/ecommerce_fraud.csv     # original dataset (unchanged)
├── scripts/                   # original training + EDA scripts (unchanged)
│   ├── train_ecommerce_model.py  train_model.py
│   ├── dataset_generator.py      eda.py
├── data/                      # created at runtime (shopzone.db) — git-ignored
├── .env.example               # copy to .env to override defaults
├── Dockerfile  .dockerignore
├── RUN.txt                    # 60-second quick start
├── DEPLOY.md                  # Resend + Neon + Render step-by-step
└── README.md
```

---

## 🚀 Run it

### Prerequisites
Python **3.10+** (tested on 3.11–3.13).

### Windows (PowerShell)
```powershell
cd Shopzone
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### macOS / Linux
```bash
cd Shopzone
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000** — the API and the website share this one port.

### Docker (optional)
```bash
cd Shopzone
docker build -t shopzone .
docker run -p 8000:8000 shopzone
```

> **Note:** on first startup you may see a `InconsistentVersionWarning` from scikit-learn if
> your installed version differs from the one used to pickle the models. This is harmless —
> the models load and predict correctly (the original pickles ship unmodified on purpose).

---

## 👤 Default credentials

| Role  | Email                  | Password   |
| ----- | ---------------------- | ---------- |
| Admin | `adminhere@gmail.com`  | `admin123` |
| User  | register your own at `/register` |

Passwords are stored as **bcrypt** hashes; sessions are **JWT HS256** tokens valid for 12 h.
Override everything (including `JWT_SECRET`) via `.env` — see `.env.example`.

---

## 🧪 Testing the fraud engine (cheat sheet)

Any future expiry (`12/29`) and any 3-digit CVV work — this is a **demo gateway**.

| Card number            | Network    | Expected result (small, daytime order)      |
| ---------------------- | ---------- | ------------------------------------------- |
| `4111 1111 1111 1111`  | Visa       | ✅ Success (low risk)                        |
| `5500 0000 0000 0004`  | MasterCard | ✅ Success                                   |
| `6000 0000 0000 0008`  | RuPay      | ✅ Success                                   |
| `3714 4963 5398 431`*  | Amex       | ✅ Success (15-digit Amex structure is rejected as 16-digit — see note) |
| `4111 1111 1111 1112`  | —          | 🚨 `Luhn Check Failed: Strike [1/3]`         |
| `9111 1111 1111 1110`  | Unknown    | ⚠️ Suspicious (+30 unknown network)          |

*The original engine (kept identical) validates a strict **16-digit** structure, so classic
15-digit Amex numbers are declined as malformed — this is intended legacy behaviour.

**Trigger each verdict:**
- **Success** — cheap product + Visa test card + daytime ⇒ risk < 50
- **Suspicious** — unknown-network card (9-prefix) at night ⇒ 30 + 20 = 50
- **Fraud** — buy the ₹1,29,999 iPhone ⇒ +25 + +40 high-value rules ⇒ 85 → blocked
- **Lockout** — fail Luhn three times ⇒ account suspended (403 on next attempt)

---

## 🔌 API reference

| Method | Endpoint                 | Auth   | Description                                  |
| ------ | ------------------------ | ------ | -------------------------------------------- |
| GET    | `/api/health`            | –      | Liveness + ML model status                   |
| POST   | `/api/auth/register`     | –      | `{name, email, phone, password}` → JWT       |
| POST   | `/api/auth/login`        | –      | `{email, password}` → JWT + user             |
| POST   | `/api/auth/reset`        | –      | `{identifier, new_password, confirm_password}` — identifier is **email or phone** (no OTP) |
| GET    | `/api/auth/me`           | JWT    | Current user profile                         |
| POST   | `/api/auth/forgot`       | –      | Email a single-use 60-min reset link (enumeration-safe) |
| POST   | `/api/auth/reset-token`  | –      | `{token, new_password, confirm_password}` — consumes the link |
| GET    | `/api/products`          | –      | Full catalog `{products, count}`             |
| GET    | `/api/products/{id}`     | –      | Single product                               |
| POST   | `/api/pay`               | JWT(user) | `{customer_name, card_number, expiry, cvv, cart:[{id,qty}]}` → verdict (`status`, `risk_score`, `reason`, `signals`, `ml_risk`, `rule_risk`, `transaction_id`, …) |
| GET    | `/api/me/transactions`   | JWT    | The caller's payment history                 |
| GET    | `/api/admin/stats`       | JWT(admin) | Metrics, category & risk-tier charts, high-risk alerts, recent transactions |
| GET    | `/api/admin/users`       | JWT(admin) | Full user registry with per-user order/wishlist/strike counts |
| PUT    | `/api/me/profile`        | JWT(user) | Update name, +91 phone, location, profile image (data-URI) |
| PUT    | `/api/me/password`       | JWT(user) | Change password (current + strong new + confirm) |
| GET    | `/api/me/wishlist`       | JWT(user) | Wishlist items (full product objects) |
| POST   | `/api/me/wishlist`       | JWT(user) | Add `{product_id}` to wishlist |
| DELETE | `/api/me/wishlist/{id}`  | JWT(user) | Remove product from wishlist |

All errors return JSON `{"detail": "…"}` with a meaningful HTTP status.
Amounts are **always computed server-side** from `products.json` — the client can never
tamper with the price. Cards are logged **masked** (`**** **** **** 1111`) — full PANs are
never stored.

---

## 📊 Dataset & models

- `dataset/ecommerce_fraud.csv` — original e-commerce fraud dataset
  (columns: `transaction_id, amount, country, transaction_hour, failed_attempts, is_fraud`).
  Regenerate with `scripts/dataset_generator.py`.
- `scripts/train_ecommerce_model.py` — trains `ecommerce_fraud_model.pkl` +
  `ecommerce_encoder.pkl` from the CSV (RandomForest, 200 trees, seed 42).
- `scripts/train_model.py` / `scripts/eda.py` — academic pipeline on the Kaggle
  **creditcard.csv** dataset (RF + StandardScaler + SMOTE) producing `fraud_model.pkl`
  and `scaler.pkl`. The ~150 MB Kaggle CSV is **not** bundled (licence/size); download it
  from Kaggle ("MLRegRESSION creditcardfraud") if you want to re-run that script.
- All four `.pkl` files ship **exactly as in the original project** — no retraining needed
  to run the app.

## ✅ Account validation rules (college spec)

| Field    | Rule |
| -------- | ---- |
| Email    | Must end with **.com / .in / .org** |
| Mobile   | **+91** prefix; 10 digits starting with **6, 7, 8 or 9** |
| Password | ≥ 8 chars mixing **uppercase + lowercase + number + special character** (live checklist on register / reset / profile) |
| Password UI | 👁 show/hide eye toggle on every password field |

Enforced **both client-side (instant feedback) and server-side (422 with a clear message)**.

## 🔒 Security notes

- bcrypt (cost 12) password hashing — never plaintext, never reversible
- JWT HS256 with 12 h expiry; role claims (`user` / `admin`) enforced server-side
- Admin cannot place orders; users cannot read admin stats (403/401 guards)
- Server-side amount computation, PAN masking, Luhn + structure validation before scoring
- Password reset requires the **registered email or phone** to match an account
- No OTP/SMS/email-sending services are used or required (removed from the original flow)

## 🛡️ Security hardening (tested)

- **Passwords:** bcrypt cost-12 hashes; strong-mix policy enforced client + server
- **Sessions:** JWT HS256, 12 h expiry, role claims enforced; tampered tokens → 401
- **Injection:** every SQL statement parameterised on both engines (SQLi probes tested)
- **XSS:** UI escapes all dynamic output; email templates HTML-escape every user value
- **Rate limiting:** login 8/min·account, register & forgot 5/min, pay 15/min → HTTP 429
- **Reset links:** single-use, 60-min expiry, stored hashed-free random 256-bit tokens;
  forgot endpoint never reveals whether an email exists (anti-enumeration)
- **Headers:** CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `Permissions-Policy`, HSTS when served over HTTPS
- **CORS:** explicit origin whitelist (no `*`); **open-redirect guard** on `?next=`
- **Payments:** amounts computed server-side, PANs masked in logs/emails, 3-strike lockout

## 🚀 Deployment

Step-by-step for **Resend + Neon + Render** in **DEPLOY.md** (with env-var table and
post-deploy checklist).

## 🧭 Ideas for extension

- Persist carts server-side; order fulfilment states (packed/shipped/delivered)
- Time-based auto-unlock or admin "unsuspend" button for locked accounts
- Export admin tables to CSV; date-range filters
- Retrain `ecommerce_fraud_model.pkl` on new gateway traffic (pipeline already in `scripts/`)
- Add product reviews, wishlists, coupons

---

*Built as a professional rebuild of the original Fraud_Detection_System college project —
same data, same models, same algorithm, new everything else.*
