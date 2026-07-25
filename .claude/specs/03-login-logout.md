# Spec: Login and Logout

## Overview
This feature wires up real session-based authentication for Spendly. `/login` and `/register`
currently just render static forms with no backend logic, and `/logout` is a placeholder string.
This step makes `/register` create a user, `/login` verify credentials and start a session, and
`/logout` clear it — giving the app its first notion of "who is signed in," which every later
step (profile, expenses) depends on.

## Depends on
- Step 1 — Database Setup (`database/db.py`: `get_db`, `init_db`, `seed_db`, `users` table). Complete.

## Routes
- `GET /register` — render registration form — public (already exists, unchanged)
- `POST /register` — create a new user, hash password, start session, redirect to profile — public
- `GET /login` — render login form — public (already exists, unchanged)
- `POST /login` — verify credentials, start session, redirect to profile — public
- `GET /logout` — clear session, redirect to landing page — logged-in

## Database changes
No database changes. The `users` table (`id`, `name`, `email`, `password_hash`, `created_at`)
already supports this feature as defined in `database/db.py`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — display `{{ error }}` on failed login (already has the block; no
    structural change needed, just confirm it renders the message passed from `app.py`)
  - `templates/register.html` — display `{{ error }}` on failed registration (same as above)
  - `templates/base.html` — nav currently always shows "Sign in" / "Get started"; switch to
    showing "Logout" (and optionally the user's name) when a session is active, `session.get("user_id")`

## Files to change
- `app.py` — add `secret_key`, implement `POST /register`, `POST /login`, `GET /logout` logic
- `templates/base.html` — conditional nav based on session state

## Files to create
None

## New dependencies
No new dependencies. `flask.session`, `werkzeug.security.generate_password_hash`, and
`werkzeug.security.check_password_hash` are already available.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Set `app.secret_key` from an environment variable with a hardcoded dev fallback (no secrets committed)
- On duplicate email during registration, re-render `register.html` with an `error` message and HTTP 400 — do not raise an unhandled exception
- On invalid credentials during login, re-render `login.html` with a generic `error` message (do not reveal whether the email exists)
- Store only `user_id` in the session — never the password hash
- `/logout` must work even if no session exists (no error if already logged out)

## Definition of done
- [ ] Visiting `/register`, submitting a new name/email/password creates a row in `users` with a hashed password and redirects to `/profile`
- [ ] Registering with an email that already exists re-renders `register.html` with an error and does not create a duplicate row
- [ ] Visiting `/login` with the seeded demo user (`demo@spendly.com` / `demo123`) logs in and redirects to `/profile`
- [ ] Visiting `/login` with a wrong password re-renders `login.html` with an error and does not start a session
- [ ] After logging in, the nav bar shows a "Logout" link instead of "Sign in" / "Get started"
- [ ] Visiting `/logout` clears the session and redirects to `/`, after which the nav bar reverts to "Sign in" / "Get started"
- [ ] Visiting `/logout` directly with no active session does not raise an error
- [ ] Restarting the Flask app (`python app.py`) still starts cleanly with no errors
