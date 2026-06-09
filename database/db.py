import sqlite3
import os

DB_PATH = "database/fraud.db"


def init_db():
    """Create database folder and tables if they don't exist."""
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT,
        customer_name TEXT,
        product_name TEXT,
        card_number TEXT,
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


# Auto-run when imported
init_db()
