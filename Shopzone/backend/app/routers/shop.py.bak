"""Shop routes — catalog + the payment gateway flow.

The payment flow is a 1:1 port of the original pages/payment.py:
structure check -> Luhn -> rule+ML scoring -> verdict -> streak/lockout ->
transaction saved with the same fields and reason strings.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, emailsvc
from ..fraud import clean_digits, evaluate_payment, luhn_check, mask_card
from ..security import (
    current_claims,
    rate_limit,
    email_suffix_ok,
    hash_password,
    normalize_in_phone,
    password_policy_issues,
    verify_password,
)

router = APIRouter(prefix="/api", tags=["shop"])

_PRODUCTS = json.loads((Path(__file__).resolve().parent.parent / "products.json").read_text())
_BY_ID = {p["id"]: p for p in _PRODUCTS}


@router.get("/products")
def products():
    return {"products": _PRODUCTS, "count": len(_PRODUCTS)}


@router.get("/products/{product_id}")
def product(product_id: int):
    item = _BY_ID.get(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return item


class CartLine(BaseModel):
    id: int
    qty: int = Field(ge=1, le=20)


class PayIn(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    card_number: str = Field(min_length=12, max_length=24)
    expiry: str = Field(min_length=4, max_length=7)
    cvv: str = Field(min_length=3, max_length=4)
    cart: list[CartLine] = Field(min_length=1)


def _decline(user_email: str, txn_id: str, name: str, products_label: str,
             amount: float, masked: str, hour: int, new_streak: int, reason: str) -> dict:
    db.save_transaction(
        txn_id, name, products_label, masked, amount, "India", "Web Browser Portal",
        hour, new_streak, 100.0, reason, "Fraud", user_email,
    )
    suspended = new_streak >= 3
    return {
        "status": "Fraud",
        "declined": True,
        "suspended": suspended,
        "risk_score": 100.0,
        "reason": reason,
        "streak": new_streak,
        "transaction_id": txn_id,
        "message": (
            "Account Suspended: Critical payment credential errors detected. Access blocked for 24 hours."
            if suspended
            else f"Payment Declined: {reason} ({new_streak}/3 failed attempts)"
        ),
    }


@router.post("/pay")
def pay(body: PayIn, request: Request, claims: dict = Depends(current_claims)):
    user_email = claims.get("sub", "")
    rate_limit("pay:" + (request.client.host if request.client else "?") + ":" + user_email, 15)
    if claims.get("role") != "user":
        raise HTTPException(status_code=403, detail="The admin desk cannot place orders.")

    current_streak = db.get_failed_payment_streak(user_email)
    if current_streak >= 3:
        raise HTTPException(
            status_code=403,
            detail="Access Violations Triggered: Your account has been suspended due to consecutive payment gateway threshold failures.",
        )

    # Amount is computed server-side from the catalog (same prices the UI shows)
    amount = 0.0
    names = []
    for line in body.cart:
        product = _BY_ID.get(line.id)
        if product is None:
            raise HTTPException(status_code=422, detail="Cart contains an unknown product.")
        amount += float(product["price"]) * line.qty
        names.append(product["name"])
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Your shopping bag is empty.")
    amount = round(amount, 2)

    clean_card = clean_digits(body.card_number)
    clean_expiry = clean_digits(body.expiry)
    if not body.customer_name.strip() or not clean_card or len(clean_expiry) != 4 or not clean_digits(body.cvv):
        raise HTTPException(status_code=422, detail="Validation Error: All processing credential parameters are required.")

    txn_id = str(uuid.uuid4())[:8]
    product_names = ", ".join(names)
    hour = datetime.now().hour

    # CHECK 1: card structure (original behaviour + reason strings)
    if len(clean_card) != 16 or not clean_card.isdigit():
        db.increment_failed_payment_streak(user_email)
        return _decline(user_email, txn_id, body.customer_name, product_names, amount,
                        "INVALID STRUCTURE", hour, current_streak + 1,
                        f"Malformed Input: Lockout [{current_streak + 1}/3]")

    # CHECK 2: Luhn
    if not luhn_check(clean_card):
        db.increment_failed_payment_streak(user_email)
        return _decline(user_email, txn_id, body.customer_name, product_names, amount,
                        mask_card(clean_card), hour, current_streak + 1,
                        f"Luhn Check Failed: Strike [{current_streak + 1}/3]")

    masked = mask_card(clean_card)

    # Score (rules + RandomForest, thresholds identical to the original)
    verdict = evaluate_payment(amount, clean_card, current_streak)
    status = verdict["status"]
    risk_score = verdict["risk_score"]
    reason = verdict["reason"]

    if status == "Fraud":
        db.increment_failed_payment_streak(user_email)
        new_streak = current_streak + 1
        db.save_transaction(
            txn_id, body.customer_name, product_names, masked, amount, verdict["country"],
            "Web Browser Portal", verdict["transaction_hour"], new_streak, risk_score,
            reason, "Fraud", user_email,
        )
        subj, hb = emailsvc.fraud_alert_email(
            body.customer_name, txn_id, f"₹{amount:,.2f}", f"{risk_score:.1f}%", reason, masked)
        emailsvc.send_async(user_email, subj, hb)
        return {
            "status": "Fraud",
            "declined": True,
            "suspended": new_streak >= 3,
            "risk_score": risk_score,
            "reason": reason,
            "streak": new_streak,
            "transaction_id": txn_id,
            "card_type": verdict["card_type"],
            "signals": verdict["signals"],
            "ml_risk": verdict["ml_risk"],
            "rule_risk": verdict["rule_risk"],
            "message": (
                "Account Locked. 3 fraud attempts detected. User logged out."
                if new_streak >= 3
                else f"Fraud Transaction Blocked | Risk Score: {risk_score:.1f}%"
            ),
        }

    if status == "Suspicious":
        db.save_transaction(
            txn_id, body.customer_name, product_names, masked, amount, verdict["country"],
            "Web Browser Portal", verdict["transaction_hour"], current_streak, risk_score,
            reason, "Suspicious", user_email,
        )
        subj, hb = emailsvc.receipt_email(
            body.customer_name, txn_id, product_names, f"₹{amount:,.2f}",
            "Suspicious", f"{risk_score:.1f}%", masked, user_email)
        emailsvc.send_async(user_email, subj, hb)
        return {
            "status": "Suspicious",
            "declined": False,
            "order_placed": True,
            "risk_score": risk_score,
            "reason": reason,
            "transaction_id": txn_id,
            "card_type": verdict["card_type"],
            "signals": verdict["signals"],
            "ml_risk": verdict["ml_risk"],
            "rule_risk": verdict["rule_risk"],
            "message": f"Suspicious Transaction Recorded | Risk Score: {risk_score:.1f}%",
        }

    # Success — reset streak exactly like the original
    db.reset_failed_payment_streak(user_email)
    db.save_transaction(
        txn_id, body.customer_name, product_names, masked, amount, verdict["country"],
        "Web Browser Portal", verdict["transaction_hour"], 0, risk_score,
        reason, "Success", user_email,
    )
    subj, hb = emailsvc.receipt_email(
        body.customer_name, txn_id, product_names, f"₹{amount:,.2f}",
        "Success", f"{risk_score:.1f}%", masked, user_email)
    emailsvc.send_async(user_email, subj, hb)
    return {
        "status": "Success",
        "declined": False,
        "order_placed": True,
        "risk_score": risk_score,
        "reason": reason,
        "transaction_id": txn_id,
        "card_type": verdict["card_type"],
        "signals": verdict["signals"],
        "ml_risk": verdict["ml_risk"],
        "rule_risk": verdict["rule_risk"],
        "message": "Payment approved. Thank you for shopping with ShopZone.",
    }


@router.get("/me/transactions")
def my_transactions(claims: dict = Depends(current_claims)):
    rows = db.list_transactions(limit=200, user_email=claims.get("sub", ""))
    return {"transactions": rows, "count": len(rows)}


# ================= user profile =================

class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=10, max_length=16)
    location: str = Field(default="", max_length=120)
    profile_image: str | None = None


class PasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=1, max_length=72)
    confirm_password: str = Field(min_length=1, max_length=72)


class WishIn(BaseModel):
    product_id: int


@router.put("/me/profile")
def update_profile(body: ProfileIn, claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    if claims.get("role") != "user":
        raise HTTPException(status_code=403, detail="Admin accounts do not have shopper profiles.")
    phone = normalize_in_phone(body.phone)
    if phone is None:
        raise HTTPException(status_code=422, detail="Enter a valid mobile number.")
    if body.profile_image is not None and len(body.profile_image) > 2_500_000:
        raise HTTPException(status_code=422, detail="Profile image too large (max ~1.5 MB).")
    ok = db.update_profile(email, body.name.strip(), phone, body.location.strip(), body.profile_image)
    if not ok:
        raise HTTPException(status_code=409, detail="That phone number is already used by another account.")
    row = db.get_user_by_email(email)
    return {"ok": True, "user": {
        "name": row["name"], "email": row["email"], "phone": row["phone"],
        "location": row.get("location") or "", "profile_image": row.get("profile_image") or "",
        "role": "user",
    }}


@router.put("/me/password")
def change_password(body: PasswordIn, claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    if claims.get("role") != "user":
        raise HTTPException(status_code=403, detail="Admin password is managed via server environment.")
    row = db.get_user_by_email(email)
    if row is None or not verify_password(body.current_password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=422, detail="New passwords do not match.")
    issues = password_policy_issues(body.new_password)
    if issues:
        raise HTTPException(status_code=422, detail="Password needs " + ", ".join(issues) + ".")
    db.update_password_hash(email, hash_password(body.new_password))
    row = db.get_user_by_email(email)
    subj, hb = emailsvc.password_changed_email(row["name"])
    emailsvc.send_async(email, subj, hb)
    return {"ok": True, "message": "Password updated. Use it on your next sign-in."}


# ================= wishlist =================

@router.get("/me/wishlist")
def wishlist(claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    rows = db.wishlist_list(email)
    items = []
    for r in rows:
        product = _BY_ID.get(r["product_id"])
        if product:
            items.append({**product, "added_at": r["added_at"]})
    return {"items": items, "count": len(items)}


@router.post("/me/wishlist")
def wishlist_add(body: WishIn, claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    if _BY_ID.get(body.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    db.wishlist_add(email, body.product_id)
    return {"ok": True, "count": len(db.wishlist_list(email))}


@router.delete("/me/wishlist/{product_id}")
def wishlist_remove(product_id: int, claims: dict = Depends(current_claims)):
    email = claims.get("sub", "")
    db.wishlist_remove(email, product_id)
    return {"ok": True, "count": len(db.wishlist_list(email))}
