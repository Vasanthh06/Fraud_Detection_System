import streamlit as st
from database.auth import reset_password

st.set_page_config(page_title="Reset Password", page_icon="🔐", layout="centered")

st.markdown(
    """
<style>
section[data-testid="stSidebar"]{
    display:none;
}
</style>
""",
    unsafe_allow_html=True,
)
import streamlit as st
from database.auth import reset_password

# Hide sidebar completely
st.markdown(
    """
<style>
section[data-testid="stSidebar"]{
    display:none;
}
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(page_title="Reset Password", page_icon="🔐", layout="centered")

st.title("🔐 Forgot Password")

email = st.text_input("Registered Email")

new_password = st.text_input("New Password", type="password")

confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Reset Password", use_container_width=True, type="primary"):

    if not email or not new_password or not confirm_password:
        st.error("Please fill all fields.")

    elif new_password != confirm_password:
        st.error("Passwords do not match.")

    elif len(new_password) < 6:
        st.error("Password must contain at least 6 characters.")

    else:
        success = reset_password(email.strip(), new_password.strip())

        if success:
            st.success("✅ Password Reset Successfully")

            st.info("You can now login with your new password.")

            if st.button("⬅ Back To Login", use_container_width=True):
                st.switch_page("app.py")

        else:
            st.error("❌ Email not found")
