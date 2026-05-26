# Personal Expense Tracker

A server-side rendered web application for tracking daily expenses, built as a software engineering practical test.

---

## Setup & Run

### Prerequisites

- Python 3.10 or later
- pip

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate.bat       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the development server

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

The SQLite database file (`expenses.db`) is created automatically in the working directory on first run. No database setup or migrations are needed.

### 4. Stop the server

Press `Ctrl + C` in the terminal.

---

## Project Structure

```
expense-tracker/
├── main.py           # FastAPI app — all routes and business logic
├── database.py       # SQLAlchemy engine, session factory, and Base class
├── models.py         # Expense ORM model and CATEGORIES constant
├── requirements.txt  # Pinned Python dependencies
├── static/
│   └── style.css     # Custom CSS (Bootstrap loaded from CDN)
├── templates/
│   ├── base.html     # Shared layout — navbar, Bootstrap, footer
│   ├── index.html    # Expense list + filter form
│   ├── add.html      # Add expense form
│   ├── edit.html     # Edit / delete form
│   └── summary.html  # Monthly summary with category breakdown
└── expenses.db       # SQLite database (auto-created, git-ignored)
```

---

## Routes

| Method | Path             | Description                        |
|--------|------------------|------------------------------------|
| GET    | `/`              | List all expenses (with filters)   |
| GET    | `/add`           | Show add-expense form              |
| POST   | `/add`           | Create a new expense               |
| GET    | `/edit/{id}`     | Show edit form                     |
| POST   | `/edit/{id}`     | Update an expense                  |
| POST   | `/delete/{id}`   | Delete an expense                  |
| GET    | `/summary`       | Monthly summary page               |

---

## Stack Choices

### FastAPI
Chosen over Flask because it ships with automatic data validation (via Pydantic), async support, and interactive API docs (`/docs`) out of the box. It has a shallow learning curve — routes look nearly identical to Flask — but the type annotations make bugs easier to catch during development.

### SQLite + SQLAlchemy ORM
SQLite requires zero infrastructure: no server to install, no connection string to configure, the database is just a file. It is the right default for a local, single-user app like this. SQLAlchemy adds a clean ORM layer so queries read as Python rather than raw SQL strings, which keeps the code easier to follow and refactor.

### Jinja2 Templates (Server-Side Rendering)
Instead of a separate frontend framework, Jinja2 renders HTML on the server. This eliminates the need for a build pipeline, a separate API layer, and JavaScript state management. For a CRUD app with straightforward pages, SSR is simpler to write, simpler to debug, and simpler to hand off.

### Bootstrap 5 (CDN)
Loaded from a CDN rather than bundled — no Node.js, no npm, no build step. Provides a production-quality responsive UI with minimal custom CSS. Bootstrap Icons add inline SVG-quality icons without an extra dependency.

### python-multipart
Required by FastAPI to parse `application/x-www-form-urlencoded` form data (the format HTML forms submit by default). Without it, `Form(...)` parameters raise a runtime error.

---

## Tradeoffs

| Decision | Benefit | Cost |
|---|---|---|
| SQLite over PostgreSQL | Zero setup, portable single file | Not suitable for concurrent writes or production multi-user deployments |
| SSR over React/Vue SPA | No build tooling, simpler codebase | Page reloads on every action; no optimistic UI updates |
| `FLOAT` for amounts | Simple Python type mapping | Floating-point rounding errors (e.g. `0.1 + 0.2 ≠ 0.3`); use `NUMERIC` / `Decimal` for production finance apps |
| Server-side validation only | Single source of truth, less code | Slightly slower feedback loop for the user vs. inline JS validation |
| POST for delete | Works without JavaScript | Not REST-idiomatic (should be `DELETE`); acceptable for a form-based app |
| No authentication | Faster to build and test | Anyone with the URL can view and modify all data |
| `--reload` in dev server | Auto-restart on file save | Slightly higher CPU usage; remove this flag for production |

---

## Skipped Features

These were left out intentionally to keep the project finishable within two hours. Each is a natural next step.

- **User authentication** — All data is shared globally. Adding login (e.g. via FastAPI's `OAuth2PasswordBearer` or a session cookie) would scope expenses per user.
- **Pagination** — The expense list loads all rows at once. For large datasets, `LIMIT` / `OFFSET` or cursor-based pagination should be added.
- **CSV / PDF export** — Users cannot download their data. A `/export` route returning a `StreamingResponse` with `text/csv` content would be straightforward to add.
- **Recurring expenses** — No concept of repeating entries (e.g. monthly rent). Would require a `recurrence` field and a scheduled background task.
- **Budget / spending limits** — No alerts when a category exceeds a threshold. Could be implemented as a per-category budget table with a comparison on the summary page.
- **Multi-currency support** — Amounts are stored as plain numbers with no currency code. All values are implicitly treated as the same currency.
- **Historical monthly summaries** — The summary page shows only the current month. A month-picker to browse past months was left out for simplicity.
- **Unit and integration tests** — No test suite is included. FastAPI's `TestClient` (built on `httpx`) makes it easy to add route-level tests.
- **Database migrations** — `metadata.create_all()` creates tables on startup but cannot evolve the schema after the first run. A tool like Alembic handles this.
- **Soft deletes** — Deleted expenses are permanently removed. Adding a `deleted_at` column would allow recovery.

---

## Known Issues

- **Amount precision** — Stored as SQL `FLOAT`, which is an IEEE 754 double. Amounts like `$9.99` may be stored as `9.989999999999999`. This is cosmetically hidden by the `"%.2f"` format filter in templates but is a real precision loss at the data layer. Fix: change the column to `Numeric(precision=10, scale=2)` and use Python `Decimal`.

- **No CSRF protection** — Forms submit to `POST` routes without a CSRF token. A malicious page could trick a logged-in user into modifying data. Acceptable for a local dev tool; unacceptable for a deployed app. Fix: add the `itsdangerous` or `starlette-csrf` library.

- **`expenses.db` in the working directory** — The database file is created wherever `uvicorn` is launched from. Running from a different directory creates a second, empty database. Fix: use an absolute path or an environment variable for `SQLALCHEMY_DATABASE_URL`.

- **`--reload` watches the whole directory** — Uvicorn's file watcher includes `expenses.db`. Heavy write activity can cause spurious reloads in development. Fix: pass `--reload-exclude expenses.db` or move the database outside the project directory.

- **No input length enforcement at the DB layer** — `title` is declared as `String(200)` in the model, but SQLite does not enforce `VARCHAR` length limits. Overly long titles are accepted silently. Fix: add a `max_length` check in the route handler or use a Pydantic schema for validation.

- **Delete uses POST, not DELETE** — HTML forms do not support the `DELETE` HTTP method natively. The delete action uses `POST /delete/{id}` instead. This works correctly but does not conform to REST conventions. Fix (optional): add a small JavaScript `fetch` call or use an `<input name="_method" value="DELETE">` override pattern.

---

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| Empty expense list | Friendly empty-state message with an "Add First Expense" button |
| No filter results | "No expenses match your filters" message with a clear-filter link |
| Invalid amount (text, zero, negative) | Form re-renders with the entered values preserved and a specific error message |
| Missing required fields | All errors collected and displayed as a list before the form |
| Invalid date string | Error shown; form re-rendered with previous values intact |
| Unknown expense ID | FastAPI raises `HTTPException(404)` |
| Unknown category value | Validated against the `CATEGORIES` list; rejected with an error |
