"""Storage layer — dual engine.

* **SQLite** (default, zero-config): file at data/shopzone.db, self-healing schema.
* **Neon / any Postgres** (production): set DATABASE_URL (e.g. Render + Neon).
  Same schema, same behaviour — only the SQL dialect and connection differ.

Every statement is parameterised (no string-built SQL) — SQL-injection safe.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import DATABASE_URL, DB_PATH

ENGINE = "postgres" if DATABASE_URL else "sqlite"

if ENGINE == "postgres":
    import psycopg2
    from psycopg2.extras import RealDictCursor


def _q(sql: str) -> str:
    """Translate ? placeholders to %s for psycopg2."""
    return sql if ENGINE == "sqlite" else sql.replace("?", "%s")


@contextmanager
def cursor(commit: bool = False):
    if ENGINE == "postgres":
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        has = cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
        if not has:  # self-healing: db file removed while running
            cur.close()
            conn.close()
            init_db()
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _rows(cur):
    return [dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------- schema

_SQLITE_DDL = [
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        failed_payment_streak INTEGER DEFAULT 0,
        location TEXT DEFAULT '',
        profile_image TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS transactions (
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_email TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_email, product_id)
    )""",
    """CREATE TABLE IF NOT EXISTS reset_tokens (
        token TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
]

_PG_DDL = [
    """CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        failed_payment_streak INTEGER DEFAULT 0,
        location TEXT DEFAULT '',
        profile_image TEXT DEFAULT '',
        created_at TIMESTAMPTZ DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        customer_name TEXT,
        product_name TEXT,
        card_masked TEXT,
        amount DOUBLE PRECISION,
        country TEXT,
        device_type TEXT,
        transaction_hour INTEGER,
        failed_attempts INTEGER,
        risk_score DOUBLE PRECISION,
        fraud_reason TEXT,
        status TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        user_email TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS wishlist (
        id SERIAL PRIMARY KEY,
        user_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        added_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(user_email, product_id)
    )""",
    """CREATE TABLE IF NOT EXISTS reset_tokens (
        token TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        expires_at TIMESTAMPTZ NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW()
    )""",
]


def init_db() -> None:
    if ENGINE == "postgres":
        with cursor(commit=True) as cur:
            for ddl in _PG_DDL:
                cur.execute(ddl)
        return
    conn = sqlite3.connect(DB_PATH)  # raw: cursor() would recurse pre-schema
    cur = conn.cursor()
    for ddl in _SQLITE_DDL:
        cur.execute(ddl)
    # legacy-file migrations (original project databases)
    for stmt in (
        "ALTER TABLE transactions ADD COLUMN user_email TEXT",
        "ALTER TABLE users ADD COLUMN location TEXT DEFAULT ''",
        "ALTER TABLE users ADD COLUMN profile_image TEXT DEFAULT ''",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------- users

def create_user(name: str, email: str, phone: str, password_hash: str) -> bool:
    with cursor() as cur:
        cur.execute(_q("SELECT id FROM users WHERE email = ?"), (email,))
        if cur.fetchone():
            return False
    with cursor(commit=True) as cur:
        try:
            cur.execute(
                _q("INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)"),
                (name, email, phone, password_hash),
            )
        except Exception:  # UNIQUE race (sqlite.IntegrityError / psycopg2.IntegrityError)
            return False
    return True


def get_user_by_email(email: str):
    with cursor() as cur:
        cur.execute(
            _q("SELECT id, name, email, phone, password_hash, failed_payment_streak,"
               " location, profile_image, created_at FROM users WHERE email = ?"),
            (email,),
        )
        row = cur.fetchone()
    return dict(row) if row else None


def reset_password(identifier: str, new_hash: str) -> bool:
    with cursor(commit=True) as cur:
        cur.execute(
            _q("UPDATE users SET password_hash = ? WHERE email = ? OR phone = ?"),
            (new_hash, identifier, identifier),
        )
        return cur.rowcount > 0


def update_profile(email: str, name: str, phone: str, location: str,
                   profile_image: str | None = None) -> bool:
    sql = ("UPDATE users SET name = ?, phone = ?, location = ?, profile_image = ? WHERE email = ?"
           if profile_image is not None else
           "UPDATE users SET name = ?, phone = ?, location = ? WHERE email = ?")
    args = ((name, phone, location, profile_image, email) if profile_image is not None
            else (name, phone, location, email))
    try:
        with cursor(commit=True) as cur:
            cur.execute(_q(sql), args)
            return cur.rowcount > 0
    except Exception:  # phone UNIQUE violation
        return False


def update_password_hash(email: str, new_hash: str) -> None:
    with cursor(commit=True) as cur:
        cur.execute(_q("UPDATE users SET password_hash = ? WHERE email = ?"), (new_hash, email))


# ---------------------------------------------------------------- streaks

def get_failed_payment_streak(email: str) -> int:
    with cursor() as cur:
        cur.execute(_q("SELECT failed_payment_streak FROM users WHERE email = ?"), (email,))
        row = cur.fetchone()
    return int(row["failed_payment_streak"] or 0) if row else 0


def increment_failed_payment_streak(email: str) -> None:
    with cursor(commit=True) as cur:
        cur.execute(
            _q("UPDATE users SET failed_payment_streak = COALESCE(failed_payment_streak, 0) + 1 WHERE email = ?"),
            (email,),
        )


def reset_failed_payment_streak(email: str) -> None:
    with cursor(commit=True) as cur:
        cur.execute(_q("UPDATE users SET failed_payment_streak = 0 WHERE email = ?"), (email,))


# ---------------------------------------------------------------- transactions

def save_transaction(transaction_id, customer_name, product_name, card_masked, amount,
                     country, device_type, transaction_hour, failed_attempts,
                     risk_score, fraud_reason, status, user_email=None) -> None:
    with cursor(commit=True) as cur:
        cur.execute(
            _q("""INSERT INTO transactions
                (transaction_id, customer_name, product_name, card_masked, amount,
                 country, device_type, transaction_hour, failed_attempts,
                 risk_score, fraud_reason, status, user_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""),
            (transaction_id, customer_name, product_name, card_masked, amount,
             country, device_type, transaction_hour, failed_attempts,
             risk_score, fraud_reason, status, user_email),
        )


