import os
import sqlite3
import bcrypt
from database.db import DB_PATH, init_db

# ============================================================
# ADMIN CONFIG — FIXED: Hardcoded static fallback hash string
# ============================================================
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "adminhere@gmail.com")

# "admin123" pre-hashed with a static salt so it matches consistently
DEFAULT_ADMIN_HASH = "$2b$12$K7Y7m8kX9XzXp7K6vE7OeeGj6fG2O8B9Z1yK5YvM3h7mR1Z6z6v2O"

ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", DEFAULT_ADMIN_HASH)


def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================
# USER REGISTRATION — FIXED: bcrypt hashing
# ============================================================
def register_user(name, email, phone, password):
    """Register a new user with bcrypt hashed password."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, phone, password_hash)
            VALUES (?, ?, ?, ?)
        """,
            (name, email, phone, password_hash),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        conn.close()
        return False


# ============================================================
# USER LOGIN — FIXED: bcrypt verification
# ============================================================
def login_user(email, password):
    """Verify user login with bcrypt."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, phone, password_hash, failed_payment_streak
        FROM users WHERE email = ?
    """,
        (email,),
    )

    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user[4].encode()):
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3],
            "failed_payment_streak": user[5],
        }
    return None


# ============================================================
# ADMIN VERIFICATION — FIXED: bcrypt
# ============================================================
def verify_admin(email, password):
    """Verify admin credentials using bcrypt."""
    if email != ADMIN_EMAIL:
        return False
    return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())


# ============================================================
# PASSWORD RESET — FIXED: Email OR Phone
# ============================================================
def reset_password(identifier, new_password):
    """Reset password by email OR phone number."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = ? OR phone = ?",
        (identifier, identifier),
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False

    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    cursor.execute(
        """
        UPDATE users SET password_hash = ? WHERE email = ? OR phone = ?
    """,
        (new_hash, identifier, identifier),
    )

    conn.commit()
    conn.close()
    return True


# ============================================================
# PAYMENT STREAK TRACKING
# ============================================================
def get_failed_payment_streak(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT failed_payment_streak FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def increment_failed_payment_streak(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE users SET failed_payment_streak = failed_payment_streak + 1
        WHERE email = ?
    """,
        (email,),
    )
    conn.commit()
    conn.close()


def reset_failed_payment_streak(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET failed_payment_streak = 0 WHERE email = ?", (email,)
    )
    conn.commit()
    conn.close()
