import sqlite3
import hashlib
from database.db import DB_PATH, init_db


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password):
    """Returns True if registered, False if email already exists."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(email, password):
    """Returns user row if credentials match, else None."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()
    return user


# ============================================================
# NEW: FRAUD ISOLATION AND ACCOUNT LOCKOUT HANDLING MODULES
# ============================================================


def get_failed_payment_streak(email):
    """Retrieves how many consecutive payment failures a customer has logged."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT failed_payment_streak FROM users WHERE email = ?", (email,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        # Self-healing database mechanism: creates column dynamically if it doesn't exist
        try:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN failed_payment_streak INTEGER DEFAULT 0"
            )
            conn.commit()
        except:
            pass
        return 0
    finally:
        conn.close()


def increment_failed_payment_streak(email):
    """Increments the failure tracking sequence by 1 when card processing flags an anomaly."""
    init_db()
    # First ensure the column exists by running a quick get request check
    get_failed_payment_streak(email)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET failed_payment_streak = COALESCE(failed_payment_streak, 0) + 1 WHERE email = ?",
            (email,),
        )
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()


def reset_failed_payment_streak(email):
    """Resets sequence tracker to 0 upon a completely successful genuine checkout settlement."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET failed_payment_streak = 0 WHERE email = ?", (email,)
        )
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()
