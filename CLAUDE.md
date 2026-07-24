# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly" — a Flask expense tracker built as a step-by-step learning project. Route handlers and
templates are annotated with the step in which they get implemented (e.g. `# coming in Step 3`),
and stub files like `database/db.py` contain only a spec comment describing what to write. When
asked to "implement the next step," check `app.py` and `database/db.py` for the placeholder/stub
markers to see what's expected rather than assuming a feature is missing by design.

The Flask project lives in the `expense-tracker/` subdirectory of the repo root; the virtualenv
(`venv/`) is a sibling of that directory at the repo root, not inside it.

## Commands

Run from the repo root (`C:\Users\visha\Desktop\expense-tracker`):

```
# install deps (venv already exists at repo root)
venv\Scripts\pip install -r expense-tracker\requirements.txt

# run the dev server — serves on http://127.0.0.1:5001, debug=True
cd expense-tracker
..\venv\Scripts\python app.py

# run tests (pytest / pytest-flask are declared in requirements.txt; no test files exist yet)
..\venv\Scripts\pytest
```

## Architecture

- **`app.py`** — single-file Flask app. All routes are registered directly on `app` (no
  blueprints). Currently implemented: `/`, `/register`, `/login`, `/terms`, `/privacy` (all
  simple `render_template` calls, no session/auth logic yet). Placeholder routes
  (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`)
  return plain placeholder strings and are meant to be built out later.
- **`database/db.py`** — not yet implemented. Per its spec comment it should expose:
  - `get_db()` — SQLite connection with `row_factory` and foreign keys enabled
  - `init_db()` — creates tables with `CREATE TABLE IF NOT EXISTS`
  - `seed_db()` — inserts sample dev data
  Uses plain `sqlite3`, no ORM. The resulting DB file (`expense_tracker.db`) is gitignored.
- **Templates** (`templates/`) — Jinja2, all pages extend `base.html`, which defines the
  shared nav/footer and exposes `title`, `head`, `content`, `scripts` blocks. Auth pages
  (`login.html`, `register.html`) post directly to `/login` / `/register` with plain HTML
  forms (no CSRF/JS handling yet).
- **Static assets** (`static/`) — one global stylesheet (`css/style.css`); `js/main.js` is
  currently an empty stub for future step work.
