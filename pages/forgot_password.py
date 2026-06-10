import streamlit as st
from database.auth import reset_password

st.set_page_config(page_title="Reset Password", page_icon="🔐", layout="centered")

st.title("🔐 Forgot Password")

# FIXED: Accept email OR phone number
identifier = st.text_input(
    "Registered Email or Phone Number", placeholder="email@gmail.com or 9876543210"
)

new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Reset Password", use_container_width=True, type="primary"):
    if not identifier or not new_password or not confirm_password:
        st.error("Please fill all fields.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    elif len(new_password) < 6:
        st.error("Password must contain at least 6 characters.")
    else:
        # FIXED: Reset by email OR phone
        success = reset_password(identifier.strip(), new_password.strip())
        if success:
            st.success("✅ Password Reset Successfully")
            st.info("You can now login with your new password.")
            if st.button("⬅ Back To Login", use_container_width=True):
                st.switch_page("app.py")
        else:
            st.error("❌ Email or Phone number not found")
