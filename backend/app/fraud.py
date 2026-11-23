"""ShopZone fraud engine — ported 1:1 from the original pages/payment.py.

Pipeline (unchanged):
  1. Card structure check (16 digits)
  2. Luhn checksum
  3. Rule-based risk points:
       failed_attempts >= 2      -> +40
       transaction hour 1..5     -> +20
       unknown card network      -> +30
       amount > 50,000           -> +25
       amount > 100,000          -> +40
  4. RandomForest (models/ecommerce_fraud_model.pkl) on
     [amount, country(encoded), transaction_hour, failed_attempts]
     ml_risk = predict_proba(fraud) * 100
  5. risk_score = max(rule_risk, ml_risk); prediction == 1 floors it at 85
  6. Verdict: >= 80 Fraud | >= 50 Suspicious | else Success
"""
import re
from datetime import datetime

import joblib
import pandas as pd

from .config import ECOM_ENCODER_PATH, ECOM_MODEL_PATH

_model = None
_encoder = None


def load_models():
    global _model, _encoder
    if _model is None:
        try:
            _model = joblib.load(ECOM_MODEL_PATH)
            _encoder = joblib.load(ECOM_ENCODER_PATH)
        except Exception as exc:
            print("ML models not found — rule-based detection only:", exc)
            _model, _encoder = None, None
    return _model, _encoder


def models_available() -> bool:
    m, e = load_models()
    return m is not None and e is not None


# ------------------------------------------------- card helpers (verbatim)
def clean_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "").strip()


def luhn_check(card_number: str) -> bool:
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def get_card_type(card_number: str) -> str:
    if card_number.startswith("4"):
        return "Visa"
    elif card_number.startswith("5"):
        return "MasterCard"
    elif card_number.startswith("6"):
        return "RuPay"
    elif card_number.startswith("34") or card_number.startswith("37"):
        return "American Express"
    return "Unknown"


def mask_card(card_number: str) -> str:
    return f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else "****"


# ------------------------------------------------------------ the engine
def evaluate_payment(
    amount: float,
    card_number: str,
    failed_attempts: int,
    country: str = "India",
    when: datetime | None = None,
) -> dict:
    """Return the verdict exactly as the original payment flow computed it,
    plus an explanation breakdown for the UI (explanation only — the scoring
    math is untouched)."""
    when = when or datetime.now()
    transaction_hour = when.hour
    card_type = get_card_type(card_number)

    signals = []
    rule_risk = 0
    if failed_attempts >= 2:
        rule_risk += 40
        signals.append({"label": "Repeated failed attempts", "points": 40})
    if 1 <= transaction_hour <= 5:
        rule_risk += 20
        signals.append({"label": "Late-night transaction (1–5 AM)", "points": 20})
    if card_type == "Unknown":
        rule_risk += 30
        signals.append({"label": "Unrecognised card network", "points": 30})
    if amount > 50000:
        rule_risk += 25
        signals.append({"label": "High-value order (₹50,000+)", "points": 25})
    if amount > 100000:
        rule_risk += 40
        signals.append({"label": "Very high-value order (₹1,00,000+)", "points": 40})

    prediction = 0
    ml_risk = 0.0
    model, encoder = load_models()
    if model is not None and encoder is not None:
        try:
            country_encoded = encoder.transform([country])[0]
            input_df = pd.DataFrame(
                [[amount, country_encoded, transaction_hour, failed_attempts]],
                columns=["amount", "country", "transaction_hour", "failed_attempts"],
            )
            prediction = int(model.predict(input_df)[0])
            if hasattr(model, "predict_proba"):
                ml_risk = round(float(model.predict_proba(input_df)[0][1]) * 100, 2)
        except Exception as exc:
            print("ML Error:", exc)

    risk_score = max(rule_risk, ml_risk)
    if prediction == 1:
        risk_score = max(risk_score, 85)

    if risk_score >= 80:
        status, reason = "Fraud", "High Risk Transaction Detected"
    elif risk_score >= 50:
        status, reason = "Suspicious", "Suspicious Behavioral Pattern"
    else:
        status, reason = "Success", "Passed Gateway Safety Parameters"

    risk_score = round(float(risk_score), 2)
    return {
        "status": status,
        "reason": reason,
        "risk_score": risk_score,
        "rule_risk": rule_risk,
        "ml_risk": ml_risk,
        "ml_prediction": prediction,
        "card_type": card_type,
        "transaction_hour": transaction_hour,
        "country": country,
        "signals": signals,
        "ml_used": model is not None and encoder is not None,
    }
