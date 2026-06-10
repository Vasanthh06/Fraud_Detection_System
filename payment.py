import streamlit as st
import uuid
import re
import joblib
import pandas as pd
from datetime import datetime

# ============================================================
# 1. AUTHENTICATION CHECK
# ============================================================
if not st.session_state.get("logged_in"):
    st.error("Authentication Error: Please Login First")
    st.stop()

from database.logger import save_transaction
from database.auth import (
    increment_failed_payment_streak,
    reset_failed_payment_streak,
    get_failed_payment_streak,
)

# Initialize payment success state
if "payment_success" not in st.session_state:
    st.session_state.payment_success = False

user_email = st.session_state.get("user_email", "guest@shopzone.com")
current_streak = get_failed_payment_streak(user_email)

if current_streak >= 3:
    st.error(
        "🚨 Access Violations Triggered: Your account has been suspended due to consecutive payment gateway threshold failures. Session Terminated."
    )
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.stop()

# ============================================================
# UI THEME
# ============================================================
st.set_page_config(
    page_title="Secure Bank Payment Gateway", page_icon="💳", layout="centered"
)
st.markdown(
    """
    <style>
    .main { background-color: #0B1120; color: #F3F4F6; }
    .payment-card {
        background-color: #1E293B; border: 1px solid #334155; border-radius: 12px;
        padding: 2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); margin-bottom: 1.5rem;
    }
    .success-container {
        text-align: center; background-color: #1E293B; border: 1px solid #10B981;
        border-radius: 12px; padding: 3rem; margin-top: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.4);
    }
    .stButton>button[kind="primary"] {
        background-color: #10B981; color: white; border: none; font-size: 1.1rem;
        border-radius: 8px; padding: 0.75rem 1rem; width: 100%; font-weight: bold;
    }
    .stButton>button[kind="primary"]:hover { background-color: #059669; }
    .stButton>button[kind="secondary"] {
        background-color: #1E293B; color: #F3F4F6; border: 1px solid #334155;
        border-radius: 8px; padding: 0.5rem 1rem; width: 100%; transition: all 0.3s;
    }
    .stButton>button[kind="secondary"]:hover { background-color: #38BDF8; color: #0B1120; border-color: #38BDF8; }
    .cancel-btn .stButton>button {
        background-color: #ef4444 !important;
        color: white !important;
        border: 1px solid #ef4444 !important;
    }
    .cancel-btn .stButton>button:hover {
        background-color: #dc2626 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 2. CORE SECURITY FUNCTIONS
# ============================================================
def luhn_check(card_number):
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


def get_card_type(card_number):
    if card_number.startswith("4"):
        return "Visa"
    elif card_number.startswith("5"):
        return "MasterCard"
    elif card_number.startswith("6"):
        return "RuPay"
    elif card_number.startswith("34") or card_number.startswith("37"):
        return "American Express"
    return "Unknown"


# ============================================================
# 3. ML MODEL LOADING — FIXED: Safe loading with fallback
# ============================================================
@st.cache_resource
def load_ml_pipeline():
    try:
        model = joblib.load("models/ecommerce_fraud_model.pkl")
        encoder = joblib.load("models/ecommerce_encoder.pkl")
        return model, encoder
    except Exception as e:
        st.warning("ML models not found. Using rule-based fraud detection.")
        return None, None


model, encoder = load_ml_pipeline()

# ============================================================
# SUCCESS SCREEN
# ============================================================
if st.session_state.payment_success:
    st.markdown(
        """
        <div class="success-container">
            <h1 style="color: #10B981; font-size: 3.5rem; margin-bottom: 1rem;">🎉 Success!</h1>
            <h2 style="color: #F3F4F6;">✅ Thank You For Shopping With ShopZone</h2>
            <h4 style="color: #9CA3AF; margin-bottom: 1.5rem;">Your Order Has Been Placed Successfully</h4>
            <p style="color: #6B7280;">We appreciate your purchase.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🛍️ Continue Shopping", use_container_width=True, type="primary"):
            st.session_state.payment_success = False
            st.switch_page("products.py")

    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.admin_login = False
            st.session_state.login_time = None
            st.session_state.user_email = ""
            st.session_state.payment_success = False
            st.session_state.cart = []
            st.session_state.total_amount = 0
            st.switch_page("app.py")

    st.stop()

# ============================================================
# 4. PAYMENT FORM
# ============================================================
st.title("💳 Secure Bank Payment Gateway")

amount = st.session_state.get("total_amount", 0)

if amount == 0:
    st.warning("Your active shopping bag is empty.")

    # FIXED: Cancel button when cart is empty
    col_empty1, col_empty2 = st.columns(2)
    with col_empty1:
        if st.button("🛍️ Back to Products", use_container_width=True, type="primary"):
            st.switch_page("products.py")
    with col_empty2:
        st.markdown('<div class="cancel-btn">', unsafe_allow_html=True)
        if st.button("❌ Cancel Payment", use_container_width=True):
            st.session_state.cart = []
            st.session_state.total_amount = 0
            st.warning("Payment cancelled. Returning to store.")
            st.switch_page("products.py")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
else:
    st.subheader(f"Total Amount Payable: ₹{amount:,}")

st.markdown('<div class="payment-card">', unsafe_allow_html=True)

customer_name = st.text_input("Card Holder Name")

raw_card_input = st.text_input(
    "Card Number",
    placeholder="XXXX-XXXX-XXXX-XXXX",
    max_chars=16,
    help="Type your 16-digit card number",
)

col_exp, col_cvv = st.columns(2)
with col_exp:
    raw_expiry_input = st.text_input(
        "Expiry Date",
        placeholder="MM/YY",
        max_chars=5,
        help="Format: MM/YY",
    )
with col_cvv:
    cvv = st.text_input(
        "CVV/CVC",
        type="password",
        placeholder="•••",
        max_chars=3,
    )

clean_card = re.sub(r"\D", "", raw_card_input).strip() if raw_card_input else ""
clean_expiry = re.sub(r"\D", "", raw_expiry_input).strip() if raw_expiry_input else ""

if clean_card:
    card_type = get_card_type(clean_card)
    if card_type != "Unknown":
        st.caption(f"Network standard match verified: **{card_type} Card**")

country = "India"
failed_attempts = current_streak

st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    "🔒 Secured Protocol Endpoint • PCI-DSS Banking Vault Architecture Standard Active"
)
st.markdown("---")

