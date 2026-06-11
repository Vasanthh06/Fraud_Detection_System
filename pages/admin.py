import pandas as pd
import plotly.express as px
import streamlit as st
from database.db import verify_db
from database.logger import get_all_transactions

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="FraudGuard Admin", page_icon="🛡️", layout="wide")

# ============================================================
# MASTER UI/UX FULL-WIDTH INJECTION (Forces pure full-screen layout)
# ============================================================
st.markdown(
    """
    <style>
    /* Bypass all structural layout constraints and fill the screen horizontally from the absolute left */
    [data-testid="stMain"], 
    [data-testid="stAppViewBlockContainer"], 
    .stMainBlockContainer {
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
        margin: 0 !important;
        left: 0 !important;
    }
    
    /* Modern Card Container styling for Metrics */
    div[data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Clean horizontal layout gaps between columns */
    div[data-testid="stHorizontalBlock"] {
        gap: 3rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# AUTH CHECK
# ============================================================
if not st.session_state.get("admin_login"):
    st.warning("Please login as admin.")
    st.stop()

# ============================================================
# HEADER
# ============================================================
st.title("🛡️ FraudGuard Command Center")
st.caption("Real-Time Fraud Detection Monitoring Dashboard")
st.divider()

# ============================================================
# LOAD DATA
# ============================================================
verify_db()
transactions = get_all_transactions()

if not transactions:
    st.warning("No transactions found in database.")
    st.stop()

# ============================================================
# DATAFRAME
# ============================================================
df = pd.DataFrame(
    transactions,
    columns=[
        "transaction_id",
        "customer_name",
        "product_name",
        "card_masked",
        "amount",
        "country",
        "device_type",
        "transaction_hour",
        "failed_attempts",
        "risk_score",
        "fraud_reason",
        "status",
        "created_at",
    ],
)

# ============================================================
# CLEAN DATA
# ============================================================
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0)
df["status"] = df["status"].astype(str).str.strip()

# ============================================================
# FILTER DATA
# ============================================================
genuine_df = df[df["status"] == "Success"].copy()
suspicious_df = df[df["status"] == "Suspicious"].copy()
fraud_df = df[df["status"] == "Fraud"].copy()

# ============================================================
# METRICS METADATA CALCULATION
# ============================================================
total_tx = len(df)
genuine_count = len(genuine_df)
suspicious_count = len(suspicious_df)
fraud_count = len(fraud_df)
total_amount = float(df["amount"].sum())
success_rate = (genuine_count / total_tx) * 100 if total_tx > 0 else 0

# ============================================================
# ROW 1: METRICS ROW (Fills screen width evenly from left to right)
# ============================================================
m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    st.metric("Transactions", total_tx)
with m2:
    st.metric("Success", genuine_count)
with m3:
    st.metric("Suspicious", suspicious_count)
with m4:
    st.metric("Fraud", fraud_count)
with m5:
    st.metric("Volume", f"₹{total_amount:,.0f}")
with m6:
    st.metric("Success Rate", f"{success_rate:.2f}%")

st.divider()

# ============================================================
# ROW 2: SIDE-BY-SIDE CHARTS (Using Plotly to fix text angles)
# ============================================================
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("📊 Transaction Categories")
    category_df = pd.DataFrame(
        {
            "Category": ["Success", "Suspicious", "Fraud"],
            "Count": [genuine_count, suspicious_count, fraud_count],
        }
    )

    fig_categories = px.bar(
        category_df,
        x="Category",
        y="Count",
        color="Category",
        color_discrete_map={
            "Success": "#10B981",
            "Suspicious": "#F59E0B",
            "Fraud": "#EF4444",
        },
    )

    # FIXED: Hardcoded tickangle=0 forces the labels to sit completely flat
    fig_categories.update_layout(
        xaxis=dict(tickangle=0, title=None),
        yaxis=dict(title="Count"),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig_categories, use_container_width=True)

with chart_right:
    st.subheader("📈 Risk Score Distribution")
    risk_bins = pd.cut(
        df["risk_score"],
        bins=[-1, 25, 50, 75, 100],
        labels=["Low", "Medium", "High", "Critical"],
    )
    risk_distribution = risk_bins.value_counts().sort_index().reset_index()
    risk_distribution.columns = ["Risk Tier", "Count"]

    fig_risk = px.bar(
        risk_distribution,
        x="Risk Tier",
        y="Count",
        color="Risk Tier",
        color_discrete_map={
            "Low": "#3B82F6",
            "Medium": "#6366F1",
            "High": "#F59E0B",
            "Critical": "#EF4444",
        },
    )

    # FIXED: Hardcoded tickangle=0 forces the labels to sit completely flat
    fig_risk.update_layout(
        xaxis=dict(tickangle=0, title=None),
        yaxis=dict(title="Count"),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig_risk, use_container_width=True)

st.divider()

# ============================================================
# ROW 3: HIGH RISK ALERTS & DATA OPERATIONS (Side-by-Side)
# ============================================================
management_left, management_right = st.columns(2)

with management_left:
    st.subheader("🚨 High Risk Transactions")
    high_risk = df[df["risk_score"] >= 80]
    if not high_risk.empty:
        st.dataframe(
            high_risk[
                [
                    "transaction_id",
                    "customer_name",
                    "amount",
                    "risk_score",
                    "status",
                ]
            ],
            use_container_width=True,
            height=280,
            hide_index=True,
        )
    else:
        st.success("No high-risk transactions detected.")

with management_right:
    st.subheader("🔍 Search & Data Export")
    search = st.text_input("Search Transaction ID Filter")
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df["transaction_id"].astype(str).str.contains(search, case=False)
        ]

    st.write("")  # Visual spacer
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Sorted Transactions CSV",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()

# ============================================================
# ROW 4: DATA LEDGER & LATEST ENTRIES (Perfect Left/Right Split Layout)
# ============================================================
panel_left, panel_right = st.columns(2)

with panel_left:
    st.subheader("📋 Segmented Data Ledger")
    tab1, tab2, tab3, tab4 = st.tabs(["All Logs", "Success", "Suspicious", "Fraud"])

    with tab1:
        st.dataframe(filtered_df, use_container_width=True, height=200, hide_index=True)
    with tab2:
        if genuine_df.empty:
            st.info("No successful transactions.")
        else:
            st.dataframe(
                genuine_df,
                use_container_width=True,
                height=200,
                hide_index=True,
            )
    with tab3:
        if suspicious_df.empty:
            st.info("No suspicious transactions.")
        else:
            st.dataframe(
                suspicious_df,
                use_container_width=True,
                height=200,
                hide_index=True,
            )
    with tab4:
        if fraud_df.empty:
            st.info("No fraud transactions.")
        else:
            st.dataframe(
                fraud_df, use_container_width=True, height=200, hide_index=True
            )

with panel_right:
    st.subheader("🕒 Latest 5 Transactions")
    latest_df = df.sort_values(by="created_at", ascending=False).head(5)
    st.dataframe(
        latest_df[
            [
                "transaction_id",
                "customer_name",
                "amount",
                "risk_score",
                "status",
            ]
        ],
        use_container_width=True,
        height=200,
        hide_index=True,
    )

st.divider()
st.caption("🛡️ FraudGuard v2.0 | AI Powered Fraud Detection System")
