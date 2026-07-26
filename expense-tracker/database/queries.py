from datetime import datetime

from database.db import get_db


def _format_member_since(created_at_str):
    dt = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%B %Y")


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": _format_member_since(row["created_at"]),
    }


def get_summary_stats(user_id):
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        transaction_count = totals["cnt"]
        if transaction_count == 0:
            return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}

        top_row = conn.execute(
            "SELECT category, SUM(amount) AS cat_total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY cat_total DESC, category ASC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    return {
        "total_spent": round(totals["total"], 2),
        "transaction_count": transaction_count,
        "top_category": top_row["category"],
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


def get_category_breakdown(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC, category ASC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    grand_total = sum(row["total"] for row in rows)
    breakdown = [
        {
            "name": row["category"],
            "amount": round(row["total"], 2),
            "pct": round(row["total"] / grand_total * 100),
        }
        for row in rows
    ]

    remainder = 100 - sum(item["pct"] for item in breakdown)
    breakdown[0]["pct"] += remainder

    return breakdown