# ============================================================
# 5. TRANSACTION PROCESSING
# ============================================================
col_pay, col_cancel = st.columns(2)

with col_pay:
    if st.button("Complete Secure Payment", type="primary", use_container_width=True):
        if (
            not customer_name.strip()
            or not clean_card
            or not clean_expiry
            or not cvv.strip()
        ):
            st.error(
                "Validation Error: All processing credential parameters are required."
            )
            st.stop()

        if len(clean_card) == 16:
            formatted_card = f"{clean_card[0:4]}-{clean_card[4:8]}-{clean_card[8:12]}-{clean_card[12:16]}"
        else:
            formatted_card = raw_card_input.strip()

        if len(clean_expiry) == 4:
            formatted_expiry = f"{clean_expiry[0:2]}/{clean_expiry[2:4]}"
        else:
            formatted_expiry = raw_expiry_input.strip()

        transaction_id = str(uuid.uuid4())[:8]
        cart = st.session_state.get("cart", [])
        product_names = (
            ", ".join([item["name"] for item in cart])
            if cart
            else "E-Commerce Goods Portfolio"
        )
        transaction_hour = datetime.now().hour
        device_type = "Web Browser Portal"
        masked_card = (
            f"**** **** **** {clean_card[-4:]}" if len(clean_card) >= 4 else "****"
        )

        # --- CHECK 1: CARD STRUCTURE ---
        if len(clean_card) != 16 or not clean_card.isdigit():
            increment_failed_payment_streak(user_email)
            new_streak = current_streak + 1
            save_transaction(
                transaction_id,
                customer_name,
                product_names,
                "INVALID STRUCTURE",
                amount,
                country,
                device_type,
                transaction_hour,
                new_streak,
                100.0,
                f"Malformed Input: Lockout [{new_streak}/3]",
                "Fraud",
            )

            if new_streak >= 3:
                st.error(
                    "🚨 Account Suspended: Critical payment credential errors detected. Access blocked for 24 hours."
                )
                st.session_state.logged_in = False
                st.rerun()
            else:
                st.error(
                    f"❌ Payment Declined: Invalid card layout. ({new_streak}/3 failed attempts)"
                )
            st.stop()

        # --- CHECK 2: LUHN VALIDATION ---
        if not luhn_check(clean_card):
            increment_failed_payment_streak(user_email)
            new_streak = current_streak + 1
            save_transaction(
                transaction_id,
                customer_name,
                product_names,
                masked_card,
                amount,
                country,
                device_type,
                transaction_hour,
                new_streak,
                100.0,
                f"Luhn Check Failed: Strike [{new_streak}/3]",
                "Fraud",
            )

            if new_streak >= 3:
                st.error(
                    "🚨 Account Suspended: Critical payment credential errors detected. Access blocked for 24 hours."
                )
                st.session_state.logged_in = False
                st.rerun()
            else:
                st.error(
                    f"❌ Payment Declined: Authorization failed. ({new_streak}/3 failed attempts)"
                )
            st.stop()

        # --- ML FRAUD DETECTION ---
        if model and encoder:
            try:
                country_encoded = encoder.transform([country])[0]
                input_df = pd.DataFrame(
                    [[amount, country_encoded, transaction_hour, failed_attempts]],
                    columns=[
                        "amount",
                        "country",
                        "transaction_hour",
                        "failed_attempts",
                    ],
                )
                prediction = model.predict(input_df)[0]
                probability = model.predict_proba(input_df)[0][1]
                risk_score = round(float(probability) * 100, 2)
            except Exception as e:
                prediction = 1 if (amount > 100000 or failed_attempts >= 2) else 0
                risk_score = 90.0 if prediction == 1 else 15.0
        else:
            prediction = 1 if (amount > 100000 or failed_attempts >= 2) else 0
            risk_score = 90.0 if prediction == 1 else 15.0

        # --- LOG AND DECIDE ---
        if prediction == 1 or risk_score >= 80.0:
            increment_failed_payment_streak(user_email)
            new_streak = current_streak + 1
            save_transaction(
                transaction_id,
                customer_name,
                product_names,
                masked_card,
                amount,
                country,
                device_type,
                transaction_hour,
                new_streak,
                risk_score,
                f"High-Risk ML Signal: Strike [{new_streak}/3]",
                "Fraud",
            )

            if new_streak >= 3:
                st.error(
                    "🚨 Account Suspended: Atypical execution pattern detected. Retries blocked for 24 hours."
                )
                st.session_state.logged_in = False
                st.rerun()
            else:
                st.error(
                    f"❌ Transaction Refused: Payment authorization failed. ({new_streak}/3 failed attempts)"
                )
        else:
            # SUCCESS PATH
            reset_failed_payment_streak(user_email)
            save_transaction(
                transaction_id,
                customer_name,
                product_names,
                masked_card,
                amount,
                country,
                device_type,
                transaction_hour,
                0,
                risk_score,
                "Passed Gateway Safety Parameters",
                "Genuine",
            )

            st.session_state.cart = []
            st.session_state.total_amount = 0
            st.session_state.payment_success = True
            st.rerun()

# FIXED: Cancel Payment Button
with col_cancel:
    st.markdown('<div class="cancel-btn">', unsafe_allow_html=True)
    if st.button("❌ Cancel Payment", use_container_width=True, type="secondary"):
        st.session_state.cart = []
        st.session_state.total_amount = 0
        st.warning("Payment process aborted. Returning to ShopZone store.")
        st.switch_page("products.py")
    st.markdown("</div>", unsafe_allow_html=True)
