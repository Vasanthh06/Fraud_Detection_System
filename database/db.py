import os
import sqlite3

# Use absolute path based on this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "shopzone.db")


def init_db():
    """Initialize the database with all required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            failed_payment_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product_name TEXT,
            card_masked TEXT,
            amount REAL,
            country TEXT,
            device_type TEXT,
            transaction_hour INTEGER,
            failed_attempts INTEGER,
            risk_score REAL,
            fraud_reason TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB INIT] Database initialized at: {DB_PATH}")


def verify_db():
    """Verify database exists and has required tables.

    Auto-creates if missing, and safely patches existing schemas.
    """
    if not os.path.exists(DB_PATH):
        print(f"[DB VERIFY] Database not found at {DB_PATH}, initializing...")
        init_db()
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if transactions table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        )
        result = cursor.fetchone()

        if not result:
            print("[DB VERIFY] Transactions table missing, re-initializing...")
            conn.close()
            init_db()
            return False

        # --- SAFE MIGRATION LOGIC INSIDE AN OPEN CONNECTION ---
        # This fixes older versions of shopzone.db if they are missing the phone column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT;")
            conn.commit()
            print("[DB MIGRATION] Safely added 'phone' column to users table.")
        except sqlite3.OperationalError:
            pass  # Column already exists, safe to ignore

        conn.close()
        return True
    except Exception as e:
        print(f"[DB VERIFY] Error: {e}")
        return False


# Auto-init on import
verify_db()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")
