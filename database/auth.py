import sqlite3
import hashlib
from database.db import DB_PATH, init_db


def hash_password(password):
    """Hashes a plain text password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def reset_password(email, new_password):
    """
    Updates the user's password securely in the database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)  # Fixed: Uses your global DB_PATH
    cursor = conn.cursor()
    try:
        # Fixed: Hashes the new password before storing it
        hashed_pwd = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?", (hashed_pwd, email)
        )
        conn.commit()

        rows_affected = cursor.rowcount
        return rows_affected > 0
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False
    finally:
        conn.close()


def register_user(name, email, phone, password):
    """Returns True if registered, False if email already exists."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        try:
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                (name, email, phone, hash_password(password)),
            )
        except sqlite3.OperationalError as e:
            if "no such column: phone" in str(e):
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
                cursor.execute(
                    "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                    (name, email, phone, hash_password(password)),
                )
            else:
                raise e
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
# FRAUD ISOLATION AND ACCOUNT LOCKOUT HANDLING MODULES
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
