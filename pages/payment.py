import streamlit as st
import uuid
import re
import joblib
import pandas as pd
from datetime import datetime

if not st.session_state.get("logged_in"):
    st.error("Please Login First")
    st.stop()

from database.logger import save_transaction

# ==========================================

# LUHN VALIDATION

# ==========================================


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


# ==========================================

# CARD TYPE

# ==========================================


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


# ==========================================

# LOAD MODEL

# ==========================================

model = joblib.load("models/ecommerce_fraud_model.pkl")

encoder = joblib.load("models/ecommerce_encoder.pkl")

st.title("💳 Secure Payment Gateway")

amount = st.session_state.get("total_amount", 0)

if amount == 0:
    st.warning("Please add products to your cart first.")

else:
    st.subheader(f"Total Amount: ₹{amount:,}")

customer_name = st.text_input("Card Holder Name")

card_number = st.text_input(
    "Card Number", placeholder="1234-5678-9012-3456", help="Enter 16-digit card number"
)

if card_number:

    temp = card_number.replace("-", "")

    if temp.startswith("4"):
        st.success("💳 Visa Card")

    elif temp.startswith("5"):
        st.success("💳 MasterCard")

    elif temp.startswith("6"):
        st.success("💳 RuPay Card")

expiry = st.text_input("Expiry Date (MM/YY)", placeholder="12/28")

cvv = st.text_input("CVV", type="password", placeholder="123")
st.markdown("### 💳 Card Preview")

preview_name = customer_name if customer_name else "YOUR NAME"

preview_card = card_number if card_number else "XXXX-XXXX-XXXX-XXXX"

preview_expiry = expiry if expiry else "MM/YY"

st.info(f"""
Card Holder : {preview_name}

Card Number : {preview_card}

Expiry : {preview_expiry}
""")

country = st.selectbox("Country", ["India", "USA", "China", "Russia", "Other"])

failed_attempts = st.number_input(
    "Previous Failed Attempts", min_value=0, max_value=10, value=0
)
st.success("🔒 SSL Secured Payment")

st.info("""
✔ PCI DSS Compliant

✔ Encrypted Banking Gateway

✔ Fraud Detection Enabled

✔ Secure Transaction Monitoring
""")
if st.button("Pay Now"):

    if customer_name.strip() == "":

        st.error("Card Holder Name Required")
        st.stop()

    if not customer_name.replace(" ", "").isalpha():

        st.error("Name must contain letters only")
        st.stop()

    clean_card = card_number.replace("-", "")

    if not clean_card.isdigit():

        st.error("Card Number must contain digits only")
        st.stop()

    if len(clean_card) != 16:

        st.error("Card Number must contain exactly 16 digits")
        st.stop()

    if len(set(clean_card)) == 1:

        st.error("Invalid Card Number")
        st.stop()

    if clean_card in ["1234567890123456", "9876543210987654"]:

        st.error("Sequential Card Numbers Not Allowed")
        st.stop()

    if not cvv.isdigit():

        st.error("CVV must contain digits only")
        st.stop()

    if len(cvv) != 3:

        st.error("CVV must contain exactly 3 digits")
        st.stop()

    pattern = r"^(0[1-9]|1[0-2])\/([0-9]{2})$"

    if not re.match(pattern, expiry):

        st.error("Expiry must be MM/YY format")
        st.stop()

    cart = st.session_state.get("cart", [])

    product_names = ", ".join([item["name"] for item in cart])

    transaction_hour = datetime.now().hour

    device_type = "Desktop"

    # INVALID CARD CHECK

    if not luhn_check(clean_card):
        transaction_id = str(uuid.uuid4())[:8]

        save_transaction(
            transaction_id,
            customer_name,
            product_names,
            "INVALID CARD",
            amount,
            country,
            device_type,
            transaction_hour,
            failed_attempts,
            100,
            "Failed Luhn Validation",
            "Rejected",
        )

        st.error("🚨 Invalid Card Number.\n\nTransaction Logged As Rejected.")

        st.stop()

    # ==================================
    # ML PREDICTION
    # ==================================

    country_encoded = encoder.transform([country])[0]

    input_df = pd.DataFrame(
        [[amount, country_encoded, transaction_hour, failed_attempts]],
        columns=["amount", "country", "transaction_hour", "failed_attempts"],
    )

    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0][1]

    risk_score = round(probability * 100, 2)

    fraud_reasons = []

    if amount > 200000:
        fraud_reasons.append("High Amount")

    if failed_attempts >= 5:
        fraud_reasons.append("Multiple Failed Attempts")

    if country in ["Russia", "China"]:
        fraud_reasons.append("High Risk Country")

    if transaction_hour >= 0 and transaction_hour <= 4:
        fraud_reasons.append("Midnight Transaction")

    fraud_reason_text = ", ".join(fraud_reasons)

    transaction_id = str(uuid.uuid4())[:8]

    masked_card = "**** **** **** " + clean_card[-4:]

    card_type = get_card_type(clean_card)

    if prediction == 1:

        status = "Fraud"

        st.error(f"🚨 Fraud Detected\n\nFraud Probability: {risk_score}%")

    else:

        status = "Genuine"

        st.success(f"✅ Genuine Transaction\n\nFraud Probability: {risk_score}%")

    save_transaction(
        transaction_id,
        customer_name,
        product_names,
        masked_card,
        amount,
        country,
        device_type,
        transaction_hour,
        failed_attempts,
        risk_score,
        fraud_reason_text,
        status,
    )

    st.divider()

    st.subheader("🧾 Payment Receipt")

    st.write("Transaction ID:", transaction_id)

    st.write("Customer:", customer_name)

    st.write("Products:", product_names)

    st.write("Card:", masked_card)

    st.write("Card Type:", card_type)

    st.write("Amount:", f"₹{amount:,}")

    st.write("Country:", country)

    st.write("Device:", device_type)

    st.write("Transaction Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.write("Fraud Probability:", f"{risk_score}%")

    st.write("Fraud Reasons:", fraud_reason_text if fraud_reason_text else "None")

    st.write("Status:", status)

    st.session_state.cart = []
