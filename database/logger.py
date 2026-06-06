import sqlite3

def save_transaction(
    transaction_id,
    customer_name,
    product_name,
    card_number,
    amount,
    country,
    device_type,
    transaction_hour,
    failed_attempts,
    risk_score,
    fraud_reason,
    status
):

    conn = sqlite3.connect("database/fraud.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions(
        transaction_id,
        customer_name,
        product_name,
        card_number,
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
        card_number,
        amount,
        country,
        device_type,
        transaction_hour,
        failed_attempts,
        risk_score,
        fraud_reason,
        status
    ))

    conn.commit()
    conn.close()