import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "fraud.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TRANSACTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
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


# Automatically create database when imported
init_db()
