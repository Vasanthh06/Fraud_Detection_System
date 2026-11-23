# 🚀 ShopZone — Production Deployment Guide
### Resend emails + Neon Postgres + Render hosting, step by step

Everything below is **optional for local use** — without any keys the app runs on SQLite
and writes emails to `data/outbox/` so you can inspect them. Set the env vars and the
same code switches to real email delivery and Neon Postgres automatically.

---

## Part 1 — Resend (transactional email)

ShopZone sends these emails **automatically** (server-triggered, no manual step):

| Trigger                | Email                                    |
| ---------------------- | ---------------------------------------- |
| New registration       | “Welcome to ShopZone 🎉”                  |
| Payment approved/flagged | Receipt with items, amount, txn id, risk verdict |
| Payment **blocked**    | 🚨 Security alert with the blocked attempt |
| Password changed       | Confirmation + “wasn’t you?” warning     |
| “Email me a reset link”| One-time link, valid 60 minutes          |

1. Go to **https://resend.com** → *Sign up* (free tier: 3,000 emails/month, 100/day).
2. Dashboard → **API Keys** → *Create API Key* → copy the key (`re_xxxxxxxxxxxx`).
3. **Sender address:**
   - *Testing right away:* keep the default `ShopZone <onboarding@resend.dev>` — works with no setup.
   - *Professional:* **Domains → Add Domain** (e.g. `mail.yourdomain.com`). Resend shows
     DNS records (SPF + DKIM). Add them in your domain registrar's DNS panel, then press
     *Verify*. Once green, set `RESEND_FROM=ShopZone <noreply@mail.yourdomain.com>`.
4. Save the key as `RESEND_API_KEY` (see Part 3). Done — emails now deliver for real.

> **Local test without a key:** run the app, register a user, then open
> `Shopzone/data/outbox/*.eml` in a browser — that's exactly what Resend would receive.

---

## Part 2 — Neon (serverless Postgres for user data)

Render's filesystem is ephemeral, so production uses Neon; local runs keep SQLite.

1. Go to **https://neon.tech** → *Sign up* (free tier is enough) → **New Project**.
   - Name: `shopzone`
   - Region: pick the one closest to your Render region (for India: `ap-south-1` Mumbai).
2. Project dashboard → **Connection Details** → copy the connection string. It looks like:
   `postgresql://shopzone_user:AbCdEf123456@ep-cool-name-123456.ap-south-1.aws.neon.tech/neondb?sslmode=require`
   (Use the **pooled** variant if offered — better for serverless.)
3. Save it as `DATABASE_URL` (Part 3). **No tables to create manually** — ShopZone builds
   its schema (users, transactions, wishlist, reset_tokens) automatically on first start.
4. Keep the string secret: it contains the password. Never commit it (`.env` is git-ignored).

---

## Part 3 — Render (hosting)

1. Push the `Shopzone` folder to a GitHub repository (repo root = the folder contents:
   `backend/`, `frontend/`, `models/`, `dataset/`, `scripts/`, `README.md`, …).
2. **https://render.com** → *New → Web Service* → connect that repository.
3. Settings:
   - **Root Directory:** *(leave blank)*
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`
   - **Instance:** free tier is fine for a demo.
4. **Environment variables** (Render → *Environment* → add each):

   | Variable          | Value |
   | ----------------- | ----- |
   | `PYTHON_VERSION`  | `3.12` |
   | `JWT_SECRET`      | any long random string (e.g. `python -c "import secrets;print(secrets.token_hex(32))"`) |
   | `ADMIN_EMAIL`     | your admin login email |
   | `ADMIN_PASSWORD_HASH` | bcrypt hash of your admin password — generate: `python -c "import bcrypt;print(bcrypt.hashpw(b'YOUR_PASSWORD',bcrypt.gensalt()).decode())"` |
   | `RESEND_API_KEY`  | `re_xxx…` from Part 1 |
   | `RESEND_FROM`     | `ShopZone <onboarding@resend.dev>` or your verified domain |
   | `DATABASE_URL`    | Neon string from Part 2 |
   | `APP_URL`         | `https://<your-service>.onrender.com` (used inside email buttons/links) |
   | `CORS_ORIGINS`    | `https://<your-service>.onrender.com` |

5. *Deploy*. First boot creates the Neon tables; open the URL and register — the welcome
   email arrives in the inbox you registered with. ✔

---

## Part 4 — Run locally WITH real email / Neon (optional)

```powershell
# Windows PowerShell
$env:RESEND_API_KEY="re_xxx..."
$env:DATABASE_URL="postgresql://user:pass@ep-xxx.ap-south-1.aws.neon.tech/neondb?sslmode=require"
$env:APP_URL="http://localhost:8000"
cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
(or put the same lines in `Shopzone/.env` — see `.env.example`.)

---

## ✅ Post-deploy checklist

- [ ] `/api/health` returns `"ml_model_loaded": true`
- [ ] Register → welcome email in inbox (check spam once, then mark not-spam)
- [ ] Buy something → receipt email; admin desk shows the transaction
- [ ] “Email me a reset link” → link opens `/reset?token=…` and works once
- [ ] Neon dashboard → *Tables* shows `users`, `transactions`, `wishlist`, `reset_tokens`

## 🔒 Security built in (summary)

bcrypt(12) password hashing · JWT HS256 12 h · server-side price computation · PAN masking
(`**** **** **** 1111`) · parameterised SQL everywhere (SQLite **and** Postgres) ·
rate limits (login 8/min, register/forgot 5/min, pay 15/min → 429) · single-use 60-min
reset tokens · enumeration-safe forgot endpoint · security headers (CSP, X-Frame-Options
DENY, nosniff, Referrer-Policy, HSTS on https) · CORS whitelist instead of `*` ·
open-redirect guard on `?next=` · XSS-escaped UI + HTML-escaped emails · 3-strike payment
lockout · admin endpoints 403 for users.
