# ============ ShopZone OTP installer ============
$ErrorActionPreference = 'Stop'
Set-Location E:\ShopZone\Shopzone

function Backup($p) {
    if (-not (Test-Path "$p.bak-otp")) { Copy-Item $p "$p.bak-otp" }
    Write-Host "  backup $p -> $p.bak-otp" -ForegroundColor DarkGray
}
function WriteNew($path, $content) {
    $dir = Split-Path $path -Parent
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    if (Test-Path $path) { Backup $path }
    Set-Content -Path $path -Value $content -Encoding UTF8 -NoNewline
    Write-Host "  wrote $path" -ForegroundColor Green
}
function CompileOrRollback($path) {
    & python -m py_compile $path
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SYNTAX ERROR in $path — rolling back" -ForegroundColor Red
        Move-Item "$path.bak-otp" $path -Force
        throw "Rolled back $path"
    }
}

# ---------- 1. backend/app/otp.py ----------
$otpPy = @'
"""OTP service — generate, store, verify, issue short-lived tokens.

Storage: uses db.cursor (SQLite / Postgres) via db._q placeholders.
Codes are bcrypt-hashed. Purposes: password_change | transaction | payment.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException

from . import db, emailsvc
from .config import ENV, JWT_SECRET
from .security import decode_token

logger = logging.getLogger("shopzone.otp")

PURPOSES = {"password_change", "transaction", "payment"}
OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 3
OTP_COOLDOWN_SECONDS = 30
TOKEN_TTL_SECONDS = 300


def init_otp_table() -> None:
    q = db._q
    with db.cursor(commit=True) as cx:
        cx.execute(q("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                purpose TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """) if db.ENGINE == "postgres" else q("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                purpose TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """))
        try:
            cx.execute(q("CREATE INDEX IF NOT EXISTS ix_otp_lookup ON otp_codes(email, purpose, used)"))
        except Exception:
            pass


def _now() -> datetime:
    return datetime.now(timezone.utc)

def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()

def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)

def _hash(code: str) -> str:
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt(rounds=10)).decode()

