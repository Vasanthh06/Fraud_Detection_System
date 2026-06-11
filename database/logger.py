import sqlite3
import os
from database.db import DB_PATH, verify_db


# ============================================================
# SAVE TRANSACTION
# ============================================================
def save_transaction(
    transaction_id,
    customer_name,
    product_name,
    card_masked,
    amount,
    country,
    device_type,
    transaction_hour,
    failed_attempts,
    risk_score,
    fraud_reason,
    status,
):
    """
    Save transaction into database.
    Returns True if successful.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO transactions
            (
                transaction_id,
                customer_name,
                product_name,
                card_masked,
                amount,
                country,
                device_type,
                transaction_hour,
                failed_attempts,
                risk_score,
                fraud_reason,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                customer_name,
                product_name,
                card_masked,
                amount,
                country,
                device_type,
                transaction_hour,
                failed_attempts,
                risk_score,
                fraud_reason,
                status,
            ),
        )

        conn.commit()

        print(
            f"[TRANSACTION SAVED] ID={transaction_id} | Amount={amount} | Status={status}"
        )

        return True

    except sqlite3.IntegrityError as e:
        print(f"[DUPLICATE TRANSACTION] {e}")
        return False

    except Exception as e:
        print(f"[SAVE ERROR] {e}")
        return False

    finally:
        conn.close()


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================
def get_all_transactions():
    """
    Returns all transactions.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                transaction_id,
                customer_name,
                product_name,
                card_masked,
                amount,
                country,
                device_type,
                transaction_hour,
                failed_attempts,
                risk_score,
                fraud_reason,
                status,
                created_at
            FROM transactions
            ORDER BY created_at DESC
            """)

        rows = cursor.fetchall()

        print(f"[FETCH] Found {len(rows)} transactions")

        return rows

    except Exception as e:
        print(f"[FETCH ERROR] {e}")
        return []

    finally:
        conn.close()


# ============================================================
# GET SINGLE TRANSACTION
# ============================================================
def get_transaction_by_id(transaction_id):
    """
    Fetch one transaction by ID.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM transactions
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )

        row = cursor.fetchone()

        return row

    except Exception as e:
        print(f"[GET ERROR] {e}")
        return None

    finally:
        conn.close()


# ============================================================
# GET FRAUD TRANSACTIONS
# ============================================================
def get_fraud_transactions():
    """
    Returns all fraud transactions.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM transactions
            WHERE status = 'Fraud'
            ORDER BY created_at DESC
            """)

        return cursor.fetchall()

    except Exception as e:
        print(f"[FRAUD FETCH ERROR] {e}")
        return []

    finally:
        conn.close()


# ============================================================
# GET GENUINE TRANSACTIONS
# ============================================================
def get_genuine_transactions():
    """
    Returns all genuine transactions.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM transactions
            WHERE status = 'Genuine'
            ORDER BY created_at DESC
            """)

        return cursor.fetchall()

    except Exception as e:
        print(f"[GENUINE FETCH ERROR] {e}")
        return []

    finally:
        conn.close()


# ============================================================
# TOTAL TRANSACTION COUNT
# ============================================================
def get_transaction_count():
    """
    Returns total transaction count.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions
            """)

        result = cursor.fetchone()

        return result[0]

    except Exception as e:
        print(f"[COUNT ERROR] {e}")
        return 0

    finally:
        conn.close()


# ============================================================
# TOTAL VOLUME
# ============================================================
def get_total_volume():
    """
    Returns total transaction amount.
    """

    verify_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT SUM(amount)
            FROM transactions
            """)

        result = cursor.fetchone()

        return result[0] if result[0] else 0

    except Exception as e:
        print(f"[VOLUME ERROR] {e}")
        return 0

    finally:
        conn.close()


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================
def database_status():
    """
    Simple DB status checker.
    """

    exists = os.path.exists(DB_PATH)

    return {
        "database_exists": exists,
        "database_path": DB_PATH,
    }
