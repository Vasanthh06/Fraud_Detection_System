import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")


if not st.session_state.get("is_admin", False):
    st.error("Access Denied. Admin Login Required.")
    st.stop()


st.title("📊 Fraud Detection Admin Dashboard")

# Database Connection
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database", "fraud.db"
)

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("SELECT * FROM transactions", conn)

conn.close()

if len(df) == 0:

    st.warning("No Transactions Found")

else:

    # -----------------------------
    # Search Customer
    # -----------------------------
    search = st.text_input("🔍 Search Customer")

    if search:

        df = df[df["customer_name"].str.contains(search, case=False, na=False)]

    # -----------------------------
    # Status Filter
    # -----------------------------
    status_filter = st.selectbox(
        "Filter by Status", ["All", "Genuine", "Suspicious", "Fraud"]
    )

    if status_filter != "All":

        df = df[df["status"] == status_filter]

    # -----------------------------
    # KPIs
    # -----------------------------
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

    # -----------------------------
    # Transaction Table
    # -----------------------------
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
        width="stretch",
    )

    # -----------------------------
    # Download CSV
    # -----------------------------
    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download Transactions CSV Report",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv",
    )

    st.divider()

    # -----------------------------
    # Pie Chart
    # -----------------------------
    st.subheader("🥧 Transaction Distribution")

    pie = px.pie(df, names="status", title="Fraud vs Genuine vs Suspicious")

    st.plotly_chart(pie, width="stretch")

    # -----------------------------
    # Risk Score Chart
    # -----------------------------
    st.subheader("📈 Risk Score Analysis")

    bar = px.bar(
        df,
        x="transaction_id",
        y="risk_score",
        color="status",
        title="Risk Score Per Transaction",
    )

    st.plotly_chart(bar, width="stretch")

    # -----------------------------
    # Country Analysis
    # -----------------------------
    st.subheader("🌍 Country Wise Transactions")

    country_chart = px.histogram(df, x="country", color="status", barmode="group")

    st.plotly_chart(country_chart, width="stretch")

# ============================================================
# NEW: DIRECT SQLITE RAW DATABASE MAINTENANCE DOWNLOAD PORTAL
# ============================================================
st.divider()
st.subheader("📦 Production Database Systems Maintenance")

if os.path.exists(DB_PATH):
    with open(DB_PATH, "rb") as db_file:
        st.download_button(
            label="📥 Download Raw SQLite Database File (.db)",
            data=db_file,
            file_name="fraud_live_database.db",
            mime="application/octet-stream",
            use_container_width=True,
            type="primary",
        )
else:
    st.error(
        "System Footprint Error: The active SQLite database file could not be localized on the hosting platform."
    )

st.markdown(
    """
<h1 style='text-align:center;color:#EF4444'>
🛡️ Administrator Portal
</h1>
""",
    unsafe_allow_html=True,
)
