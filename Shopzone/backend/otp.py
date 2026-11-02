# generate_otp(email, purpose) -> sends email, stores hash, returns None
# verify_otp(email, code, purpose) -> bool
# issue_otp_token(email, purpose) -> JWT string (~5 min)
# require_otp_token(request, purpose) -> decoded payload or raises 403"""OTP service — generate, store, verify, issue short-lived tokens.

Storage: SQLite (same DB_PATH as the app). Codes are bcrypt-hashed.
Purposes: password_change | transaction | payment
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException

from . import db, emailsvc
from .config import DB_PATH, ENV, JWT_SECRET
from .security import create_token  # reuse the JWT helper

logger = logging.getLogger("shopzone.otp")

PURPOSES = {"password_change", "transaction", "payment"}
OTP_TTL_SECONDS = 300          # 5 min
OTP_MAX_ATTEMPTS = 3
OTP_COOLDOWN_SECONDS = 30
TOKEN_TTL_SECONDS = 300        # otp_token valid 5 min

# ---------- schema ----------
def init_otp_table() -> None:
    with db.connect() as cx:
        cx.execute(
            """
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
            """
        )
        cx.execute(
            "CREATE INDEX IF NOT EXISTS ix_otp_lookup ON otp_codes(email, purpose, used)"
        )

# ---------- helpers ----------
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

# ---------- public API ----------
def generate_otp(email: str, purpose: str) -> None:
    """Create a fresh code (invalidating prior ones) and email it."""
    _validate_purpose(purpose)
    email = (email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    now = _now()

    with db.connect() as cx:
        # cooldown — last code for this email+purpose
        row = cx.execute(
            "SELECT created_at FROM otp_codes WHERE email=? AND purpose=? "
            "ORDER BY id DESC LIMIT 1",
            (email, purpose),
        ).fetchone()
        if row:
            last = _parse_iso(row["created_at"])
            elapsed = (now - last).total_seconds()
            if elapsed < OTP_COOLDOWN_SECONDS:
                wait = int(OTP_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(
                    status_code=429,
                    detail=f"Please wait {wait}s before requesting another code.",
                )

        # invalidate prior unused codes for this purpose
        cx.execute(
            "UPDATE otp_codes SET used=1 WHERE email=? AND purpose=? AND used=0",
            (email, purpose),
        )

        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = now + timedelta(seconds=OTP_TTL_SECONDS)
        cx.execute(
            "INSERT INTO otp_codes (email, purpose, code_hash, expires_at, "
            "attempts, used, created_at) VALUES (?,?,?,?,0,0,?)",
            (email, purpose, _hash(code), _iso(expires_at), _iso(now)),
        )

    if ENV == "development":
        logger.info("OTP [%s] for %s: %s (dev log — do not use in prod)", purpose, email, code)

    subject = "Your ShopZone verification code"
    html = (
        f"<p>Your ShopZone verification code is:</p>"
        f"<p style='font-size:28px;font-weight:bold;letter-spacing:6px'>{code}</p>"
        f"<p>This code expires in 5 minutes. Purpose: <b>{purpose}</b>.</p>"
        f"<p>If you didn't request this, ignore the email.</p>"
    )
    emailsvc.send_email_async(email, subject, html)


def verify_otp(email: str, code: str, purpose: str) -> str:
    """Verify code. Returns a signed otp_token on success, raises HTTPException otherwise."""
    _validate_purpose(purpose)
    email = (email or "").strip().lower()
    code = (code or "").strip()
    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required.")
    if not (len(code) == 6 and code.isdigit()):
        raise HTTPException(status_code=400, detail="Code must be 6 digits.")

    now = _now()
    with db.connect() as cx:
        row = cx.execute(
            "SELECT id, code_hash, expires_at, attempts, used FROM otp_codes "
            "WHERE email=? AND purpose=? ORDER BY id DESC LIMIT 1",
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
            cx.execute(
                "UPDATE otp_codes SET attempts = attempts + 1 WHERE id=?",
                (row["id"],),
            )
            remaining = OTP_MAX_ATTEMPTS - (row["attempts"] + 1)
            raise HTTPException(
                status_code=400,
                detail=f"Incorrect code. {max(remaining, 0)} attempt(s) left.",
            )

        cx.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row["id"],))

    return _issue_otp_token(email, purpose)


def _issue_otp_token(email: str, purpose: str) -> str:
    """Short-lived JWT proving OTP was verified for this email+purpose."""
    payload = {
        "sub": email,
        "otp": True,
        "purpose": purpose,
        "exp": int((_now() + timedelta(seconds=TOKEN_TTL_SECONDS)).timestamp()),
    }
    return create_token(payload, expires_hours=0)  # helper accepts exp in payload


def require_otp(request, purpose: str, email: str) -> None:
    """Gate: ensure X-OTP-Token header is valid for this email+purpose."""
    from .security import decode_token  # local import to avoid cycles

    token = request.headers.get("x-otp-token") or request.headers.get("X-OTP-Token")
    if not token:
        raise HTTPException(status_code=403, detail="OTP verification required.")

    try:
        claims = decode_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired OTP token.")

    if not claims.get("otp"):
        raise HTTPException(status_code=403, detail="Not an OTP token.")
    if (claims.get("sub") or "").lower() != email.lower():
        raise HTTPException(status_code=403, detail="OTP token is for a different account.")
    if claims.get("purpose") != purpose:
        raise HTTPException(status_code=403, detail=f"OTP token purpose mismatch (need {purpose}).")