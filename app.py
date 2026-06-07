from database.auth import register_user, login_user
from datetime import datetime
import streamlit as st
from database.db import init_db

init_db()
st.set_page_config(
    page_title="Smart E-Commerce Fraud Detection", page_icon="💳", layout="wide"
)

# ==========================
# SESSION VARIABLES
# ==========================


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "login_time" not in st.session_state:
    st.session_state.login_time = None

if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
# Hide sidebar before login

if not st.session_state.logged_in:

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
# ==========================
# SESSION TIMEOUT
# ==========================

if st.session_state.logged_in and st.session_state.login_time:

    seconds = (datetime.now() - st.session_state.login_time).seconds

    if seconds > 3600:

        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False

        st.warning("Session Expired. Please Login Again.")

        st.stop()

# ==========================
# HEADER IMAGE
# ==========================

# st.image(
# "https://images.unsplash.com/photo-1556740749-887f6717d7e4",
# use_container_width=True,
# )

st.markdown(
    """
<style>
.big-title{
    text-align:center;
    font-size:50px;
    font-weight:bold;
    color:#4F46E5;
}
.subtitle{
    text-align:center;
    font-size:20px;
    color:#94A3B8;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<p class="big-title">🛍️ Smart Shop</p>', unsafe_allow_html=True)

st.markdown(
    '<p class="subtitle">Secure Shopping Experience</p>', unsafe_allow_html=True
)

# ==========================
# ADMIN BUTTON
# ==========================

if not st.session_state.logged_in and not st.session_state.admin_login:

    col1, col2 = st.columns([9, 1])

    with col2:

        if st.button("🛡️ Admin"):

            st.session_state.admin_login = True
            st.rerun()

# ==========================
# ADMIN LOGIN
# ==========================

if st.session_state.admin_login:

    st.title("🛡️ Admin Login")

    admin_email = st.text_input("Admin Email")

    admin_password = st.text_input("Admin Password", type="password")

    if st.button("Admin Sign In"):

        if admin_email == "adminhere@gmail.com" and admin_password == "admin123":

            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.login_time = datetime.now()

            st.success("Admin Login Successful")

            st.switch_page("pages/admin.py")

        else:

            st.error("Invalid Admin Credentials")

    if st.button("Back To User Login"):

        st.session_state.admin_login = False
        st.rerun()

    st.stop()

# ==========================
# USER LOGIN / SIGNUP
# ==========================

if not st.session_state.logged_in:

    st.title("🛒 Welcome To Our Store")

    login_tab, signup_tab = st.tabs(["Login", "Signup"])

    # LOGIN

    with login_tab:

        email = st.text_input("Email", key="login_email")

        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):

            user = login_user(email, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.session_state.login_time = datetime.now()

                st.success("Login Successful")

                st.switch_page("pages/products.py")

            else:

                st.error("Invalid Credentials")

    # SIGNUP

    with signup_tab:

        name = st.text_input("Full Name", key="signup_name")

        signup_email = st.text_input("Email Address", key="signup_email")

        signup_password = st.text_input(
            "Password", type="password", key="signup_password"
        )

        if st.button("Create Account"):
            try:
                register_user(name, signup_email, signup_password)
                st.success("Account Created Successfully")
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================
# AFTER LOGIN
# ==========================

else:

    if st.session_state.is_admin:

        st.title("🛡️ Administrator Panel")

        st.success("Logged In As Administrator")

        if st.button("Open Admin Dashboard"):

            st.switch_page("pages/admin.py")

    else:

        st.switch_page("pages/products.py")

    st.divider()

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False

        st.rerun()

st.divider()

st.caption("© 2026 Smart Shop • Secure Payments ")
