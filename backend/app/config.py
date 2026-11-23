"""Shopzone configuration.

Reads optional .env from the project root. The defaults are demo-safe:
the bundled admin hash matches ADMIN_EMAIL / admin123 so the project runs
with zero configuration, exactly like the original Streamlit build.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_HERE = Path(__file__).resolve()
# Layout: Shopzone/backend/app/config.py -> ROOT = Shopzone/
ROOT = _HERE.parents[2]

load_dotenv(ROOT / ".env")

APP_NAME = "Shopzone"
ENV = os.getenv("ENV", "development")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Admin credentials (same mechanism as the original database/auth.py)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "adminhere@gmail.com")
# bcrypt hash of "admin123" — override with ADMIN_PASSWORD_HASH in production
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "$2b$12$XSbtGRs8ZuYNEi4T6vPyE.HAy6irouBWaGLt1JdcG5YUbDr9YXi0e",
)

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-shopzone-secret-key-2026")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "12"))

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "shopzone.db")))

MODELS_DIR = ROOT / "models"
ECOM_MODEL_PATH = MODELS_DIR / "ecommerce_fraud_model.pkl"
ECOM_ENCODER_PATH = MODELS_DIR / "ecommerce_encoder.pkl"
CARD_MODEL_PATH = MODELS_DIR / "fraud_model.pkl"
CARD_SCALER_PATH = MODELS_DIR / "scaler.pkl"

# ---- optional Neon Postgres (production). Empty = local SQLite. ----
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# ---- public base URL (used in email links; set on Render) ----
# Updated fallback to your custom domain just in case
APP_URL = os.getenv("APP_URL", "https://www.fraudetect.site").rstrip("/")

# ---- Resend transactional email (empty key = dev outbox mode) ----
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
# Updated fallback to your verified custom domain
RESEND_FROM = os.getenv("RESEND_FROM", "ShopZone <noreply@fraudetect.site>")

# ---- CORS: same-origin app needs no wildcards; extend via env on Render ----
CORS_ORIGINS = [
    o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",") if o.strip()
]

FRONTEND_DIR = ROOT / "frontend"