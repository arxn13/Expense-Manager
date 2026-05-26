# Personal Expense Tracker

A web application to track personal expenses, built with **FastAPI**, **SQLite**, **SQLAlchemy**, **Jinja2**, and **Bootstrap 5**.

---

## Features

- **Add expenses** — title, amount, category, date (defaults to today), optional note
- **View all expenses** — sorted newest first, all fields displayed
- **Edit expenses** — update any field in place
- **Delete expenses** — with confirmation prompt
- **Filter expenses** — by category, date range, or partial title search
- **Monthly summary** — current month total + category-wise breakdown with progress bars

---

## Project Structure

```
expense-tracker/
├── main.py           # FastAPI app — all routes and business logic
├── database.py       # SQLAlchemy engine, session factory, and Base class
├── models.py         # Expense ORM model and CATEGORIES constant
├── requirements.txt  # Python dependencies
├── static/
│   └── style.css     # Custom CSS (Bootstrap loaded from CDN)
├── templates/
│   ├── base.html     # Shared layout — navbar, Bootstrap, footer
│   ├── index.html    # Expense list + filter form
│   ├── add.html      # Add expense form
│   ├── edit.html     # Edit expense form
│   └── summary.html  # Monthly summary with category breakdown
└── expenses.db       # SQLite database (auto-created on first run)
```

---

## Setup & Run

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

### 3. Start the server

```bash
uvicorn main:app --reload
```

Open your browser at **http://127.0.0.1:8000**

---

## Routes

| Method | Path                | Description              |
|--------|---------------------|--------------------------|
| GET    | `/`                 | List all expenses (with filters) |
| GET    | `/add`              | Show add-expense form    |
| POST   | `/add`              | Create a new expense     |
| GET    | `/edit/{id}`        | Show edit form           |
| POST   | `/edit/{id}`        | Update an expense        |
| POST   | `/delete/{id}`      | Delete an expense        |
| GET    | `/summary`          | Monthly summary page     |

---

## Categories

`Food`, `Transport`, `Shopping`, `Bills`, `Entertainment`, `Other`

---

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| Empty expense list | Friendly empty-state with a "Add First Expense" call-to-action |
| Invalid amount | Re-renders form with error message; no database write |
| Missing required fields | Form-level validation with clear error list |
| Invalid date format | Error shown; form re-rendered with previous values |
| No filter results | "No expenses match your filters" message with clear-filter link |
| Expense not found (404) | FastAPI raises HTTPException with 404 status |

---

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Server | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (file-based, zero config) |
| Templates | Jinja2 |
| UI | Bootstrap 5.3 + Bootstrap Icons |

---

## Development Notes

- The SQLite database file (`expenses.db`) is created automatically in the working directory on first run.
- `--reload` in uvicorn restarts the server on every file save — ideal for development.
- Validation happens in the route handlers (server-side). No JavaScript validation is used, keeping the code simple.
- All monetary amounts are stored as `FLOAT`. For production use, consider `NUMERIC` / `Decimal`.
