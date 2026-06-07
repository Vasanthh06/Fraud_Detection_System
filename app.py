import streamlit as st
from datetime import datetime

# ============================================================
# INIT DB FIRST — before any other database imports
# ============================================================
from database.db import init_db

init_db()

# ============================================================
# NOW safe to import auth
# ============================================================
from database.auth import register_user, login_user

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Smart E-Commerce Fraud Detection",
    page_icon="💳",
    layout="wide",
)

# ============================================================
# SESSION STATE DEFAULTS
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "login_time" not in st.session_state:
    st.session_state.login_time = None

if "admin_login" not in st.session_state:
    st.session_state.admin_login = False

if "cart" not in st.session_state:
    st.session_state.cart = []

if "total_amount" not in st.session_state:
    st.session_state.total_amount = 0

# ============================================================
# HIDE SIDEBAR BEFORE LOGIN
# ============================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SESSION TIMEOUT (1 hour)
# ============================================================
if st.session_state.logged_in and st.session_state.login_time:
    seconds = (datetime.now() - st.session_state.login_time).seconds
    if seconds > 3600:
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False
        st.warning("Session Expired. Please Login Again.")
        st.stop()

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>
    .big-title {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        color: #4F46E5;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #94A3B8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="big-title">🛍️ Smart Shop</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Secure Shopping Experience</p>', unsafe_allow_html=True
)

# ============================================================
# ADMIN BUTTON (top right, only when not logged in)
# ============================================================
if not st.session_state.logged_in and not st.session_state.admin_login:
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🛡️ Admin"):
            st.session_state.admin_login = True
            st.rerun()

# ============================================================
# ADMIN LOGIN SCREEN
# ============================================================
if st.session_state.admin_login:

    st.title("🛡️ Admin Login")

    admin_email = st.text_input("Admin Email", key="admin_email_input")
    admin_password = st.text_input(
        "Admin Password", type="password", key="admin_pass_input"
    )

    if st.button("Admin Sign In"):
        if (
            admin_email.strip() == "adminhere@gmail.com"
            and admin_password.strip() == "admin123"
        ):
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

# ============================================================
# USER LOGIN / SIGNUP
# ============================================================
if not st.session_state.logged_in:

    st.title("🛒 Welcome To Our Store")

    login_tab, signup_tab = st.tabs(["Login", "Signup"])

    # ---------- LOGIN ----------
    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not email.strip() or not password.strip():
                st.error("Please enter both email and password.")
            else:
                user = login_user(email.strip(), password.strip())
                if user:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.login_time = datetime.now()
                    st.success("Login Successful")
                    st.switch_page("pages/products.py")
                else:
                    st.error("Invalid Credentials")

    # ---------- SIGNUP ----------
    with signup_tab:
        name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_password = st.text_input(
            "Password", type="password", key="signup_password"
        )

        if st.button("Create Account"):
            if (
                not name.strip()
                or not signup_email.strip()
                or not signup_password.strip()
            ):
                st.error("All fields are required.")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success = register_user(
                    name.strip(), signup_email.strip(), signup_password.strip()
                )
                if success:
                    st.success("Account Created Successfully! Please login.")
                else:
                    st.error("Email already registered. Please use a different email.")

# ============================================================
# AFTER LOGIN (admin or user)
# ============================================================
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
        st.session_state.cart = []
        st.rerun()

st.divider()
st.caption("© 2026 Smart Shop • Secure Payments")
