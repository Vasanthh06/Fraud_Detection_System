import sqlite3
from database.db import DB_PATH


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
    """Save a transaction to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transactions
        (transaction_id, customer_name, product_name, card_masked, amount,
         country, device_type, transaction_hour, failed_attempts,
         risk_score, fraud_reason, status)
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
    conn.close()
