import re

import database.queries as queries


# ---- get_user_by_id ----

def test_get_user_by_id_valid(app, demo_user_id):
    user = queries.get_user_by_id(demo_user_id)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert re.match(r"^[A-Z][a-z]+ \d{4}$", user["member_since"])


def test_get_user_by_id_nonexistent(app):
    assert queries.get_user_by_id(999999) is None


# ---- get_summary_stats ----

def test_get_summary_stats_with_expenses(app, demo_user_id):
    stats = queries.get_summary_stats(demo_user_id)
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"
    assert stats["total_spent"] == 347.99


def test_get_summary_stats_no_expenses(app, new_user_id):
    assert queries.get_summary_stats(new_user_id) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


# ---- get_recent_transactions ----

def test_get_recent_transactions_with_expenses(app, demo_user_id):
    txns = queries.get_recent_transactions(demo_user_id)
    assert len(txns) == 8
    dates = [t["date"] for t in txns]
    assert dates == sorted(dates, reverse=True)
    for t in txns:
        assert set(t.keys()) == {"date", "description", "category", "amount"}


def test_get_recent_transactions_no_expenses(app, new_user_id):
    assert queries.get_recent_transactions(new_user_id) == []


# ---- get_category_breakdown ----

def test_get_category_breakdown_with_expenses(app, demo_user_id):
    cats = queries.get_category_breakdown(demo_user_id)
    assert len(cats) == 7
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True)
    assert all(isinstance(c["pct"], int) for c in cats)
    assert sum(c["pct"] for c in cats) == 100


def test_get_category_breakdown_no_expenses(app, new_user_id):
    assert queries.get_category_breakdown(new_user_id) == []


# ---- route tests ----

def test_profile_unauthenticated_redirects(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_authenticated_seed_user(client, demo_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = demo_user_id

    resp = client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "₹347.99" in body
    assert "Bills" in body

    for name in ["Food", "Bills", "Shopping", "Transport", "Entertainment", "Health", "Other"]:
        assert name in body

    ordered_descriptions = [t["description"] for t in queries.get_recent_transactions(demo_user_id)]
    positions = [body.find(desc) for desc in ordered_descriptions]
    assert all(p != -1 for p in positions)
    assert positions == sorted(positions)


def test_profile_new_user_no_expenses(client, new_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = new_user_id

    resp = client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert "₹0.00" in body
    assert "{{" not in body
    assert "Traceback" not in body
