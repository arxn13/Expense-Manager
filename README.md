# Expense Tracker

A simple Personal Expense Tracker built using FastAPI, SQLite, SQLAlchemy and Jinja2 templates.

## Features

- Add expenses
  - Title
  - Amount
  - Category
  - Date
  - Note (optional)

- View all expenses
  - Sorted by most recent
  - Displays all fields

- Edit expenses

- Delete expenses

- Filter expenses by:
  - Category
  - Date range
  - Partial title search

- Monthly summary:
  - Total spending
  - Category-wise breakdown

- Edge case handling:
  - Empty expense list
  - Invalid inputs
  - Missing values
  - No search results

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy ORM

### Database
- SQLite

### Frontend
- Jinja2 Templates
- HTML
- Bootstrap CSS

---

## Project Structure

```txt
expense-tracker/

main.py
database.py
models.py
requirements.txt
expenses.db

templates/
    index.html
    edit.html
    summary.html

static/
    style.css

README.md
```

---

## Installation

Clone repository:

```bash
git clone https://github.com/arxn13/expense-tracker.git

cd expense-tracker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
uvicorn main:app --reload
```

Open browser:

```txt
http://127.0.0.1:8000
```

---

## Database

SQLite database:

```txt
expenses.db
```

Stores:

- id
- title
- amount
- category
- date
- note

---

## Design Decisions

SQLite chosen because:

- Lightweight
- No separate DB server needed
- Fast setup
- Suitable for local applications

FastAPI chosen because:

- Fast development
- Automatic validation
- Easy routing
- Lightweight

Jinja templates chosen because:

- Faster than building React frontend
- Simpler for timed assessments

---

## Tradeoffs

Current implementation prioritizes:

- Working functionality
- Speed of development
- Simplicity

Over:

- Authentication
- Deployment
- Extensive testing
- Multi-user support

---

## Known Issues

Possible issues:

- SQLite not ideal for large-scale concurrent users
- No authentication
- Minimal styling
- No pagination

---

## Future Improvements

Potential additions:

- User login/authentication
- CSV export
- Charts and analytics
- API endpoints
- Cloud deployment
- Multi-user support

---

## Author

GitHub:

https://github.com/arxn13

Project:

https://github.com/arxn13/expense-tracker
