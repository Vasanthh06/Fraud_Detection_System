import streamlit as st
from datetime import datetime
from database.db import init_db

# ============================================================
# 1. ALWAYS CALL THIS AT THE VERY TOP
# ============================================================
init_db()

# Safe to import auth modules
from database.auth import (
    register_user,
    login_user,
    get_failed_payment_streak,
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
# 6. REDESIGNED CSS — Deep Navy + Coral Accent + Soft Cards
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
    background: #0d1117;
    font-family: 'Inter', sans-serif;
}

/* Remove default streamlit padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ===========================
   ANIMATED BACKGROUND GRID
=========================== */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
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
    background: linear-gradient(135deg, #1a1f2e 0%, #161b2a 100%);
    border: 1px solid rgba(99,102,241,0.2);
    overflow: hidden;
    animation: fadeSlideDown 0.6s ease both;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    bottom: -80px; left: -40px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(244,114,74,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc;
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
    color: #f1f5f9;
    line-height: 1.1;
    margin: 0 0 12px;
    letter-spacing: -1px;
}
.hero-title span {
    background: linear-gradient(90deg, #6366f1, #f4724a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 16px;
    color: #a5b4fc;
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
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    color: #c7d2fe;
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 50px;
    font-weight: 500;
}

/* ===========================
   SECTION HEADER
=========================== */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 20px;
    margin-top: 0;
    letter-spacing: -0.3px;
}

/* ===========================
   LOGIN / SIGNUP CARD
=========================== */
.login-card-wrap {
    background: #161b2a;
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 20px;
    padding: 24px 28px;
    animation: fadeSlideUp 0.5s ease both;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

/* ===========================
   STREAMLIT INPUT OVERRIDES
=========================== */
.stTextInput > label {
    color: #e2e8f0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
}
.stTextInput input {
    background: #0f172a !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ===========================
   TABS
=========================== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #c7d2fe !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ===========================
   BUTTONS
=========================== */
.stButton > button {
    width: 100% !important;
    height: 48px !important;
    border-radius: 12px !important;
    border: none !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.12), transparent);
    opacity: 0;
    transition: opacity 0.25s ease;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}
.stButton > button:hover::after { opacity: 1; }
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ===========================
   FEATURE / INFO CARDS
=========================== */
.feat-card {
    background: #161b2a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    animation: fadeSlideUp 0.5s ease both;
}
.feat-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99,102,241,0.35);
    box-shadow: 0 12px 40px rgba(99,102,241,0.1);
}
.feat-icon {
    font-size: 28px;
    margin-bottom: 10px;
}
.feat-title {
    font-weight: 700;
    font-size: 14px;
    color: #f1f5f9;
    margin-bottom: 6px;
}
.feat-desc {
    font-size: 12px;
    color: #c7d2fe;
    line-height: 1.5;
    margin: 0;
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
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #818cf8;
    line-height: 1;
}
.stat-label {
    font-size: 11px;
    color: #c7d2fe;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===========================
   OFFER BANNER
=========================== */
.offer-banner {
    background: linear-gradient(135deg, #1e1030, #1a1f2e);
    border: 1px solid rgba(244,114,74,0.25);
    border-radius: 16px;
    padding: 20px 22px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 16px;
    animation: pulse-border 3s ease infinite;
}
@keyframes pulse-border {
    0%, 100% { border-color: rgba(244,114,74,0.25); }
    50%       { border-color: rgba(244,114,74,0.55); }
}
.offer-tag {
    background: linear-gradient(135deg, #f4724a, #e85d3a);
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.offer-text {
    color: #e2e8f0;
    font-size: 13px;
    line-height: 1.5;
    margin: 0;
}
.offer-text strong { color: #f1f5f9; }

/* ===========================
   INFO / SUCCESS ALERTS
=========================== */
.stInfo, .stSuccess, .stError, .stWarning {
    border-radius: 12px !important;
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
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 12px 16px;
}
.perk-icon { font-size: 18px; }
.perk-text { font-size: 13px; color: #e2e8f0; font-weight: 500; }
.perk-text strong { color: #f1f5f9; }

/* ===========================
   STAFF LOGIN BUTTON (top-right)
=========================== */
.staff-btn-wrap .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #c7d2fe !important;
    height: 38px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
.staff-btn-wrap .stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.35) !important;
    color: #a5b4fc !important;
    box-shadow: none !important;
}

/* ===========================
   ADMIN GATE CARD
=========================== */
.admin-gate-card {
    background: #0d1117;
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    padding: 36px 32px;
    text-align: center;
    box-shadow: 0 25px 80px rgba(0,0,0,0.5);
    animation: fadeSlideUp 0.4s ease both;
}
.admin-gate-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 6px;
}
.admin-gate-sub {
    font-size: 12px;
    color: #c7d2fe;
    margin-bottom: 24px;
}
.admin-lock-icon {
    font-size: 36px;
    margin-bottom: 12px;
    display: block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-6px); }
}

/* ===========================
   ADMIN COMMAND CENTER
=========================== */
.admin-hero {
    background: linear-gradient(135deg, #0d1117 0%, #161b2a 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 24px;
    padding: 48px 40px;
    text-align: center;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    animation: fadeSlideDown 0.5s ease both;
}
.admin-hero::before {
    content: '';
    position: absolute;
    top: -80px; left: 50%;
    transform: translateX(-50%);
    width: 400px; height: 200px;
    background: radial-gradient(ellipse, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.admin-hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.admin-hero-sub {
    font-size: 14px;
    color: #c7d2fe;
    max-width: 460px;
    margin: 0 auto;
}
.admin-status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: blink 1.8s ease infinite;
    vertical-align: middle;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}
.admin-section-header {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #818cf8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 16px;
}

/* ===========================
   FORGOT PASSWORD PAGE
=========================== */
.fp-card {
    background: #161b2a;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 36px 32px;
    animation: fadeSlideUp 0.4s ease both;
    max-width: 480px;
    margin: 0 auto;
}
.fp-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 6px;
}
.fp-sub {
    font-size: 13px;
    color: #c7d2fe;
    margin-bottom: 24px;
}

/* ===========================
   DIVIDER OVERRIDE
=========================== */
hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 28px 0 !important;
}

/* ===========================
   FOOTER — WHITE TEXT FIX
=========================== */
.stApp footer {
    color: #e2e8f0 !important;
}
.stCaption {
    color: #e2e8f0 !important;
}

/* ===========================
   KEYFRAMES
=========================== */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Metric overrides */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 16px;
}
[data-testid="stMetricValue"] {
    color: #818cf8 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 22px !important;
}
[data-testid="stMetricLabel"] {
    color: #c7d2fe !important;
    font-size: 12px !important;
}

/* ===========================
   GENERAL TEXT COLOR FIXES
=========================== */
/* Make all paragraph text white */
p {
    color: #e2e8f0 !important;
}

/* Make all heading text white */
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
}

