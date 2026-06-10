# ShopZone - Fixed & Secure E-Commerce App

## 🔧 Fixes Applied

| Issue                           | Fix                                                                     |
| ------------------------------- | ----------------------------------------------------------------------- |
| **Sidebar shows all pages**     | Uses `st.navigation` with `position="hidden"` + custom sidebar per role |
| **Admin Logic Bug**             | Fixed `if not is_admin: stop()` instead of wrong `if is_admin: stop()`  |
| **Hardcoded Admin Credentials** | Moved to environment variables with bcrypt hashing                      |
| **Session Timeout Bug**         | Changed `.seconds` to `.total_seconds()`                                |
| **Security (SHA256 passwords)** | Replaced with bcrypt hashing                                            |
| **Logout Doesn't Clear Cart**   | Now clears cart, total_amount, user_email, username                     |
| **Payment Model Safety**        | Added try/except with fallback rule-based detection                     |
| **Duplicate Imports**           | Removed all duplicate imports across all files                          |
| **Cancel Payment Button**       | Added to payment page                                                   |
| **Password Reset**              | Now accepts email OR phone number                                       |
| **Cart Remove Item**            | Added remove button for each item                                       |

## 📁 Project Structure

```
shopzone/
├── .streamlit/
│   └── config.toml          # Hides native sidebar navigation
├── database/
│   ├── __init__.py
│   ├── db.py                # Database setup
│   ├── auth.py              # bcrypt authentication
│   └── logger.py            # Transaction logging
├── models/                  # ML model files (optional)
│   ├── ecommerce_fraud_model.pkl
│   └── ecommerce_encoder.pkl
├── app.py                   # Main entry point (router)
├── products.py              # Product catalog
├── cart.py                  # Shopping cart
├── payment.py               # Secure checkout
├── admin.py                 # Admin dashboard
├── forgot_password.py       # Password reset
├── requirements.txt
├── .env                     # Environment variables (create from .env.example)
└── README.md
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and set your admin credentials
```

### 3. Generate Admin Password Hash

```python
import bcrypt
password = "your_admin_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())
# Copy this hash to ADMIN_PASSWORD_HASH in .env
```

### 4. Run the App

```bash
streamlit run app.py
```

## 👤 User Roles

### Normal User (after login)

- **Sidebar shows**: Products, Cart, Payment
- **Can**: Browse products, add to cart, checkout, cancel payment
- **Cannot see**: Admin dashboard, forgot password page (only accessible from login)

### Admin (after staff login)

- **Sidebar shows**: Admin Dashboard only
- **Can**: View transactions, download reports, download database
- **Cannot see**: Products, Cart, Payment

### Not Logged In

- **Sidebar shows**: Login only
- **Can**: Login, register, reset password, access staff login

## 🔒 Security Features

- **bcrypt password hashing** (not SHA256)
- **Environment variables** for admin credentials
- **Session timeout** (1 hour)
- **Payment fraud detection** (ML + rule-based fallback)
- **Account lockout** after 3 failed payment attempts
- **Luhn algorithm** card validation
- **AES-256** encrypted gateway tokens

## 📝 Notes

- The `config.toml` file is **required** to hide the native Streamlit multipage sidebar
- All pages must be registered in `st.navigation` for `st.switch_page()` to work
- The ML models in `models/` folder are optional - the app works with rule-based fallback
