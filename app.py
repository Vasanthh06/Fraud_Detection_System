import re
from datetime import datetime
import streamlit as st
from database.db import init_db

# ============================================================
# 1. ALWAYS CALL THIS AT THE VERY TOP
# ============================================================
init_db()

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
# 5. SESSION TIMEOUT (1 hour) — FIXED: use total_seconds()
# ============================================================
if st.session_state.logged_in and st.session_state.login_time:
    elapsed = (datetime.now() - st.session_state.login_time).total_seconds()
    if elapsed > 3600:
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False
        st.session_state.cart = []
        st.session_state.total_amount = 0
        st.session_state.user_email = ""
        st.warning("Session Expired. Please Login Again.")
        st.stop()

# ============================================================
# 6. CSS — YOUR ORIGINAL UI + ENHANCED BUTTONS
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Syne:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #f6f8fa;
    color: #24292f;
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

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

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #24292f;
    margin-bottom: 20px;
    letter-spacing: -0.3px;
}

.login-card-wrap {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 32px 28px;
    animation: fadeSlideUp 0.5s ease both;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

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

.stButton > button {
    width: 100% !important;
    height: 48px !important;
    border-radius: 12px !important;
    border: none !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
    cursor: pointer !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0969da 0%, #054da7 50%, #0969da 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(9,105,218,0.35) !important;
    background-size: 200% 200% !important;
    animation: gradientShift 3s ease infinite !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(9,105,218,0.5) !important;
    filter: brightness(1.1) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #57606a !important;
    border: 1px solid #d0d7de !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f6f8fa !important;
    color: #24292f !important;
    border-color: #0969da !important;
    box-shadow: 0 4px 12px rgba(9,105,218,0.1) !important;
    transform: translateY(-1px) !important;
}

.staff-btn .stButton > button {
    background: linear-gradient(135deg, #24292f 0%, #1a1f2e 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 12px !important;
    height: 38px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}
.staff-btn .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
    filter: brightness(1.2) !important;
}

.feat-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
}
.feat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    border-color: #0969da;
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
    transition: all 0.3s ease;
}
.stat-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(9,105,218,0.1);
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
    transition: all 0.3s ease;
}
.perk-row:hover {
    border-color: #0969da;
    box-shadow: 0 2px 8px rgba(9,105,218,0.08);
    transform: translateX(4px);
}
.perk-text { font-size: 13px; color: #57606a; }
.perk-text strong { color: #24292f; }

.admin-gate-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 36px 32px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}
.admin-gate-card:hover {
    box-shadow: 0 15px 50px rgba(0,0,0,0.12);
}
.admin-gate-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #24292f;
}

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

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 14px 16px;
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    border-color: #0969da;
    box-shadow: 0 2px 8px rgba(9,105,218,0.1);
}
[data-testid="stMetricValue"] {
    color: #0969da !important;
}

@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 7. DEFINE PAGES FOR NAVIGATION (app.py NOT included)
# ============================================================
products_page = st.Page("pages/products.py", title="Products", icon="🛍️")
cart_page = st.Page("pages/cart.py", title="Cart", icon="🛒")
payment_page = st.Page("pages/payment.py", title="Payment", icon="💳")
admin_page = st.Page("pages/admin.py", title="Admin Dashboard", icon="🛡️")
forgot_password_page = st.Page(
    "pages/forgot_password.py", title="Reset Password", icon="🔑"
)

# ============================================================
# 8. ROUTING LOGIC
# ============================================================
if not st.session_state.logged_in:
    # NOT LOGGED IN: Show login form
    if st.session_state.show_forgot_password:
        # Show forgot password in navigation (hidden sidebar)
        pg = st.navigation([forgot_password_page], position="hidden")
        pg.run()
    else:
        # Show login form directly (no navigation)
        # Hero Banner
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

        # Staff Login button
        if not st.session_state.admin_login:
            top_left, top_right = st.columns([9, 1])
            with top_right:
                st.markdown('<div class="staff-btn">', unsafe_allow_html=True)
                if st.button("🔒 Staff", use_container_width=True):
                    st.session_state.admin_login = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # Admin Verification Gate
        if not st.session_state.logged_in and st.session_state.admin_login:
            st.markdown("<br>", unsafe_allow_html=True)
            left, center, right = st.columns([2, 1.4, 2])

            with center:
                st.markdown(
                    """
                    <div class="admin-gate-card">
                        <div style="font-size:36px;margin-bottom:12px;">🔐</div>
                        <div class="admin-gate-title">Admin Verification Gate</div>
                        <div style="font-size:12px;color:#57606a;margin-bottom:24px;">Authorised personnel only</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                st.write("")

                with st.form("admin_gate_form"):
                    admin_email = st.text_input("Admin Email", key="admin_email_input")
                    admin_password = st.text_input(
                        "Admin Password", type="password", key="admin_pass_input"
                    )
                    submit_admin = st.form_submit_button(
                        "🚀 Authenticate", use_container_width=True
                    )

                c1, c2 = st.columns(2)
                with c1:
                    if submit_admin:
                        import os

                        admin_email_env = os.getenv(
                            "ADMIN_EMAIL", "adminhere@gmail.com"
                        )
                        admin_password_env = os.getenv("ADMIN_PASSWORD", "admin123")
                        if (
                            admin_email.strip() == admin_email_env
                            and admin_password.strip() == admin_password_env
                        ):
                            st.session_state.logged_in = True
                            st.session_state.is_admin = True
                            st.session_state.username = "Administrator"
                            st.session_state.user_email = admin_email.strip()
                            st.session_state.login_time = datetime.now()
                            st.success("Welcome back, Administrator ✓")
                            st.rerun()
                        else:
                            st.error("Invalid administrative credentials.")
                with c2:
                    if st.button("⬅ Back", use_container_width=True):
                        st.session_state.admin_login = False
                        st.rerun()

            st.stop()

        # Main Login + Info Layout
        col_login, col_info = st.columns([1.1, 1.9], gap="large")

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
                            st.error(
                                "🚨 Account temporarily suspended. Contact support."
                            )
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
                                st.rerun()
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

            st.markdown("</div>", unsafe_allow_html=True)

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

            st.markdown(
                """
                <div class="perks-grid">
                    <div class="perk-row">
                        <div style="font-size:18px;">🚚</div>
                        <div class="perk-text"><strong>Free Shipping</strong> on orders above $50</div>
                    </div>
                    <div class="perk-row">
                        <div style="font-size:18px;">↩️</div>
                        <div class="perk-text"><strong>Easy Returns</strong> within 30 days window</div>
                    </div>
                    <div class="perk-row">
                        <div style="font-size:18px;">🔒</div>
                        <div class="perk-text"><strong>Secure Payments</strong> protected by AES-256 ledger</div>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

elif st.session_state.logged_in and st.session_state.is_admin:
    # ADMIN: Show admin dashboard with navigation
    pg = st.navigation([admin_page], position="sidebar")
    pg.run()

else:
    # NORMAL USER: Show products, cart, payment in sidebar
    pg = st.navigation(
        {"Shop": [products_page, cart_page, payment_page]}, position="sidebar"
    )
    pg.run()
