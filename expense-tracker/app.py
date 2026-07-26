import os
import sqlite3
from datetime import datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Presentation helpers                                                #
# ------------------------------------------------------------------ #

def format_currency(amount):
    return f"₹{amount:.2f}"


def format_txn_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")


def derive_initials(name):
    words = name.split()
    if not words:
        return ""
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def snap_bar_width(pct):
    return min(100, max(5, round(pct / 5) * 5))


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("register.html"), 400

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html"), 400

        try:
            user_id = create_user(name, email, password)
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
            return render_template("register.html"), 400

        session["user_id"] = user_id
        return redirect(url_for("profile"))
    else:
        abort(405)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user_row = get_user_by_id(user_id)
    if user_row is None:
        session.pop("user_id", None)
        return redirect(url_for("login"))

    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "member_since": user_row["member_since"],
        "initials": derive_initials(user_row["name"]),
    }

    stats_row = get_summary_stats(user_id)
    stats = {
        "total_spent": format_currency(stats_row["total_spent"]),
        "transaction_count": stats_row["transaction_count"],
        "top_category": stats_row["top_category"],
    }

    transactions = [
        {
            "date": format_txn_date(t["date"]),
            "description": t["description"],
            "category": t["category"],
            "amount": format_currency(t["amount"]),
        }
        for t in get_recent_transactions(user_id)
    ]

    categories = [
        {
            "name": c["name"],
            "total": format_currency(c["amount"]),
            "pct": c["pct"],
            "bar_width": snap_bar_width(c["pct"]),
        }
        for c in get_category_breakdown(user_id)
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
