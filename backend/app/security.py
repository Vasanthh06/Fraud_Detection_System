"""Password hashing (bcrypt), JWT session tokens and a sliding-window rate limiter."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Header, HTTPException

from .config import ADMIN_EMAIL, ADMIN_PASSWORD_HASH, JWT_EXPIRE_HOURS, JWT_SECRET


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def create_token(email: str, role: str, name: str = "") -> str:
    payload = {
        "sub": email,
        "role": role,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")


def current_claims(authorization: str = Header(default="")) -> dict:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in required.")
    return decode_token(authorization.split(" ", 1)[1].strip())


def admin_claims(authorization: str = Header(default="")) -> dict:
    claims = current_claims(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin desk only.")
    return claims


EMAIL_SUFFIXES = (".com", ".in", ".org")


def email_suffix_ok(email: str) -> bool:
    """Registered emails must end with .com / .in / .org (college spec)."""
    local, sep, domain = email.partition("@")
    if not sep or not local:
        return False
    return domain.lower().endswith(EMAIL_SUFFIXES)


def normalize_in_phone(value: str) -> str | None:
    """Indian mobile: optional +91/91 prefix, then 10 digits starting 6-9.
    Returns the bare 10-digit number or None when invalid."""
    digits = "".join(ch for ch in value if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10 or digits[0] not in "6789":
        return None
    return digits


def password_policy_issues(password: str) -> list[str]:
    """Strong-password mix: length + upper + lower + digit + symbol."""
    issues = []
    if len(password) < 8:
        issues.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        issues.append("an uppercase letter")
    if not any(c.islower() for c in password):
        issues.append("a lowercase letter")
    if not any(c.isdigit() for c in password):
        issues.append("a number")
    if not any(not c.isalnum() for c in password):
        issues.append("a special character")
    return issues


def is_admin_identity(email: str, password: str) -> bool:
    """Same rule as the original verify_admin: env admin email + bcrypt hash."""
    return email.strip().lower() == ADMIN_EMAIL.strip().lower() and verify_password(
        password, ADMIN_PASSWORD_HASH
    )


# ---------------- rate limiting (in-memory, per worker) ----------------
import time
from collections import defaultdict, deque

_buckets: dict = defaultdict(deque)


def rate_limit(key: str, limit: int, window: int = 60) -> None:
    """429 when `key` exceeds `limit` requests inside `window` seconds."""
    now = time.time()
    dq = _buckets[key]
    while dq and now - dq[0] > window:
        dq.popleft()
    if len(dq) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please slow down and try again in a minute.",
        )
    dq.append(now)
