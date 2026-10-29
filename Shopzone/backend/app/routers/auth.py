"""Auth routes — register / login / reset (bcrypt, email-OR-phone reset, no OTP)
plus the college validation spec:
  * email must end with .com / .in / .org
  * Indian mobile: +91 prefix, 10 digits starting 6/7/8/9
  * strong password mix: 8+ chars, upper, lower, digit, special
"""
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from .. import db, emailsvc
from ..config import APP_URL
from ..security import (
    current_claims,
    rate_limit,
    create_token,
    email_suffix_ok,
    hash_password,
    is_admin_identity,
    normalize_in_phone,
    password_policy_issues,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$")


def _fail(status: int, message: str):
    from fastapi import HTTPException

    raise HTTPException(status_code=status, detail=message)


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=180)
    phone: str = Field(min_length=10, max_length=16)
    password: str = Field(min_length=1, max_length=72)


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=180)
    password: str = Field(min_length=1, max_length=72)


class ForgotIn(BaseModel):
    email: str = Field(min_length=5, max_length=180)


class ResetTokenIn(BaseModel):
    token: str = Field(min_length=10, max_length=120)
    new_password: str = Field(min_length=1, max_length=72)
    confirm_password: str = Field(min_length=1, max_length=72)


class ResetIn(BaseModel):
    identifier: str = Field(min_length=3, max_length=180)  # email OR phone
    new_password: str = Field(min_length=1, max_length=72)
    confirm_password: str = Field(min_length=1, max_length=72)


def _user_payload(row) -> dict:
    row = dict(row)  # sqlite3.Row -> plain dict (Row has no .get)
    return {
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "location": row.get("location") or "",
        "profile_image": row.get("profile_image") or "",
        "role": "user",
        "failed_payment_streak": row["failed_payment_streak"] or 0,
    }


@router.post("/register")
def register(body: RegisterIn, request: Request):
    rate_limit("reg:" + (request.client.host if request.client else "?"), 5)
    email = body.email.strip().lower()
    if not EMAIL_RE.match(email):
        _fail(422, "Enter a valid email address.")
    if not email_suffix_ok(email):
        _fail(422, "Enter a valid email address.")
    phone = normalize_in_phone(body.phone)
    if phone is None:
        _fail(422, "Enter a valid mobile number.")
    issues = password_policy_issues(body.password)
    if issues:
        _fail(422, "Password needs " + ", ".join(issues) + ".")
    ok = db.create_user(body.name.strip(), email, phone, hash_password(body.password))
    if not ok:
        _fail(409, "An account with this email already exists. Sign in instead.")
    row = db.get_user_by_email(email)
    token = create_token(email, "user", body.name.strip())
    subject, html_body = emailsvc.welcome_email(row["name"], email)
    emailsvc.send_async(email, subject, html_body)
    return {"token": token, "user": _user_payload(row)}


@router.post("/login")
def login(body: LoginIn, request: Request):
    email = body.email.strip().lower()
    rate_limit("login:" + (request.client.host if request.client else "?") + ":" + email, 8)
    # Admin desk (same rule as original verify_admin)
    if is_admin_identity(email, body.password):
        token = create_token(email, "admin", "Administrator")
        return {"token": token, "user": {"name": "Administrator", "email": email, "role": "admin"}}
    row = db.get_user_by_email(email)
    if row is None or not verify_password(body.password, row["password_hash"]):
        _fail(401, "Incorrect email or password.")
    token = create_token(email, "user", row["name"])
    return {"token": token, "user": _user_payload(row)}


@router.post("/reset")
def reset(body: ResetIn, request: Request):
    rate_limit("reset:" + (request.client.host if request.client else "?"), 5)
    if body.new_password != body.confirm_password:
        _fail(422, "Passwords do not match.")
    issues = password_policy_issues(body.new_password)
    if issues:
        _fail(422, "Password needs " + ", ".join(issues) + ".")
    identifier = body.identifier.strip()
    if "@" in identifier:
        identifier = identifier.lower()
    else:
        identifier = normalize_in_phone(identifier) or re.sub(r"\D", "", identifier)
    ok = db.reset_password(identifier, hash_password(body.new_password))
    if not ok:
        _fail(404, "No account found for that email or phone number.")
    return {"ok": True, "message": "Password reset successfully. You can sign in now."}


@router.post("/forgot")
def forgot(body: ForgotIn, request: Request):
    """Email a single-use, 60-minute reset link. Generic reply on purpose:
    never reveals whether an address is registered (account-enumeration safe)."""
    rate_limit("forgot:" + (request.client.host if request.client else "?"), 5)
    email = body.email.strip().lower()
    row = db.get_user_by_email(email)
    if row:
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.create_reset_token(email, token, expires.isoformat())
        link = f"{APP_URL}/reset?token={token}"
        subject, html_body = emailsvc.reset_link_email(row["name"], link)
        emailsvc.send_async(email, subject, html_body)
    return {"ok": True,
            "message": "If that email is registered, a reset link is on its way. Check your inbox."}


@router.post("/reset-token")
def reset_token(body: ResetTokenIn, request: Request):
    rate_limit("resettoken:" + (request.client.host if request.client else "?"), 10)
    if body.new_password != body.confirm_password:
        _fail(422, "Passwords do not match.")
    issues = password_policy_issues(body.new_password)
    if issues:
        _fail(422, "Password needs " + ", ".join(issues) + ".")
    email = db.consume_reset_token(body.token.strip())
    if email is None:
        _fail(400, "This reset link is invalid, already used or expired. Request a new one.")
    db.update_password_hash(email, hash_password(body.new_password))
    row = db.get_user_by_email(email)
    subject, html_body = emailsvc.password_changed_email(row["name"])
    emailsvc.send_async(email, subject, html_body)
    return {"ok": True, "message": "Password reset successfully. You can sign in now."}


@router.get("/me")
def me(claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    if claims.get("role") == "admin":
        return {"name": claims.get("name", "Administrator"), "email": email, "role": "admin"}
    row = db.get_user_by_email(email)
    if row is None:
        _fail(401, "Account no longer exists.")
    return _user_payload(row)
