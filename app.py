import streamlit as st
from datetime import datetime
from database.db import init_db

# ============================================================
# 1. ALWAYS CALL THIS AT THE VERY TOP
# ============================================================
init_db()

# Safe to import auth modules
from database.auth import register_user, login_user, get_failed_payment_streak

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

# ============================================================
# 4. HIDE SIDEBAR BEFORE LOGIN
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
# 6. CUSTOM CSS FOR THE DYNAMIC LOOK
# ============================================================
st.markdown(
    """
<style>

/* ===========================
PAGE BACKGROUND
=========================== */

.stApp{
    background: linear-gradient(
        135deg,
        #eef4ff,
        #f8fbff
    );
}

/* ===========================
TOP HERO BANNER
=========================== */

.store-banner {
    background: linear-gradient(
        135deg,
        #4f46e5,
        #2563eb
    );

    /* 1. Reduced internal padding to shrink the height */
    padding: 20px 38px; 

    /* 2. Optional: Limits how wide the banner stretches across the screen */
    max-width: 600px;   
    
    /* 3. Centers the card horizontally and keeps the 35px bottom spacing */
    margin: 0 auto 35px auto; 

    border-radius: 20px;
    text-align: center;
    color: white;
    
    box-shadow: 0 15px 40px rgba(79, 70, 229, .25);
}
.hero-title{
    font-size:65px;
    font-weight:600;
    color:white;
}

.hero-subtitle{
    font-size:20px;
    color:#e2e8f0;
}

/* ===========================
SECTION TITLE
=========================== */

.section-header{
    font-size:34px;
    font-weight:800;
    color:#1e293b;
    margin-bottom:20px;
}

/* ===========================
LOGIN CARD
=========================== */

[data-testid="stVerticalBlock"] div:has(> .stTabs){

    background:rgba(255,255,255,.85);

    backdrop-filter:blur(15px);

    border-radius:25px;

    padding:30px;

    box-shadow:
    0 10px 35px rgba(0,0,0,.08);

    border:1px solid rgba(255,255,255,.6);
}

/* ===========================
INPUT BOXES
=========================== */

.stTextInput input{

    border-radius:15px !important;

    border:2px solid #dbe4ff !important;

    padding:14px !important;

    background:white !important;

    font-size:16px !important;
}

.stTextInput input:focus{

    border:2px solid #4f46e5 !important;
}

/* ===========================
BUTTONS
=========================== */

.stButton button{

    width:100%;

    height:55px;

    border-radius:15px !important;

    border:none !important;

    font-size:16px;

    font-weight:700;

    transition:.3s;
}

/* Login Button */

.stButton button[kind="primary"]{

    background:
    linear-gradient(
        90deg,
        #4f46e5,
        #2563eb
    ) !important;

    color:white !important;
}

/* Hover */

.stButton button:hover{

    transform:translateY(-2px);

    box-shadow:
    0 10px 25px rgba(79,70,229,.35);
}

/* ===========================
FEATURE CARD
=========================== */

.feature-card{

    background:white;

    border-radius:20px;

    padding:25px;

    text-align:center;

    box-shadow:
    0 6px 25px rgba(0,0,0,.06);

    margin-bottom:15px;

    transition:.3s;
}

.feature-card:hover{

    transform:translateY(-6px);
}

/* ===========================
TABS
=========================== */

.stTabs [data-baseweb="tab"]{

    font-size:17px;
    font-weight:700;
}

/* ===========================
SUCCESS
=========================== */

.stSuccess{

    border-radius:15px;
}

/* ===========================
INFO
=========================== */

.stInfo{

    border-radius:15px;
}

/* ===========================
ADMIN BANNER
=========================== */

.admin-banner{

    background:
    linear-gradient(
        135deg,
        #0f172a,
        #1e293b
    );

    padding:40px;

    border-radius:25px;

    color:white;

    text-align:center;

    margin-bottom:30px;
}

.admin-section-header{

    font-size:28px;

    font-weight:800;

    color:#06b6d4;

    margin-bottom:20px;
}

</style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>

/* ALL BUTTONS */
.stButton > button{
    width:100%;
    height:58px;
    border:none;
    border-radius:16px;
    color:white !important;
    font-size:16px;
    font-weight:700;
    background:linear-gradient(
        135deg,
        #4f46e5,
        #2563eb
    ) !important;

    position:relative;
    overflow:hidden;
    transition:all .4s ease;
}

/* SHINE EFFECT */
.stButton > button::after{
    content:"";
    position:absolute;
    top:0;
    left:-120%;
    width:60%;
    height:100%;

    background:linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,.35),
        transparent
    );

    transform:skewX(-25deg);
}

/* HOVER ANIMATION */
.stButton > button:hover::after{
    left:150%;
    transition:.8s;
}

.stButton > button:hover{
    transform:translateY(-4px);
    box-shadow:
    0 12px 25px rgba(79,70,229,.35);
}

/* CLICK EFFECT */
.stButton > button:active{
    transform:scale(.98);
}

</style>
""",
    unsafe_allow_html=True,
)
# ============================================================
# 7. CASE A: ADMIN IS LOGGED IN (Show the Secret Security Dashboard)
# ============================================================
if st.session_state.logged_in and st.session_state.is_admin:

    st.markdown(
        """
        <div class="admin-banner">
            <div class="hero-title">FraudGuard Command Center 🛡️</div>
            <div class="hero-subtitle">Real-Time Transaction Integrity & Machine Learning Guardrails Active</div>
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
        '<div class="admin-section-header">Innovative Engine Pipeline Overview</div>',
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            '<div class="feature-card"><strong>🛡️ Risk Isolation</strong><p style="font-size:13px; color:#6c757d; margin-top:5px;">Evaluates location data dynamically on checkout.</p></div>',
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            '<div class="feature-card"><strong>🤖 ML Inference</strong><p style="font-size:13px; color:#6c757d; margin-top:5px;">Engineered using scikit-learn model classifying fraud patterns.</p></div>',
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            '<div class="feature-card"><strong>📊 Audit Logger</strong><p style="font-size:13px; color:#6c757d; margin-top:5px;"> checkout streams directly into encrypted SQLite system ledger.</p></div>',
            unsafe_allow_html=True,
        )

# ============================================================
# 8. CASE B: NORMAL USER OR NOT LOGGED IN (Show Standard Clean Store UI)
# ============================================================
else:
    # Standard Customer Storefront Header Banner
    st.markdown(
        """
        <div class="store-banner">
            <div class="hero-title">ShopZone 🛍️</div>
            <div class="hero-subtitle">Premium Goods • Fast Delivery • Frictionless Checkout Experience</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Only show the staff login option if not inside the verification panel
    if not st.session_state.admin_login:
        top_left, top_right = st.columns([8, 2])
        with top_right:
            if st.button("🔒 Staff Login", use_container_width=True):
                st.session_state.admin_login = True
                st.rerun()

    # Secret Admin Verification Gate Form
    if not st.session_state.logged_in and st.session_state.admin_login:
        st.markdown("<br>", unsafe_allow_html=True)
        left, center, right = st.columns([2, 1.5, 2])

        with center:
            st.markdown(
                """
                <div style="background:white; padding:35px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08);">
                    <h1 style="text-align:center; color:#1e293b; font-size:23px; margin-bottom:10px;">🔒 Staff Verification Gate</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
            admin_email = st.text_input("Admin Email", key="admin_email_input")
            admin_password = st.text_input(
                "Admin Password", type="password", key="admin_pass_input"
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                    "🚀 Authenticate", use_container_width=True, type="primary"
                ):
                    if (
                        admin_email.strip() == "adminhere@gmail.com"
                        and admin_password.strip() == "admin123"
                    ):
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.username = "Administrator"
                        st.session_state.user_email = "adminhere@gmail.com"
                        st.session_state.login_time = datetime.now()
                        st.success("Welcome back Administrator")
                        st.rerun()
                    else:
                        st.error("Invalid Administrative Credentials")
            with c2:
                if st.button("⬅ Back", use_container_width=True):
                    st.session_state.admin_login = False
                    st.rerun()
        st.stop()

    # CRITICAL CHANGE: This block is now strictly nested within the 'else' statement
    # to guarantee it drops off completely when an admin logs in.
    col_login, col_info = st.columns([1.2, 1.8], gap="large")

    # LEFT SIDE → LOGIN / SIGNUP
    with col_login:
        st.markdown(
            '<div class="section-header">Customer Access</div>', unsafe_allow_html=True
        )
        login_tab, signup_tab = st.tabs(["🔒 Secure Login", "📝 New Account"])

        with login_tab:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("🚀 Login to Shop", use_container_width=True, type="primary"):
                if not email.strip() or not password.strip():
                    st.error("Please fill out all fields.")
                else:
                    user_email_clean = email.strip()
                    if get_failed_payment_streak(user_email_clean) >= 3:
                        st.error("🚨 Account temporarily suspended. Try again later.")
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
                            st.success("Login Successful!")
                            st.switch_page("pages/products.py")
                        else:
                            st.error("Invalid email or password.")

        with signup_tab:
            name = st.text_input("Full Name", key="signup_name")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_password = st.text_input(
                "Password", type="password", key="signup_password"
            )
            if st.button("✨ Create Account", use_container_width=True):
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
                        st.success("Registration Successful!")
                    else:
                        st.error("Email already exists.")

    # RIGHT SIDE → SHOP INFO
    with col_info:
        st.markdown(
            "<h1 style='font-size:48px; font-weight:800; color:#1e3a8a;'>Welcome to ShopZone 🛍️</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "### Premium Shopping Experience\n\nDiscover thousands of products from:\n\n✔ Electronics ✔ Fashion  ✔ Home Decor \n\n✔ Lifestyle Products  ✔ Books  ✔ Accessories"
        )
        st.info(
            "🚚 Free Delivery Above ₹999\n\n⚡ Fast Checkout Experience\n\n📦 24x7 Customer Support"
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Products", "1000+")
        c2.metric("Customers", "5000+")
        c3.metric("Orders", "3500+")

        st.write("")
        st.markdown(
            '<div class="feature-card"><h3>🎉 Today\'s Offer</h3><p>Flat 20% OFF on Electronics<br>+ Free Delivery Across India</p></div>',
            unsafe_allow_html=True,
        )

st.divider()
st.caption("© 2026 ShopZone Marketplace • Secure Customer Portal")