/* Make labels and small text white */
label {
    color: #e2e8f0 !important;
}

/* Streamlit widget labels */
[data-testid="stWidgetLabel"] {
    color: #e2e8f0 !important;
}

/* Fix for st.write text */
[data-testid="stMarkdownContainer"] p {
    color: #e2e8f0 !important;
}

/* Fix for form labels */
[data-testid="stForm"] label {
    color: #e2e8f0 !important;
}

/* Fix for checkbox and radio labels */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {
    color: #e2e8f0 !important;
}

/* Fix for selectbox labels */
[data-testid="stSelectbox"] label {
    color: #e2e8f0 !important;
}

/* Fix for text area */
.stTextArea textarea {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for selectbox */
.stSelectbox > div > div {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for multiselect */
.stMultiSelect > div > div {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for date input */
.stDateInput input {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for number input */
.stNumberInput input {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for slider */
.stSlider > div > div > div {
    color: #e2e8f0 !important;
}

/* Fix for file uploader */
.stFileUploader > div > div {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for code block */
pre {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}

/* Fix for table */
table {
    color: #e2e8f0 !important;
}

/* Fix for dataframe */
[data-testid="stDataFrame"] {
    color: #e2e8f0 !important;
}

/* Fix for expander */
[data-testid="stExpander"] > div > div {
    color: #e2e8f0 !important;
}

/* Fix for toast notifications */
[data-testid="stToast"] {
    color: #f1f5f9 !important;
}

/* Fix for tooltip */
[data-testid="stTooltipIcon"] {
    color: #c7d2fe !important;
}

/* Fix for spinner */
[data-testid="stSpinner"] {
    color: #e2e8f0 !important;
}

/* Fix for progress bar */
[data-testid="stProgressBar"] > div {
    color: #e2e8f0 !important;
}

/* Fix for metric delta */
[data-testid="stMetricDelta"] {
    color: #e2e8f0 !important;
}

/* Fix for empty state */
[data-testid="stEmpty"] {
    color: #e2e8f0 !important;
}

/* Fix for status */
[data-testid="stStatus"] {
    color: #e2e8f0 !important;
}

/* Fix for chat message */
[data-testid="stChatMessage"] {
    color: #e2e8f0 !important;
}

/* Fix for chat input */
[data-testid="stChatInput"] input {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for audio player */
[data-testid="stAudio"] {
    color: #e2e8f0 !important;
}

/* Fix for video player */
[data-testid="stVideo"] {
    color: #e2e8f0 !important;
}

/* Fix for image caption */
[data-testid="stImage"] figcaption {
    color: #c7d2fe !important;
}

/* Fix for download button */
[data-testid="stDownloadButton"] button {
    color: white !important;
}

/* Fix for link button */
[data-testid="stLinkButton"] a {
    color: #818cf8 !important;
}

/* Fix for page link */
[data-testid="stPageLink"] a {
    color: #c7d2fe !important;
}

/* Fix for navigation */
[data-testid="stNavigation"] {
    color: #e2e8f0 !important;
}

/* Fix for sidebar navigation */
[data-testid="stSidebarNav"] a {
    color: #c7d2fe !important;
}

/* Fix for sidebar navigation active */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: #818cf8 !important;
}

/* Fix for breadcrumbs */
[data-testid="stBreadcrumbs"] {
    color: #c7d2fe !important;
}

/* Fix for pagination */
[data-testid="stPagination"] {
    color: #e2e8f0 !important;
}

/* Fix for search */
[data-testid="stSearch"] input {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}

/* Fix for filter */
[data-testid="stFilter"] {
    color: #e2e8f0 !important;
}

/* Fix for sort */
[data-testid="stSort"] {
    color: #e2e8f0 !important;
}

/* Fix for column config */
[data-testid="stColumnConfig"] {
    color: #e2e8f0 !important;
}

/* Fix for cell editor */
[data-testid="stCellEditor"] {
    color: #f1f5f9 !important;
}

/* Fix for row selector */
[data-testid="stRowSelector"] {
    color: #e2e8f0 !important;
}

/* Fix for batch editor */
[data-testid="stBatchEditor"] {
    color: #e2e8f0 !important;
}

/* Fix for data editor */
[data-testid="stDataEditor"] {
    color: #e2e8f0 !important;
}

/* Fix for code editor */
[data-testid="stCodeEditor"] {
    color: #e2e8f0 !important;
}

/* Fix for json viewer */
[data-testid="stJsonViewer"] {
    color: #e2e8f0 !important;
}

/* Fix for html viewer */
[data-testid="stHtmlViewer"] {
    color: #e2e8f0 !important;
}

/* Fix for markdown viewer */
[data-testid="stMarkdownViewer"] {
    color: #e2e8f0 !important;
}

/* Fix for latex viewer */
[data-testid="stLatexViewer"] {
    color: #e2e8f0 !important;
}

/* Fix for graphviz viewer */
[data-testid="stGraphvizViewer"] {
    color: #e2e8f0 !important;
}

/* Fix for plotly chart */
[data-testid="stPlotlyChart"] {
    color: #e2e8f0 !important;
}

/* Fix for altair chart */
[data-testid="stAltairChart"] {
    color: #e2e8f0 !important;
}

/* Fix for vega lite chart */
[data-testid="stVegaLiteChart"] {
    color: #e2e8f0 !important;
}

/* Fix for bokeh chart */
[data-testid="stBokehChart"] {
    color: #e2e8f0 !important;
}

/* Fix for pydeck chart */
[data-testid="stPydeckChart"] {
    color: #e2e8f0 !important;
}

/* Fix for deck gl chart */
[data-testid="stDeckGlChart"] {
    color: #e2e8f0 !important;
}

/* Fix for mapbox */
[data-testid="stMapbox"] {
    color: #e2e8f0 !important;
}

/* Fix for folium */
[data-testid="stFolium"] {
    color: #e2e8f0 !important;
}

/* Fix for leaflet */
[data-testid="stLeaflet"] {
    color: #e2e8f0 !important;
}

/* Fix for google maps */
[data-testid="stGoogleMaps"] {
    color: #e2e8f0 !important;
}

/* Fix for iframe */
[data-testid="stIframe"] {
    color: #e2e8f0 !important;
}

/* Fix for html */
[data-testid="stHtml"] {
    color: #e2e8f0 !important;
}

/* Fix for markdown */
[data-testid="stMarkdown"] {
    color: #e2e8f0 !important;
}

/* Fix for text */
[data-testid="stText"] {
    color: #e2e8f0 !important;
}

/* Fix for title */
[data-testid="stTitle"] {
    color: #f1f5f9 !important;
}

/* Fix for header */
[data-testid="stHeader"] {
    color: #f1f5f9 !important;
}

/* Fix for subheader */
[data-testid="stSubheader"] {
    color: #e2e8f0 !important;
}

/* Fix for caption */
[data-testid="stCaption"] {
    color: #c7d2fe !important;
}

/* Fix for code */
[data-testid="stCode"] {
    color: #e2e8f0 !important;
}

/* Fix for latex */
[data-testid="stLatex"] {
    color: #e2e8f0 !important;
}

/* Fix for divider */
[data-testid="stDivider"] {
    color: #475569 !important;
}

/* Fix for space */
[data-testid="stSpace"] {
    color: #e2e8f0 !important;
}

/* Fix for tabs */
[data-testid="stTabs"] {
    color: #e2e8f0 !important;
}

/* Fix for tab */
[data-testid="stTab"] {
    color: #c7d2fe !important;
}

/* Fix for tab panel */
[data-testid="stTabPanel"] {
    color: #e2e8f0 !important;
}

/* Fix for container */
[data-testid="stContainer"] {
    color: #e2e8f0 !important;
}

/* Fix for column */
[data-testid="stColumn"] {
    color: #e2e8f0 !important;
}

/* Fix for vertical block */
[data-testid="stVerticalBlock"] {
    color: #e2e8f0 !important;
}

/* Fix for horizontal block */
[data-testid="stHorizontalBlock"] {
    color: #e2e8f0 !important;
}

/* Fix for expander */
[data-testid="stExpander"] {
    color: #e2e8f0 !important;
}

/* Fix for form */
[data-testid="stForm"] {
    color: #e2e8f0 !important;
}

/* Fix for form submit button */
[data-testid="stFormSubmitButton"] {
    color: white !important;
}

/* Fix for cache spinner */
[data-testid="stCacheSpinner"] {
    color: #e2e8f0 !important;
}

/* Fix for dialog */
[data-testid="stDialog"] {
    color: #e2e8f0 !important;
}

/* Fix for alert */
[data-testid="stAlert"] {
    color: #e2e8f0 !important;
}

/* Fix for info box */
[data-testid="stInfoBox"] {
    color: #e2e8f0 !important;
}

/* Fix for success box */
[data-testid="stSuccessBox"] {
    color: #e2e8f0 !important;
}

/* Fix for warning box */
[data-testid="stWarningBox"] {
    color: #e2e8f0 !important;
}

/* Fix for error box */
[data-testid="stErrorBox"] {
    color: #e2e8f0 !important;
}

/* Fix for exception */
[data-testid="stException"] {
    color: #e2e8f0 !important;
}

/* Fix for traceback */
[data-testid="stTraceback"] {
    color: #e2e8f0 !important;
}

/* Fix for balloon */
[data-testid="stBalloon"] {
    color: #e2e8f0 !important;
}

/* Fix for snow */
[data-testid="stSnow"] {
    color: #e2e8f0 !important;
}

/* Fix for toast */
[data-testid="stToast"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy dataframe */
[data-testid="stLegacyDataFrame"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy table */
[data-testid="stLegacyTable"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy chart */
[data-testid="stLegacyChart"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy map */
[data-testid="stLegacyMap"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy image */
[data-testid="stLegacyImage"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy audio */
[data-testid="stLegacyAudio"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy video */
[data-testid="stLegacyVideo"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy html */
[data-testid="stLegacyHtml"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy markdown */
[data-testid="stLegacyMarkdown"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy text */
[data-testid="stLegacyText"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy title */
[data-testid="stLegacyTitle"] {
    color: #f1f5f9 !important;
}

/* Fix for legacy header */
[data-testid="stLegacyHeader"] {
    color: #f1f5f9 !important;
}

/* Fix for legacy subheader */
[data-testid="stLegacySubheader"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy caption */
[data-testid="stLegacyCaption"] {
    color: #c7d2fe !important;
}

/* Fix for legacy code */
[data-testid="stLegacyCode"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy latex */
[data-testid="stLegacyLatex"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy divider */
[data-testid="stLegacyDivider"] {
    color: #475569 !important;
}

/* Fix for legacy space */
[data-testid="stLegacySpace"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy tabs */
[data-testid="stLegacyTabs"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy tab */
[data-testid="stLegacyTab"] {
    color: #c7d2fe !important;
}

/* Fix for legacy tab panel */
[data-testid="stLegacyTabPanel"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy container */
[data-testid="stLegacyContainer"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy column */
[data-testid="stLegacyColumn"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy vertical block */
[data-testid="stLegacyVerticalBlock"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy horizontal block */
[data-testid="stLegacyHorizontalBlock"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy expander */
[data-testid="stLegacyExpander"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy form */
[data-testid="stLegacyForm"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy form submit button */
[data-testid="stLegacyFormSubmitButton"] {
    color: white !important;
}

/* Fix for legacy cache spinner */
[data-testid="stLegacyCacheSpinner"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy dialog */
[data-testid="stLegacyDialog"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy alert */
[data-testid="stLegacyAlert"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy info box */
[data-testid="stLegacyInfoBox"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy success box */
[data-testid="stLegacySuccessBox"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy warning box */
[data-testid="stLegacyWarningBox"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy error box */
[data-testid="stLegacyErrorBox"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy exception */
[data-testid="stLegacyException"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy traceback */
[data-testid="stLegacyTraceback"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy balloon */
[data-testid="stLegacyBalloon"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy snow */
[data-testid="stLegacySnow"] {
    color: #e2e8f0 !important;
}

/* Fix for legacy toast */
[data-testid="stLegacyToast"] {
    color: #e2e8f0 !important;
}

/* Fix for all other text elements */
* {
    color: #e2e8f0;
}

/* Override for specific elements that need different colors */
.stButton > button {
    color: white !important;
}

.stTabs [aria-selected="true"] {
    color: white !important;
}

.offer-tag {
    color: white !important;
}

.hero-title span {
    color: transparent !important;
}

.admin-status-dot {
    color: transparent !important;
}

[data-testid="stMetricValue"] {
    color: #818cf8 !important;
}

[data-testid="stMetricLabel"] {
    color: #c7d2fe !important;
}

.stat-num {
    color: #818cf8 !important;
}

.stat-label {
    color: #c7d2fe !important;
}

.feat-title {
    color: #f1f5f9 !important;
}

.feat-desc {
    color: #c7d2fe !important;
}

.perk-text {
    color: #e2e8f0 !important;
}

.perk-text strong {
    color: #f1f5f9 !important;
}

.offer-text {
    color: #e2e8f0 !important;
}

.offer-text strong {
    color: #f1f5f9 !important;
}

.fp-title {
    color: #f1f5f9 !important;
}

.fp-sub {
    color: #c7d2fe !important;
}

.admin-gate-title {
    color: #f1f5f9 !important;
}

.admin-gate-sub {
    color: #c7d2fe !important;
}

.admin-hero-title {
    color: #f1f5f9 !important;
}

.admin-hero-sub {
    color: #c7d2fe !important;
}

.admin-section-header {
    color: #818cf8 !important;
}

.section-header {
    color: #f1f5f9 !important;
}

.hero-badge {
    color: #a5b4fc !important;
}

.hero-title {
    color: #f1f5f9 !important;
}

.hero-subtitle {
    color: #a5b4fc !important;
}

.hero-pill {
    color: #c7d2fe !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 7. DEFINE PAGES FOR NAVIGATION
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
                st.markdown('<div class="staff-btn-wrap">', unsafe_allow_html=True)
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
                        <span class="admin-lock-icon">🔐</span>
                        <div class="admin-gate-title">Admin Verification Gate</div>
                        <div class="admin-gate-sub">Authorised personnel only</div>
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
                """
                <div class="login-card-wrap">
                    <div class="section-header">Customer Access</div>
                """,
                unsafe_allow_html=True,
            )

            login_tab, signup_tab = st.tabs(["🔒 Sign In", "✨ Create Account"])

            with login_tab:
                email = st.text_input("Email address", key="login_email")
                password = st.text_input(
                    "Password", type="password", key="login_password"
                )

                if st.button(
                    "Login to ShopZone →", use_container_width=True, type="primary"
                ):
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
                name = st.text_input("Full Name", key="signup_name")
                signup_email = st.text_input("Email Address", key="signup_email")
                signup_phone = st.text_input("Phone Number", key="signup_phone")
                signup_password = st.text_input(
                    "Password (min 6 chars)", type="password", key="signup_password"
                )

                if st.button("Create My Account →", use_container_width=True):
                    if (
                        not name.strip()
                        or not signup_email.strip()
                        or not signup_phone.strip()
                        or not signup_password.strip()
                    ):
                        st.error("All fields are required.")
                    elif len(signup_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success = register_user(
                            name.strip(),
                            signup_email.strip(),
                            signup_phone.strip(),
                            signup_password.strip(),
                        )
                        if success:
                            st.success(
                                "🎉 Account created! Switch to Sign In to log in."
                            )
                        else:
                            st.error("An account with that email already exists.")

            st.markdown("</div>", unsafe_allow_html=True)

        with col_info:
            st.markdown(
                """
                <h1 style='font-family:"Syne",sans-serif;font-size:clamp(28px,3.5vw,44px);
                            font-weight:800;color:#f1f5f9;line-height:1.15;
                            letter-spacing:-0.5px;margin-bottom:6px;'>
                    Welcome to<br><span style='background:linear-gradient(90deg,#6366f1,#f4724a);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;'>ShopZone</span>
                </h1>
                <p style='color:#e2e8f0;font-size:14px;margin-bottom:20px;'>
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
                        <span class="perk-icon">🚚</span>
                        <span class="perk-text"><strong>Free delivery</strong> on orders above ₹999</span>
                    </div>
                    <div class="perk-row">
                        <span class="perk-icon">⚡</span>
                        <span class="perk-text"><strong>Express checkout</strong> — pay in under 30 seconds</span>
                    </div>
                    <div class="perk-row">
                        <span class="perk-icon">📦</span>
                        <span class="perk-text"><strong>24×7 support</strong> for every order, every day</span>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="offer-banner">
                    <span class="offer-tag">🎉 Today</span>
                    <p class="offer-text"><strong>Flat 20% OFF on all Electronics</strong> + free delivery across India. Limited time.</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

elif st.session_state.logged_in and st.session_state.is_admin:
    # ADMIN: Show admin dashboard with navigation
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
            # Use navigation instead of switch_page
            pg = st.navigation([admin_page], position="sidebar")
            pg.run()

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

else:
    # NORMAL USER: Show products, cart, payment in sidebar
    pg = st.navigation(
        {"Shop": [products_page, cart_page, payment_page]}, position="sidebar"
    )
    pg.run()

st.divider()
st.markdown(
    '<p style="color:#e2e8f0;text-align:center;">© 2026 ShopZone Marketplace • Secure Customer Portal</p>',
    unsafe_allow_html=True,
)
