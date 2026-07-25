import os
import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

with app.app_context():
    init_db()
    seed_db()


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
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "January 2026",
    }
    stats = {
        "total_spent": "₹348.00",
        "transaction_count": 8,
        "top_category": "Food",
    }
    transactions = [
        {"date": "Jul 22, 2026", "description": "Restaurant dinner", "category": "Food", "amount": "₹42.75"},
        {"date": "Jul 19, 2026", "description": "New shoes", "category": "Shopping", "amount": "₹67.25"},
        {"date": "Jul 15, 2026", "description": "Movie tickets", "category": "Entertainment", "amount": "₹32.00"},
        {"date": "Jul 12, 2026", "description": "Pharmacy", "category": "Health", "amount": "₹23.50"},
        {"date": "Jul 08, 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹89.99"},
        {"date": "Jul 05, 2026", "description": "Monthly metro pass", "category": "Transport", "amount": "₹45.00"},
        {"date": "Jul 01, 2026", "description": "Groceries", "category": "Food", "amount": "₹32.50"},
    ]
    # pct is each category's total relative to the largest category (Bills),
    # rounded to the nearest 5 so it maps onto the .bar-w-* utility classes.
    categories = [
        {"name": "Bills", "total": "₹89.99", "pct": 100},
        {"name": "Food", "total": "₹75.25", "pct": 85},
        {"name": "Shopping", "total": "₹67.25", "pct": 75},
        {"name": "Transport", "total": "₹45.00", "pct": 50},
        {"name": "Entertainment", "total": "₹32.00", "pct": 35},
        {"name": "Health", "total": "₹23.50", "pct": 25},
        {"name": "Other", "total": "₹15.00", "pct": 15},
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
