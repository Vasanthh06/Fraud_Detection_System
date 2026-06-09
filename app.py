import re
from datetime import datetime
import streamlit as st
from database.db import init_db

# ============================================================
# 1. ALWAYS CALL THIS AT THE VERY TOP
# ============================================================
init_db()

# Safe to import auth modules
from database.auth import (
    get_failed_payment_streak,
    login_user,
    register_user,
    reset_password,
)

# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ShopZone | Premium Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 3. SESSION STATE DEFAULTS
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

if "username" not in st.session_state:
    st.session_state.username = "User"

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

# ============================================================
# 4. HIDE SIDEBAR BEFORE LOGIN
# ============================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 5. SESSION TIMEOUT (1 hour)
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
# 6. UNIFORM LIGHT THEME CSS
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Syne:wght@700;800&display=swap');

/* ===========================
   GLOBAL RESET & BASE
=========================== */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #f6f8fa; /* Modern Soft light background */
    color: #24292f;      /* Clean Dark text */
    font-family: 'Inter', sans-serif;
}

/* Remove default streamlit padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ===========================
   ANIMATED BACKGROUND GRID (Soft Light Contrast)
=========================== */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(9,105,218,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(9,105,218,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ===========================
   HERO BANNER
=========================== */
.hero-wrap {
    position: relative;
    text-align: center;
    padding: 56px 40px 48px;
    margin-bottom: 40px;
    border-radius: 24px;
    background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
    border: 1px solid #d0d7de;
    overflow: hidden;
    animation: fadeSlideDown 0.6s ease both;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.hero-badge {
    display: inline-block;
    background: rgba(9,105,218,0.1);
    border: 1px solid rgba(9,105,218,0.25);
    color: #0969da;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 50px;
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(38px, 6vw, 64px);
    font-weight: 800;
    color: #24292f;
    line-height: 1.1;
    margin: 0 0 12px;
    letter-spacing: -1px;
}
.hero-title span {
    background: linear-gradient(90deg, #0969da, #cf222e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 16px;
    color: #57606a;
    font-weight: 400;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}
.hero-pills {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 24px;
    flex-wrap: wrap;
}
.hero-pill {
    background: #ffffff;
    border: 1px solid #d0d7de;
    color: #57606a;
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 50px;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* ===========================
   SECTION HEADER
=========================== */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #24292f;
    margin-bottom: 20px;
    letter-spacing: -0.3px;
}

/* ===========================
   LOGIN / SIGNUP CARD
=========================== */
.login-card-wrap {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 32px 28px;
    animation: fadeSlideUp 0.5s ease both;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

/* ===========================
   STREAMLIT INPUT OVERRIDES
=========================== */
.stTextInput > label {
    color: #57606a !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
.stTextInput input {
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 12px !important;
    color: #24292f !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
}
.stTextInput input:focus {
    border-color: #0969da !important;
    box-shadow: 0 0 0 3px rgba(9,105,218,0.15) !important;
}

/* ===========================
   SIDEBAR LIGHT OVERRIDES
=========================== */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #d0d7de !important;
}
[data-testid="stSidebarNav"] label {
    color: #24292f !important;
}
[data-testid="stSidebarNav"] a span {
    color: #57606a !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #0969da !important;
    font-weight: bold !important;
}

/* ===========================
   TABS
=========================== */
.stTabs [data-baseweb="tab-list"] {
    background: #f6f8fa !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #d0d7de !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #57606a !important;
    padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: #0969da !important;
    color: white !important;
}

/* ===========================
   BUTTONS
=========================== */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    border-radius: 12px !important;
    border: 1px solid #d0d7de !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    background: #ffffff !important;
    color: #24292f !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    background-color: #f6f8fa !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

/* Redesign active triggers/primary action elements */
.stButton > button[type="primary"] {
    background: linear-gradient(135deg, #0969da, #054da7) !important;
    color: white !important;
    border: none !important;
}
.stButton > button[type="primary"]:hover {
    box-shadow: 0 6px 20px rgba(9,105,218,0.3) !important;
}

/* ===========================
   FEATURE / INFO CARDS
=========================== */
.feat-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.feat-title {
    font-weight: 700;
    font-size: 14px;
    color: #24292f;
    margin-bottom: 6px;
}
.feat-desc {
    font-size: 12px;
    color: #57606a;
}

/* ===========================
   STATS ROW
=========================== */
.stats-row {
    display: flex;
    gap: 12px;
    margin: 20px 0;
    flex-wrap: wrap;
}
.stat-box {
    flex: 1;
    min-width: 90px;
    background: rgba(9,105,218,0.06);
    border: 1px solid rgba(9,105,218,0.15);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #0969da;
}
.stat-label {
    font-size: 11px;
    color: #57606a;
}

/* ===========================
   DELIVERY PERKS BLOCK
=========================== */
.perks-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 16px 0;
}
.perk-row {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.perk-text { font-size: 13px; color: #57606a; }
.perk-text strong { color: #24292f; }

/* ===========================
   ADMIN GATE CARD
=========================== */
.admin-gate-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 36px 32px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
}
.admin-gate-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #24292f;
}

/* ===========================
   ADMIN COMMAND CENTER
=========================== */
.admin-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f6f8fa 100%);
    border: 1px solid #d0d7de;
    border-radius: 24px;
    padding: 48px 40px;
    text-align: center;
    margin-bottom: 32px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.admin-hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 800;
    color: #24292f;
}

/* ===========================
   FORGOT PASSWORD PAGE
=========================== */
.fp-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
}
.fp-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #24292f;
}

/* Metric overrides */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 14px 16px;
}
[data-testid="stMetricValue"] {
    color: #0969da !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 7. CASE A: ADMIN IS LOGGED IN (FraudGuard Command Center)
# ============================================================
if st.session_state.logged_in and st.session_state.is_admin:

    st.markdown(
        """
        <div class="admin-hero">
            <div style="margin-bottom:12px;">
                <span class="admin-status-dot"></span>
                <span style="font-size:12px;color:#22c55e;font-weight:600;letter-spacing:1px;">ALL SYSTEMS OPERATIONAL</span>
            </div>
            <div class="admin-hero-title">FraudGuard Command Center 🛡️</div>
            <div class="admin-hero-sub">Real-Time Transaction Integrity &amp; Machine Learning Guardrails Active</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1.2, 1.8], gap="large")

    with col_right:
        st.markdown(
            '<div class="admin-section-header">System Operations</div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "🛡️ Open Full Admin Dashboard Module",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page("pages/admin.py")

        st.write("")
        if st.button("🔴 Terminate Admin Session", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.login_time = None
            st.session_state.admin_login = False
            st.session_state.user_email = ""
            st.rerun()

    st.divider()

    st.markdown(
        '<div class="admin-section-header">Engine Pipeline Overview</div>',
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
            <div class="feat-card">
                <div class="feat-icon">🛡️</div>
                <div class="feat-title">Risk Isolation</div>
                <p class="feat-desc">Evaluates location &amp; device data dynamically on every checkout event.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="feat-card">
                <div class="feat-icon">🤖</div>
                <div class="feat-title">ML Inference</div>
                <p class="feat-desc">Scikit-learn classifier scores fraud probability on each transaction in real time.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="feat-card">
                <div class="feat-icon">📊</div>
                <div class="feat-title">Audit Logger</div>
                <p class="feat-desc">Every checkout stream is written directly to the encrypted SQLite ledger.</p>
            </div>""",
            unsafe_allow_html=True,
        )

# ============================================================
# 8. CASE B: NORMAL USER OR NOT LOGGED IN
# ============================================================
else:
    # ── Hero Banner ──────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">✦ Premium Marketplace</div>
            <div class="hero-title">Shop<span>Zone</span> 🛍️</div>
            <div class="hero-subtitle">Thousands of products. Fast delivery. A checkout that just works.</div>
            <div class="hero-pills">
                <span class="hero-pill">✔ Electronics</span>
                <span class="hero-pill">✔ Fashion</span>
                <span class="hero-pill">✔ Home Decor</span>
                <span class="hero-pill">✔ Books</span>
                <span class="hero-pill">✔ Accessories</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Staff Login (top-right ghost button) ─────────────────
    if not st.session_state.admin_login:
        top_left, top_right = st.columns([9, 1])
        with top_right:
            st.markdown('<div class="staff-btn-wrap">', unsafe_allow_html=True)
            if st.button("🔒 Staff", use_container_width=True):
                st.session_state.admin_login = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Admin Verification Gate ───────────────────────────────
    if not st.session_state.logged_in and st.session_state.admin_login:
        st.markdown("<br>", unsafe_allow_html=True)
        left, center, right = st.columns([2, 1.4, 2])

        with center:
            st.markdown(
                """
                <div class="admin-gate-card">
                    <span class="admin-lock-icon">🔐</span>
                    <div class="admin-gate-title">Admin Verification Gate</div>
                    <div class="admin-gate-sub">Authorised personnel only</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.write("")

            # Wrapped Admin Credentials in a form
            with st.form("admin_gate_form"):
                admin_email = st.text_input("Admin Email", key="admin_email_input")
                admin_password = st.text_input(
                    "Admin Password", type="password", key="admin_pass_input"
                )
                # FIX: Fixed the typo 'st.st.form_submit_button' down to 'st.form_submit_button'
                submit_admin = st.form_submit_button(
                    "🚀 Authenticate", use_container_width=True
                )

            c1, c2 = st.columns(2)
            with c1:
                if submit_admin:
                    if (
                        admin_email.strip() == "adminhere@gmail.com"
                        and admin_password.strip() == "admin123"
                    ):
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.username = "Administrator"
                        st.session_state.user_email = "adminhere@gmail.com"
                        st.session_state.login_time = datetime.now()
                        st.success("Welcome back, Administrator ✓")
                        st.rerun()
                    else:
                        st.error("Invalid administrative credentials.")
            with c2:
                if st.button("⬅ Back", use_container_width=True):
                    st.session_state.admin_login = False
                    st.rerun()

        # Stop rendering the rest of the page while gate is open
        st.stop()

    # ── Forgot Password ───────────────────────────────────────
    if st.session_state.show_forgot_password:
        st.markdown("<br>", unsafe_allow_html=True)
        _, center, _ = st.columns([1, 2, 1])
        with center:
            st.markdown(
                """
                <div class="fp-card">
                    <div class="fp-title">🔑 Reset Password</div>
                    <div class="fp-sub">Enter your registered email and choose a new password.</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.write("")

            with st.form("forgot_password_form"):
                email = st.text_input("Registered Email")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_fp = st.form_submit_button(
                    "Reset Password", use_container_width=True
                )

            if submit_fp:
                if not email or not new_password or not confirm_password:
                    st.error("Please fill all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success = reset_password(email, new_password)
                    if success:
                        st.success(
                            "✅ Password reset successfully! You can now log in."
                        )
                    else:
                        st.error("❌ No account found with that email.")

            st.write("")
            if st.button("⬅ Back to Login", use_container_width=True):
                st.session_state.show_forgot_password = False
                st.rerun()

        st.stop()

    # ── Main Login + Info Layout ──────────────────────────────
    col_login, col_info = st.columns([1.1, 1.9], gap="large")

    # LEFT — Login / Signup card
    with col_login:
        st.markdown(
            '<div class="section-header">Customer Access</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="login-card-wrap">', unsafe_allow_html=True)

        login_tab, signup_tab = st.tabs(["🔒 Sign In", "✨ Create Account"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email address", key="login_email")
                password = st.text_input(
                    "Password", type="password", key="login_password"
                )
                submit_login = st.form_submit_button(
                    "Login to ShopZone →", use_container_width=True
                )

            if submit_login:
                if not email.strip() or not password.strip():
                    st.error("Please fill out all fields.")
                else:
                    user_email_clean = email.strip()
                    if get_failed_payment_streak(user_email_clean) >= 3:
                        st.error("🚨 Account temporarily suspended. Contact support.")
                    else:
                        user = login_user(user_email_clean, password.strip())
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.is_admin = False
                            st.session_state.user_email = user_email_clean
                            st.session_state.username = user_email_clean.split("@")[
                                0
                            ].capitalize()
                            st.session_state.login_time = datetime.now()
                            st.success("Login successful!")
                            st.switch_page("pages/products.py")
                        else:
                            st.error("Incorrect email or password.")

            st.write("")
            if st.button("Forgot password?", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()

        with signup_tab:
            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("Full Name", key="signup_name")
                signup_email = st.text_input("Email Address", key="signup_email")
                signup_phone = st.text_input("Phone Number", key="signup_phone")
                signup_password = st.text_input(
                    "Password", type="password", key="signup_password"
                )
                submit_signup = st.form_submit_button(
                    "Register Account", use_container_width=True
                )

            if submit_signup:
                if (
                    not name.strip()
                    or not signup_email.strip()
                    or not signup_phone.strip()
                    or not signup_password.strip()
                ):
                    st.error("All fields, including Phone Number, are required.")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success = register_user(
                        name=name.strip(),
                        email=signup_email.strip(),
                        phone=signup_phone.strip(),
                        password=signup_password.strip(),
                    )
                    if success:
                        st.success(
                            "Registration Successful! Please switch to the Login tab."
                        )
                    else:
                        st.error("This email address is already in use.")

    # RIGHT — Shop info
    with col_info:
        st.markdown(
            """
            <h1 style='font-family:"Syne",sans-serif;font-size:clamp(28px,3.5vw,44px);
                        font-weight:800;color:#24292f;line-height:1.15;
                        letter-spacing:-0.5px;margin-bottom:6px;'>
                Welcome to<br><span style='background:linear-gradient(90deg,#0969da,#cf222e);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;'>ShopZone</span>
            </h1>
            <p style='color:#57606a;font-size:14px;margin-bottom:20px;'>
                Your premium one-stop marketplace — from daily essentials to the latest tech.
            </p>
        """,
            unsafe_allow_html=True,
        )

        # Stats
        st.markdown(
            """
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-num">1K+</div>
                    <div class="stat-label">Products</div>
                </div>
                <div class="stat-box">
                    <div class="stat-num">5K+</div>
                    <div class="stat-label">Customers</div>
                </div>
                <div class="stat-box">
                    <div class="stat-num">3.5K</div>
                    <div class="stat-label">Orders</div>
                </div>
                <div class="stat-box">
                    <div class="stat-num">4.8★</div>
                    <div class="stat-label">Rating</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Perks
        st.markdown(
            """
            <div class="perks-grid">
                <div class="perk-row">
                    <div class="perk-icon">🚚</div>
                    <div class="perk-text"><strong>Free Shipping</strong> on orders above $50</div>
                </div>
                <div class="perk-row">
                    <div class="perk-icon">↩️</div>
                    <div class="perk-text"><strong>Easy Returns</strong> within 30 days window</div>
                </div>
                <div class="perk-row">
                    <div class="perk-icon">🔒</div>
                    <div class="perk-text"><strong>Secure Payments</strong> protected by AES-256 ledger</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )
