import calendar
import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# Resolved relative to this file's location (not cwd) so the DB always lands
# in the project root, as a sibling of app.py.
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "expense_tracker.db")
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        if existing["count"] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cur.lastrowid

        # Spread 8 dates evenly across the current month regardless of month
        # length (28-31 days) or what day-of-month seeding actually runs on.
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        step = days_in_month // 8
        sample_days = [1 + i * step for i in range(8)]

        sample_expenses = [
            (32.50, "Food", "Groceries"),
            (45.00, "Transport", "Monthly metro pass"),
            (89.99, "Bills", "Electricity bill"),
            (23.50, "Health", "Pharmacy"),
            (32.00, "Entertainment", "Movie tickets"),
            (67.25, "Shopping", "New shoes"),
            (15.00, "Other", "Miscellaneous"),
            (42.75, "Food", "Restaurant dinner"),
        ]

        for day, (amount, category, description) in zip(sample_days, sample_expenses):
            expense_date = date(today.year, today.month, day).isoformat()
            conn.execute(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, category, expense_date, description),
            )

        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    conn = get_db()
    try:
        password_hash = generate_password_hash(password)
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
