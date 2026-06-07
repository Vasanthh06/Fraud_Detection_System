Markdown

# 🛡️ E-Commerce Predictive Fraud Detection & Automated Account Isolation System

An end-to-end intelligent security framework built with **Python**, **Streamlit**, and **Machine Learning** to protect e-commerce payment gateways. This application analyzes transactions in real-time, intercepts card structural anomalies using mathematical checksums, calculates risk scores via predictive modeling, and enforces an automated 3-strike account lockout defense mechanism.

---

## 🚀 Core Architectural Features

- **Real-Time Payment Gateway & Validation:** Includes structural client-side input constraint management (automatic formatting truncation using `max_chars`) to validate card criteria gracefully.
- **Mathematical Guardrails (Luhn Checklist):** Intercepts random string or key irregularities instantly using a built-in Mod-10 checksum calculation engine before dispatching API vectors.
- **Machine Learning Predictive Core:** Runs background pipeline evaluation over attributes like transaction amount, source country profile, execution window hour, and historical user velocity tags to label transactions as _Genuine_, _Suspicious_, or _Fraud_.
- **3-Strike Dynamic Security Lockout:** Tracks account irregularities across sessions. Upon triggering 3 consecutive threshold failures, it updates the persistent storage schema, kills active authentication tokens, and locks the profile for 24 hours.
- **Comprehensive Administrative Business Intelligence Dashboard:** A secure visualization workspace with live analytical key performance indicators (KPIs), structural filtering tables, interactive transaction distribution charts, and raw database migration management.

---

## 📊 System Architecture & Data Flow

[ Customer Shopper ] --------> [ Streamlit Gateway Interface ]
|
/ \_
| |
[ Step 1: Structural Check ] [ Step 2: Predictive Engine ]

- Truncation Input Bounds - ML Pipeline Inference Data Matrix
- Luhn Mod-10 Algorithm - Multi-categorical Risk Profiling
  | |
  ****\*\*****\_\_****\*\***** ****\*\*****\_\_\_****\*\*****/
  | /
  v
  [ Step 3: Enforcement State ]
- Genuine: Complete Allocation & Receipt
- Fraud / Strike: Increment Strike Count Index
  |
  v
  [ Dynamic Persistence Layer ]
- SQLite Database Audit Ledger (fraud.db)
- 3 Strikes Triggered -> Active Account Suspended

---

## 🛠️ Technology Stack & Dependencies

- **Frontend UI & Framework:** Streamlit (Python-native multi-page web app architecture)
- **Data Analysis & Aggregation:** Pandas, NumPy
- **Interactive Visualizations:** Plotly Express (Data-driven distribution charts & trend analysis)
- **Predictive Model Core:** Scikit-Learn, Joblib (Serialized custom Random Forest / Gradient Boosting pipeline models)
- **Database Storage Engine:** SQLite3 (Relational persistence layer mapping application events)

---

## 📂 Project Directory Structure

```text
Fraud_Detection_System/
│
├── .streamlit/
│   └── config.toml          # Custom UI branding and primary styling configurations
│
├── database/
│   ├── fraud.db             # Live persistent SQLite relational file
│   ├── auth.py              # User security policies and strike increments
│   ├── db.py                # Core database connection pool configuration
│   └── logger.py            # Transaction ledger write/read streams
│
├── models/
│   ├── ecommerce_fraud_model.pkl   # Serialized machine learning inference pipeline
│   └── ecommerce_encoder.pkl       # Categorical feature encoder matrix
│
├── pages/
│   ├── admin.py             # Admin Dashboard, live KPIs, charts, and DB maintenance portal
│   ├── login.py             # Secure registration & login portal
│   ├── payment.py           # Clean payment input screen with built-in input cutoff
│   └── shop.py              # Product gallery and shopping cart validation loop
│
├── app.py                   # Main portal landing module layout gateway
├── requirements.txt         # Pinned cloud dependencies log register
└── README.md                # Master repository documentation manual
```
