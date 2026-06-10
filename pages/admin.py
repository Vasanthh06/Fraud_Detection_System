import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from database.db import DB_PATH, init_db

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# FIXED: Correct admin check - only block NON-admins
if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

if not st.session_state.get("is_admin", False):
    st.error("Access Denied. Admin Login Required.")
    st.stop()

st.title("📊 Fraud Detection Admin Dashboard")

# ============================================================
# NEW: GO BACK + LOGOUT BUTTONS
# ============================================================
col_back, col_logout = st.columns([1, 1])
with col_back:
    if st.button("⬅ Go Back", use_container_width=True):
        st.session_state.admin_login = False
        st.rerun()
with col_logout:
    # FIXED: Logout clears everything
    if st.button("🔴 Logout", use_container_width=True, type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False
        st.session_state.cart = []
        st.session_state.total_amount = 0
        st.session_state.user_email = ""
        st.session_state.username = "User"
        st.session_state.payment_success = False
        st.rerun()

init_db()
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

if len(df) == 0:
    st.warning("No Transactions Found")
else:
    search = st.text_input("🔍 Search Customer")
    if search:
        df = df[df["customer_name"].str.contains(search, case=False, na=False)]
    status_filter = st.selectbox(
        "Filter by Status", ["All", "Genuine", "Suspicious", "Fraud"]
    )
    if status_filter != "All":
        df = df[df["status"] == status_filter]

    total_transactions = len(df)
    genuine_transactions = len(df[df["status"] == "Genuine"])
    fraud_transactions = len(df[df["status"] == "Fraud"])
    suspicious_transactions = len(df[df["status"] == "Suspicious"])
    fraud_percentage = (
        round((fraud_transactions / total_transactions) * 100, 2)
        if total_transactions > 0
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Transactions", total_transactions)
    col2.metric("Genuine", genuine_transactions)
    col3.metric("Fraud", fraud_transactions)
    col4.metric("Suspicious", suspicious_transactions)
    col5.metric("Fraud %", f"{fraud_percentage}%")
    st.divider()

    st.subheader("📋 Transaction History")
    st.dataframe(
        df[
            [
                "transaction_id",
                "customer_name",
                "product_name",
                "amount",
                "country",
                "device_type",
                "risk_score",
                "fraud_reason",
                "status",
            ]
        ].sort_values(by="transaction_id", ascending=False),
        use_container_width=True,
    )

    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv",
    )
    st.divider()

    st.subheader("🥧 Transaction Distribution")
    pie = px.pie(df, names="status", title="Fraud vs Genuine vs Suspicious")
    st.plotly_chart(pie, use_container_width=True)

    st.subheader("📈 Risk Score Analysis")
    bar = px.bar(
        df,
        x="transaction_id",
        y="risk_score",
        color="status",
        title="Risk Score Per Transaction",
    )
    st.plotly_chart(bar, use_container_width=True)

    st.subheader("🌍 Country Wise Transactions")
    country_chart = px.histogram(df, x="country", color="status", barmode="group")
    st.plotly_chart(country_chart, use_container_width=True)

st.divider()
st.subheader("📦 Database Maintenance")
if os.path.exists(DB_PATH):
    with open(DB_PATH, "rb") as db_file:
        st.download_button(
            label="📥 Download .db File",
            data=db_file,
            file_name="fraud_live_database.db",
            mime="application/octet-stream",
            use_container_width=True,
            type="primary",
        )
else:
    st.error("Database file not found.")

st.markdown(
    "<h1 style='text-align:center;color:#EF4444'>🛡️ Administrator Portal</h1>",
    unsafe_allow_html=True,
)