def list_transactions(limit: int = 500, user_email: str | None = None):
    with cursor() as cur:
        if user_email:
            cur.execute(
                _q("SELECT * FROM transactions WHERE user_email = ? ORDER BY created_at DESC LIMIT ?"),
                (user_email, limit),
            )
        else:
            cur.execute(_q("SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?"), (limit,))
        return _rows(cur)


# ---------------------------------------------------------------- wishlist

def wishlist_list(email: str):
    with cursor() as cur:
        cur.execute(
            _q("SELECT product_id, added_at FROM wishlist WHERE user_email = ? ORDER BY added_at DESC"),
            (email,),
        )
        return _rows(cur)


def wishlist_add(email: str, product_id: int) -> None:
    with cursor(commit=True) as cur:
        try:
            cur.execute(
                _q("INSERT INTO wishlist (user_email, product_id) VALUES (?, ?)"),
                (email, product_id),
            )
        except Exception:
            pass  # already favourited


def wishlist_remove(email: str, product_id: int) -> None:
    with cursor(commit=True) as cur:
        cur.execute(
            _q("DELETE FROM wishlist WHERE user_email = ? AND product_id = ?"),
            (email, product_id),
        )


# ---------------------------------------------------------------- reset tokens

def create_reset_token(email: str, token: str, expires_iso: str) -> None:
    with cursor(commit=True) as cur:
        cur.execute(_q("DELETE FROM reset_tokens WHERE email = ? OR expires_at < ?"),
                    (email, now_iso()))
        cur.execute(
            _q("INSERT INTO reset_tokens (token, email, expires_at) VALUES (?, ?, ?)"),
            (token, email, expires_iso),
        )


def consume_reset_token(token: str) -> str | None:
    """Returns the email if the token is valid & unused, then marks it used."""
    if ENGINE == "postgres":
        sql = ("SELECT email FROM reset_tokens WHERE token = %s AND used = 0"
               " AND expires_at > NOW()")
        args = (token,)
    else:
        sql = ("SELECT email FROM reset_tokens WHERE token = ? AND used = 0"
               " AND expires_at > ?")
        args = (token, now_iso())
    with cursor(commit=True) as cur:
        cur.execute(sql, args)
        row = cur.fetchone()
        if not row:
            return None
        cur.execute(_q("UPDATE reset_tokens SET used = 1 WHERE token = ?"), (token,))
        return row["email"]


# ---------------------------------------------------------------- admin

def list_users_with_stats():
    with cursor() as cur:
        cur.execute(
            """SELECT u.name, u.email, u.phone, u.location, u.profile_image,
                      u.failed_payment_streak, u.created_at,
                      (SELECT COUNT(*) FROM transactions t WHERE t.user_email = u.email) AS tx_count,
                      (SELECT COUNT(*) FROM wishlist w WHERE w.user_email = u.email)  AS wish_count
               FROM users u ORDER BY u.created_at DESC"""
        )
        return _rows(cur)
