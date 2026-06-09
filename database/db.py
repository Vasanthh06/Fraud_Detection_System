import sqlite3
import os

# ============================================================
# SINGLE SOURCE OF TRUTH FOR THE DATABASE PATH
# ============================================================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fraud.db")

_DB_INITIALISED = False


def init_db():
    global _DB_INITIALISED
    if _DB_INITIALISED:
        return

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Keep retrying if another process briefly holds the file
    import time

    for attempt in range(5):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=15)
            try:
                # Set WAL — if this fails (file locked by external tool) we
                # just skip it; the DB still works, just without WAL mode.
                try:
                    conn.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.OperationalError:
                    pass

                conn.execute("PRAGMA busy_timeout=15000;")

                conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name                  TEXT    NOT NULL,
                    email                 TEXT    UNIQUE NOT NULL,
                    password              TEXT    NOT NULL,
                    role                  TEXT    DEFAULT 'user',
                    failed_payment_streak INTEGER DEFAULT 0,
                    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id   TEXT,
                    customer_name    TEXT,
                    product_name     TEXT,
                    card_number      TEXT,
                    amount           REAL,
                    country          TEXT,
                    device_type      TEXT,
                    transaction_hour INTEGER,
                    failed_attempts  INTEGER,
                    risk_score       REAL,
                    fraud_reason     TEXT,
                    status           TEXT,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                conn.commit()
                _DB_INITIALISED = True
                return  # Success — exit

            finally:
                conn.close()

        except sqlite3.OperationalError as e:
            if attempt < 4:
                time.sleep(1)  # Wait 1 second and retry
                continue
            raise  # All 5 attempts failed — re-raise so Streamlit shows the error
