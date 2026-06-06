import sqlite3

conn = sqlite3.connect(
"database/fraud.db"
)

cursor = conn.cursor()

# ==================================

# TRANSACTIONS TABLE

# ==================================

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

# ==================================

# USERS TABLE

# ==================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
password TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

print(
"Database Created Successfully!"
)

conn.close()
