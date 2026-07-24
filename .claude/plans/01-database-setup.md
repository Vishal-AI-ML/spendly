# Plan: Step 1 — Database Setup (`database/db.py`)

## Context

Spendly is a step-by-step Flask learning project. Step 1 establishes the data layer:
`database/db.py` is currently just a stub comment, and every future feature (auth, profile,
expense CRUD) depends on it. The spec at `.claude/specs/01-database-setup.md` fully defines
the schema and required behavior for `get_db()`, `init_db()`, and `seed_db()`, plus the
`app.py` startup wiring. This plan implements that spec exactly, with no extra scope
(no ORM, no Flask `g`/teardown wiring, no new routes — those are explicitly out of scope
per the spec).

## Approach

### 1. `database/db.py` — full replacement of the stub

- **Path resolution**: resolve `expense_tracker.db` relative to `db.py`'s own file location
  (`os.path.dirname(os.path.abspath(__file__))`, joined with `..`), not cwd. This guarantees
  the DB always lands in the project root (sibling of `app.py`) regardless of where the
  process is launched from — matches the existing `.gitignore` entry (`expense_tracker.db`,
  no path prefix, sitting in the `expense-tracker/` root).

- **`get_db()`**: opens `sqlite3.connect(DB_PATH)`, sets `row_factory = sqlite3.Row`, runs
  `PRAGMA foreign_keys = ON`, returns the connection.

- **`init_db()`**: opens a connection via `get_db()`, runs two `CREATE TABLE IF NOT EXISTS`
  statements (schema below), commits, closes in a `finally` block.

  - `users`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `name TEXT NOT NULL`,
    `email TEXT UNIQUE NOT NULL`, `password_hash TEXT NOT NULL`,
    `created_at TEXT DEFAULT (datetime('now'))`.
  - `expenses`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `user_id INTEGER NOT NULL`,
    `amount REAL NOT NULL`, `category TEXT NOT NULL`, `date TEXT NOT NULL` (YYYY-MM-DD),
    `description TEXT` (nullable), `created_at TEXT DEFAULT (datetime('now'))`,
    `FOREIGN KEY (user_id) REFERENCES users (id)`.

- **`seed_db()`**: opens a connection, checks `SELECT COUNT(*) FROM users` — if non-zero,
  returns early (idempotent, no duplication). Otherwise:
  - Inserts demo user (`Demo User`, `demo@spendly.com`, password `demo123` hashed via
    `werkzeug.security.generate_password_hash`) using a parameterized `INSERT`.
  - Inserts 8 sample expenses linked to that user via `cur.lastrowid`, covering all 7 fixed
    categories (Food, Transport, Bills, Health, Entertainment, Shopping, Other — Food appears
    twice to reach 8 rows), with dates spread across the current month.
  - **Date spread**: use `calendar.monthrange(year, month)[1]` for days-in-month, then
    `step = days_in_month // 8` and `days = [1 + i*step for i in range(8)]`. Verified this
    produces 8 valid, distinct days (max day 22) for every real month length (28–31), so no
    clamping logic is needed and it works no matter what day of the month seeding runs on.
  - All SQL parameterized (`?` placeholders) — no string formatting, per spec rule.
  - Commits and closes in `finally`.

Each function opens/closes its own connection (no shared state, no Flask `g`) — connection
lifecycle management via `g`/teardown is explicitly out of scope since the spec doesn't call
for any new routes in this step.

### 2. `app.py` — wire up startup initialization

Add right after `app = Flask(__name__)` and before the routes section:

```python
from database.db import get_db, init_db, seed_db

with app.app_context():
    init_db()
    seed_db()
```

Placed at module level (not inside `if __name__ == "__main__":`) so it runs both under
`python app.py` and when the module is imported directly by pytest/pytest-flask later —
Python only executes module-level code once per process, so there's no double-init risk.
All existing routes (including the untouched placeholder routes) and the
`if __name__ == "__main__": app.run(...)` block at the bottom are left exactly as-is.

### Files changed
- `database/db.py` (full replacement of stub)
- `app.py` (add import + startup block only)

No new files, no new dependencies (`werkzeug` already in `requirements.txt`).

## Verification

1. Run `..\venv\Scripts\python app.py` from `expense-tracker/` (or via the documented repo-root
   command) — confirm it starts without errors and `expense_tracker.db` appears in the project
   root.
2. Inspect the DB (e.g. `python -c` with `sqlite3`, or any SQLite browser) — confirm `users`
   has exactly 1 row with a hashed (not plaintext) password, and `expenses` has exactly 8 rows
   spanning all 7 categories with `YYYY-MM-DD` dates.
3. Restart the app a second time — confirm row counts are unchanged (seed does not duplicate).
4. Sanity-check constraints via a quick REPL using `get_db()`: inserting a duplicate email
   should raise `sqlite3.IntegrityError` (UNIQUE); inserting an expense with a bogus `user_id`
   should raise `sqlite3.IntegrityError` (FOREIGN KEY) since `PRAGMA foreign_keys = ON` is set
   on every connection.
