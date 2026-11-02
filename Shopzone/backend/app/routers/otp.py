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