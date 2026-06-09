import sqlite3
import hashlib
from database.db import DB_PATH

# ============================================================
# NO init_db() import or call anywhere in this file.
# init_db() is called once at startup in app.py.
# Calling it here caused multiple concurrent connections
# which is what produces "database is locked".
# ============================================================


def _connect():
    """Open a connection with WAL mode and a busy timeout.
    ALWAYS use inside a 'with' block — it auto-closes on exit,
    even if an exception is raised mid-function.
    """
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str) -> bool:
    """Returns True if registered, False if email already exists."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hash_password(password)),
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # Duplicate email — expected, not a crash


def login_user(email: str, password: str):
    """Returns user row if credentials match, else None."""
    with _connect() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, hash_password(password)),
        )
        return cursor.fetchone()


# ============================================================
# FRAUD ISOLATION AND ACCOUNT LOCKOUT HANDLING MODULES
# ============================================================


def get_failed_payment_streak(email: str) -> int:
    """Retrieves how many consecutive payment failures a customer has logged."""
    with _connect() as conn:
        try:
            cursor = conn.execute(
                "SELECT failed_payment_streak FROM users WHERE email = ?", (email,)
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else 0
        except sqlite3.OperationalError:
            # Self-healing: column missing in older DB — add it once
            try:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN failed_payment_streak INTEGER DEFAULT 0"
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Already exists — safe to ignore
            return 0


def increment_failed_payment_streak(email: str) -> None:
    """Increments failure counter by 1 when a payment anomaly is flagged."""
    with _connect() as conn:
        conn.execute(
            """UPDATE users
               SET failed_payment_streak = COALESCE(failed_payment_streak, 0) + 1
               WHERE email = ?""",
            (email,),
        )
        conn.commit()


def reset_failed_payment_streak(email: str) -> None:
    """Resets counter to 0 after a successful genuine checkout."""
    with _connect() as conn:
        conn.execute(
            "UPDATE users SET failed_payment_streak = 0 WHERE email = ?",
            (email,),
        )
        conn.commit()


def reset_password(email: str, new_password: str) -> bool:
    """Returns True if password updated, False if email not found."""
    with _connect() as conn:
        cursor = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is None:
            return False
        conn.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hash_password(new_password), email),
        )
        conn.commit()
        return True
