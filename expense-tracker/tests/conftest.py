import pytest


@pytest.fixture()
def app(tmp_path, monkeypatch):
    import database.db as db_module

    db_path = tmp_path / "test_expense_tracker.db"
    monkeypatch.setattr(db_module, "DB_PATH", str(db_path))

    db_module.init_db()
    db_module.seed_db()

    from app import app as flask_app

    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture()
def demo_user_id(app):
    import database.db as db_module

    row = db_module.get_user_by_email("demo@spendly.com")
    return row["id"]


@pytest.fixture()
def new_user_id(app):
    import database.db as db_module

    return db_module.create_user("Brand New User", "newuser@example.com", "password123")
