import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fraud.db")


def register_user(name, email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users(name,email,password)
        VALUES(?,?,?)
        """,
        (name, email, password),
    )

    conn.commit()
    conn.close()


def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE email=? AND password=?
        """,
        (email, password),
    )

    user = cursor.fetchone()

    conn.close()

    return user
