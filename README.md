Markdown

# 🛡️ Dual-Engine Predictive Fraud Detection & Automated Account Isolation System

An end-to-end intelligent financial security framework built with **Python**, **Streamlit**, and **Machine Learning** to protect transaction processing systems. The system deploys a dual-engine architecture: an interactive e-commerce web portal powered by a custom behavioral model, and a deep data analysis pipeline trained on real-world bank credit card logs optimized with synthetic class balancing.

---

## 🚀 Core Architectural Features

- **Real-Time Payment Gateway Validation:** Implements front-end field character truncation limits (`max_chars`) to validate input formats seamlessly before processing backend calculations.
- **Algorithmic Checksum Defenses (Luhn Checklist):** Intercepts randomized digits and mistyped card entries using a fast Mod-10 checksum loop before forwarding data to predictive APIs.
- **Dual ML Predictive Processing Engines:**
  - **Engine A (E-Commerce Behavioral Model):** Evaluates live user session contexts (Amount, Country Profile, Transaction Hour, and Historical Failure Streak Velocity).
  - **Engine B (Anonymized Credit Card Model):** Processes highly dimensional real-world bank transactions optimized using specialized oversampling techniques (`SMOTE`).
- **Automated 3-Strike Security Isolation:** Monitors customer transaction failure rates. Triggering 3 consecutive validation drops updates the SQL persistence layer, terminates active authentication tokens, and enforces a 24-hour account suspension.
- **Administrative Analytics Workspace:** Provides an isolated dashboard rendering dynamic transaction filters, interactive Plotly distribution charts, and a one-click binary database extraction portal (`.db`).

---

## 📊 System Architecture & Data Flow

```text
       [ Customer Shopper / Browser Session ]
                         │
                         ▼
           [ Streamlit Gateway Interface ]
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
  [ Layer 1: Structural Check ]   [ Layer 2: Predictive Engine ]
  - Character Cutoff Controls     - ML Pipeline Inference Matrix
  - Luhn Mod-10 Checksum Formula  - Random Forest Class Identification
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
           [ Layer 3: Enforcement State ]
           ├── Genuine: Complete Allocation & Log Receipt
           └── Fraud/Strike: Increment Failure Index Count
                         │
                         ▼
           [ Dynamic Persistence Layer ]
           ├── SQLite DB Audit Ledger (`fraud.db`)
           └── Strike Count = 3 ──► Automatic Account Suspension
📂 Project Directory Structure
Plaintext
Fraud_Detection_System/
│
├── .streamlit/
│   └── config.toml          # Custom UI branding and primary styling configurations
│
├── database/
│   ├── fraud.db             # Live relational SQLite database file
│   ├── auth.py              # User security policies and strike increments
│   ├── db.py                # Core database connection pool configuration
│   └── logger.py            # Transaction ledger write/read streams
│
├── dataset/
│   ├── ecommerce_fraud.csv  # Generated e-commerce simulation records (5,000 entries)
│   └── creditcard.csv       # Real-world anonymized financial transaction entries
│
├── models/
│   ├── ecommerce_fraud_model.pkl   # Serialized Random Forest e-commerce model
│   ├── ecommerce_encoder.pkl       # Categorical string country encoding matrix
│   ├── fraud_model.pkl             # High-dimensional real credit card analysis model
│   └── scaler.pkl                  # Quantitative feature scaling matrix
│
├── pages/
│   ├── admin.py             # Admin Dashboard, live KPIs, charts, and DB download button
│   ├── login.py             # Secure registration & login portal
│   ├── payment.py           # Clean payment input screen with built-in input cutoff
│   └── shop.py              # Product gallery and shopping cart validation loop
│
├── app.py                   # Main portal landing module layout gateway
├── dataset_generator.py     # Rule-based e-commerce matrix data simulator
├── eda.py                   # Credit card structural exploration script
├── train_ecommerce_model.py # E-commerce scenario encoder & model training pipeline
├── train_model.py           # Credit card SMOTE class balancing & model trainer
└── requirements.txt         # Pinned cloud dependencies log register
🛠️ Technology Stack & Dependencies
Frontend UI & Framework: Streamlit (Python-native multi-page web architecture)

Data Analysis & Aggregation: Pandas, NumPy

Interactive Visualizations: Plotly Express (Data-driven distribution charts & trend analysis)

Predictive Model Core: Scikit-Learn, Joblib (Serialized Random Forest pipelines)

Database Storage Engine: SQLite3 (Relational persistence layer mapping application events)
```

⚡ Setup & Data Pipeline Execution Guide

1. Clone & Environment Initialization
   Bash
   git clone [https://github.com/Vasanthh06/Fraud_Detection_System.git](https://github.com/Vasanthh06/Fraud_Detection_System.git)
   cd Fraud_Detection_System

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt 2. Run the E-Commerce Behavioral Pipeline
Generates 5,000 synthetic transaction records modeling adversarial heuristics, encodes country objects, and trains the e-commerce model classifier:

Bash
python dataset_generator.py
python train_ecommerce_model.py 3. Run the Advanced Credit Card Analysis Pipeline
Processes the authentic bank dataset, scales feature dimensions, applies SMOTE to handle class imbalances, and trains the real-world pipeline:

Bash
python train_model.py 4. Run the Web Interface
Bash
streamlit run app.py
🧪 Testing Presentation Scenarios
User Access Configuration
Administrator Workspace: Log in with adminhere@gmail.com to review metrics, system distribution trends, and download the raw .db database ledger file.

Customer Session: Register any unique test email address to run shopping transactions.

Testing Workflows
Genuine Checkout Processing: Use a valid card structure (e.g., 4222-2222-2222-2222), enter transaction details, and watch the system pass all security rules to successfully build an invoice receipt.

Mathematical Validation Intercept: Attempt a checkout with an invalid sequence of random numbers. The system intercepts the transaction at Layer 1 via the Luhn formula, preventing unnecessary API calls.

Automated Account Isolation: Deliberately trigger 3 failed transaction attempts on an account. The database updates failed_payment_streak = 3, kills the session token, logs the user out, and blocks subsequent authentication attempts.