def _check(code: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(code.encode(), hashed.encode())
    except ValueError:
        return False

def _validate_purpose(purpose: str) -> None:
    if purpose not in PURPOSES:
        raise HTTPException(status_code=400, detail="Invalid OTP purpose.")


def generate_otp(email: str, purpose: str) -> None:
    _validate_purpose(purpose)
    email = (email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    q = db._q
    now = _now()
    with db.cursor(commit=True) as cx:
        row = cx.execute(
            q("SELECT created_at FROM otp_codes WHERE email=? AND purpose=? ORDER BY id DESC LIMIT 1"),
            (email, purpose),
        ).fetchone()
        if row:
            elapsed = (now - _parse_iso(row["created_at"])).total_seconds()
            if elapsed < OTP_COOLDOWN_SECONDS:
                wait = int(OTP_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(status_code=429, detail=f"Please wait {wait}s before requesting another code.")

        cx.execute(
            q("UPDATE otp_codes SET used=1 WHERE email=? AND purpose=? AND used=0"),
            (email, purpose),
        )
        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = now + timedelta(seconds=OTP_TTL_SECONDS)
        cx.execute(
            q("INSERT INTO otp_codes (email, purpose, code_hash, expires_at, attempts, used, created_at) "
              "VALUES (?,?,?,?,0,0,?)"),
            (email, purpose, _hash(code), _iso(expires_at), _iso(now)),
        )

    if ENV == "development":
        logger.info("OTP [%s] for %s: %s (dev log)", purpose, email, code)

    subject = "Your ShopZone verification code"
    html = (
        f"<p>Your ShopZone verification code is:</p>"
        f"<p style='font-size:28px;font-weight:bold;letter-spacing:6px'>{code}</p>"
        f"<p>This code expires in 5 minutes. Purpose: <b>{purpose}</b>.</p>"
        f"<p>If you didn't request this, ignore the email.</p>"
    )
    try:
        if hasattr(emailsvc, "send_async"):
            emailsvc.send_async(email, subject, html)
        else:
            emailsvc.send_email(email, subject, html)
    except Exception as e:
        logger.exception("Failed to send OTP email: %s", e)


def verify_otp(email: str, code: str, purpose: str) -> str:
    _validate_purpose(purpose)
    email = (email or "").strip().lower()
    code = (code or "").strip()
    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required.")
    if not (len(code) == 6 and code.isdigit()):
        raise HTTPException(status_code=400, detail="Code must be 6 digits.")

    q = db._q
    now = _now()
    with db.cursor(commit=True) as cx:
        row = cx.execute(
            q("SELECT id, code_hash, expires_at, attempts, used FROM otp_codes "
              "WHERE email=? AND purpose=? ORDER BY id DESC LIMIT 1"),
            (email, purpose),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="No OTP found. Request a new code.")
        if row["used"]:
            raise HTTPException(status_code=400, detail="Code already used. Request a new one.")
        if _parse_iso(row["expires_at"]) < now:
            raise HTTPException(status_code=400, detail="Code expired. Request a new one.")
        if row["attempts"] >= OTP_MAX_ATTEMPTS:
            raise HTTPException(status_code=400, detail="Too many attempts. Request a new code.")

        if not _check(code, row["code_hash"]):
            cx.execute(q("UPDATE otp_codes SET attempts = attempts + 1 WHERE id=?"), (row["id"],))
            remaining = OTP_MAX_ATTEMPTS - (row["attempts"] + 1)
            raise HTTPException(status_code=400, detail=f"Incorrect code. {max(remaining,0)} attempt(s) left.")

        cx.execute(q("UPDATE otp_codes SET used=1 WHERE id=?"), (row["id"],))

    return _issue_otp_token(email, purpose)


def _issue_otp_token(email: str, purpose: str) -> str:
    payload = {
        "sub": email,
        "otp": True,
        "purpose": purpose,
        "exp": int((_now() + timedelta(seconds=TOKEN_TTL_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def require_otp(request, purpose: str, email: str) -> None:
    token = request.headers.get("x-otp-token")
    if not token:
        raise HTTPException(status_code=403, detail="OTP verification required.")
    try:
        claims = decode_token(token)
    except HTTPException:
        raise HTTPException(status_code=403, detail="Invalid or expired OTP token.")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired OTP token.")
    if not claims.get("otp"):
        raise HTTPException(status_code=403, detail="Not an OTP token.")
    if (claims.get("sub") or "").lower() != (email or "").lower():
        raise HTTPException(status_code=403, detail="OTP token is for a different account.")
    if claims.get("purpose") != purpose:
        raise HTTPException(status_code=403, detail=f"OTP token purpose mismatch (need {purpose}).")
'@
WriteNew "backend\app\otp.py" $otpPy
CompileOrRollback "backend\app\otp.py"

# ---------- 2. backend/app/routers/otp.py ----------
$otpRouter = @'
"""OTP routes: /api/otp/send, /api/otp/verify"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..otp import generate_otp, verify_otp
from ..security import current_claims

router = APIRouter(prefix="/api/otp", tags=["otp"])


class SendIn(BaseModel):
    email: str = Field(min_length=5, max_length=180)
    purpose: str = Field(min_length=4, max_length=32)


class VerifyIn(BaseModel):
    email: str = Field(min_length=5, max_length=180)
    code: str = Field(min_length=6, max_length=6)
    purpose: str = Field(min_length=4, max_length=32)


@router.post("/send")
def send(body: SendIn):
    generate_otp(body.email, body.purpose)
    return {"ok": True, "message": "If the email exists, a code was sent."}


@router.post("/verify")
def verify(body: VerifyIn, claims: dict = Depends(current_claims)):
    if (claims.get("sub") or "").lower() != body.email.strip().lower():
        raise HTTPException(status_code=403, detail="OTP email must match the logged-in account.")
    token = verify_otp(body.email, body.code, body.purpose)
    return {"ok": True, "otp_token": token}
'@
WriteNew "backend\app\routers\otp.py" $otpRouter
CompileOrRollback "backend\app\routers\otp.py"

# ---------- 3. patch shop.py ----------
Backup "backend\app\routers\shop.py"
$shop = Get-Content "backend\app\routers\shop.py" -Raw

# 3a: import
if ($shop -notmatch 'from \.\.otp import require_otp') {
    $shop = $shop -replace '(?m)^(from \.\. import db, emailsvc\r?\n)', "`$1from ..otp import require_otp`r`n"
}

# 3b: gate POST /pay — insert after the FIRST occurrence of user_email = claims.get("sub", "") inside pay()
if ($shop -notmatch 'require_otp\(request, "payment"') {
    $shop = [regex]::Replace(
        $shop,
        '(def pay\([^\)]*\):\s*\r?\n\s+user_email = claims\.get\("sub", ""\)\r?\n)(\s+rate_limit\("pay:)',
        { param($m) $m.Groups[1].Value + '    require_otp(request, "payment", user_email)' + "`r`n" + $m.Groups[2].Value },
        1
    )
}

# 3c: change_password — add request param + insert gate after `email = claims.get("sub", "")`
if ($shop -notmatch 'require_otp\(request, "password_change"') {
    $shop = [regex]::Replace(
        $shop,
        '(def change_password\(body: PasswordIn,)(\s*)claims: dict = Depends\(current_claims\)\):(\s*\r?\n\s+)email = claims\.get\("sub", ""\)(\r?\n)',
        { param($m)
            'def change_password(body: PasswordIn,' + $m.Groups[2].Value + 'request: Request,' + $m.Groups[2].Value + 'claims: dict = Depends(current_claims)):' + $m.Groups[3].Value + 'email = claims.get("sub", "")' + $m.Groups[4].Value + '    require_otp(request, "password_change", email)' + "`r`n"
        },
        1
    )
}

Set-Content "backend\app\routers\shop.py" $shop -Encoding UTF8 -NoNewline
Write-Host "  patched backend\app\routers\shop.py" -ForegroundColor Green
CompileOrRollback "backend\app\routers\shop.py"

# ---------- 4. patch main.py ----------
Backup "backend\app\main.py"
$main = Get-Content "backend\app\main.py" -Raw

if ($main -notmatch 'from \.routers import .*otp') {
    if ($main -match '(from \.routers import )([^\r\n]+)') {
        $imports = $matches[2].Trim()
        if ($imports -notmatch '\botp\b') {
            $main = $main -replace [regex]::Escape($matches[0]), ("from .routers import " + $imports + ", otp as otp_router")
        }
    } else {
        $main = $main -replace '(?m)^(from fastapi import [^\r\n]*\r?\n)', "`$1from .routers import otp as otp_router`r`n"
    }
}

if ($main -notmatch 'include_router\(otp_router\.router\)') {
    if ($main -match '(app\.include_router\([^\r\n]+\)\r?\n)') {
        $main = $main -replace [regex]::Escape($matches[0]), ($matches[0] + "app.include_router(otp_router.router)`r`n")
    } else {
        $main = $main.TrimEnd() + "`r`napp.include_router(otp_router.router)`r`n"
    }
}

if ($main -notmatch 'init_otp_table\(\)') {
    if ($main -match '(app\s*=\s*FastAPI\([^\)]*\)\r?\n)') {
        $main = $main -replace [regex]::Escape($matches[0]), ($matches[0] + "`r`nfrom .otp import init_otp_table`r`ninit_otp_table()`r`n")
    } else {
        $main = $main.TrimEnd() + "`r`nfrom .otp import init_otp_table`r`ninit_otp_table()`r`n"
    }
}

Set-Content "backend\app\main.py" $main -Encoding UTF8 -NoNewline
Write-Host "  patched backend\app\main.py" -ForegroundColor Green
CompileOrRollback "backend\app\main.py"

# ---------- 5. frontend/js/otp.js ----------
$otpJs = @'
// frontend/js/otp.js — OTP request + modal verify
async function requestOtp(email, purpose) {
  return API.post('/otp/send', { email, purpose });
}

function showOtpModal({ email, purpose, onVerified }) {
  if (document.getElementById('otpModal')) return;
  const wrap = document.createElement('div');
  wrap.id = 'otpModal';
  wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.55);display:grid;place-items:center;z-index:9999';
  wrap.innerHTML = `
    <div style="background:var(--card,#fff);color:inherit;padding:24px;border-radius:14px;width:340px;max-width:92vw;box-shadow:0 20px 60px rgba(0,0,0,.4)">
      <h3 style="margin:0 0 8px">Verify your email</h3>
      <p style="margin:0 0 16px;font-size:14px;opacity:.8">
        We sent a 6-digit code to <b>${email}</b> for <b>${purpose}</b>.
      </p>
      <input id="otpCode" inputmode="numeric" maxlength="6"
             style="width:100%;padding:10px;font-size:22px;letter-spacing:8px;text-align:center;border-radius:10px;border:1px solid #ccc"
             placeholder="••••••" />
      <div id="otpErr" style="color:#e11d48;font-size:13px;margin-top:8px;display:none"></div>
      <div style="display:flex;gap:8px;margin-top:14px">
        <button id="otpCancel" style="flex:1;padding:10px;border-radius:10px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer">Cancel</button>
        <button id="otpResend" style="flex:1;padding:10px;border-radius:10px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer" disabled>Resend (30s)</button>
        <button id="otpOk" style="flex:1;padding:10px;border-radius:10px;border:none;background:#10b981;color:#04121a;font-weight:700;cursor:pointer">Verify</button>
      </div>
    </div>`;
  document.body.appendChild(wrap);

  const codeEl = wrap.querySelector('#otpCode');
  const errEl  = wrap.querySelector('#otpErr');
  const okBtn  = wrap.querySelector('#otpOk');
  const rsBtn  = wrap.querySelector('#otpResend');
  const cancel = wrap.querySelector('#otpCancel');
  codeEl.focus();

  let seconds = 30;
  const tick = setInterval(() => {
    seconds -= 1;
    if (seconds <= 0) { clearInterval(tick); rsBtn.disabled = false; rsBtn.textContent = 'Resend'; }
    else { rsBtn.textContent = `Resend (${seconds}s)`; }
  }, 1000);

  const close = () => { clearInterval(tick); wrap.remove(); };
  cancel.onclick = close;

  rsBtn.onclick = async () => {
    rsBtn.disabled = true; seconds = 30; rsBtn.textContent = `Resend (${seconds}s)`;
    try { await requestOtp(email, purpose); } catch (e) {
      errEl.textContent = e.message; errEl.style.display = 'block';
    }
  };

  okBtn.onclick = async () => {
    errEl.style.display = 'none';
    const code = codeEl.value.trim();
    if (!/^\d{6}$/.test(code)) { errEl.textContent = 'Enter the 6-digit code.'; errEl.style.display = 'block'; return; }
    okBtn.disabled = true; okBtn.textContent = 'Verifying…';
    try {
      const res = await API.post('/otp/verify', { email, code, purpose });
      close(); onVerified(res.otp_token);
    } catch (e) {
      errEl.textContent = e.message; errEl.style.display = 'block';
      okBtn.disabled = false; okBtn.textContent = 'Verify';
    }
  };
}
'@
WriteNew "frontend\js\otp.js" $otpJs

Write-Host ""
Write-Host "=== Install complete ===" -ForegroundColor Green
Write-Host "Next: restart uvicorn (Ctrl+C in its terminal, then:"
Write-Host "  cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000)"
Write-Host ""
Write-Host "Then verify the patches landed:"
Write-Host "  Select-String -Path backend\app\routers\shop.py -Pattern 'require_otp'"
Write-Host "  Select-String -Path backend\app\main.py -Pattern 'otp_router|init_otp_table'"