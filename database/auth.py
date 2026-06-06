import sqlite3

def register_user(name, email, password):
    conn = sqlite3.connect("database/fraud.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users(name,email,password)
        VALUES(?,?,?)
        """,
        (name,email,password)
    )

    conn.commit()
    conn.close()


def login_user(email,password):
    conn = sqlite3.connect("database/fraud.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE email=? AND password=?
        """,
        (email,password)
    )

    user = cursor.fetchone()

    conn.close()

    return user

