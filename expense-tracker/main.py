import datetime
from typing import Optional

from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import extract
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from models import Expense, CATEGORIES

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Expense Tracker")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ─────────────────────────────────────────────
# LIST / HOME
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def list_expenses(
    request: Request,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    errors = []
    query = db.query(Expense)

    if category and category in CATEGORIES:
        query = query.filter(Expense.category == category)

    if date_from:
        try:
            df = datetime.date.fromisoformat(date_from)
            query = query.filter(Expense.date >= df)
        except ValueError:
            errors.append("Invalid 'From Date' format. Use YYYY-MM-DD.")

    if date_to:
        try:
            dt = datetime.date.fromisoformat(date_to)
            query = query.filter(Expense.date <= dt)
        except ValueError:
            errors.append("Invalid 'To Date' format. Use YYYY-MM-DD.")

    if search:
        query = query.filter(Expense.title.ilike(f"%{search}%"))

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = sum(e.amount for e in expenses)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "expenses": expenses,
            "categories": CATEGORIES,
            "total": total,
            "filters": {
                "category": category or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
                "search": search or "",
            },
            "errors": errors,
        },
    )


# ─────────────────────────────────────────────
# ADD EXPENSE
# ─────────────────────────────────────────────

@app.get("/add", response_class=HTMLResponse)
def add_expense_form(request: Request):
    return templates.TemplateResponse(
        request,
        "add.html",
        {
            "categories": CATEGORIES,
            "today": datetime.date.today().isoformat(),
            "errors": [],
            "form": {},
        },
    )


@app.post("/add", response_class=HTMLResponse)
def add_expense(
    request: Request,
    title: str = Form(...),
    amount: str = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    errors = []
    form_data = {
        "title": title,
        "amount": amount,
        "category": category,
        "date": date,
        "note": note,
    }

    # Validate title
    title = title.strip()
    if not title:
        errors.append("Title is required.")

    # Validate amount
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            errors.append("Amount must be a positive number.")
    except ValueError:
        amount_val = None
        errors.append("Amount must be a valid number (e.g. 12.50).")

    # Validate category
    if category not in CATEGORIES:
        errors.append(f"Category must be one of: {', '.join(CATEGORIES)}.")

    # Validate date
    try:
        date_val = datetime.date.fromisoformat(date)
    except ValueError:
        date_val = None
        errors.append("Date is invalid. Use YYYY-MM-DD format.")

    if errors:
        return templates.TemplateResponse(
            request,
            "add.html",
            {
                "categories": CATEGORIES,
                "today": datetime.date.today().isoformat(),
                "errors": errors,
                "form": form_data,
            },
            status_code=422,
        )

    expense = Expense(
        title=title,
        amount=amount_val,
        category=category,
        date=date_val,
        note=note.strip() or None,
    )
    db.add(expense)
    db.commit()

    return RedirectResponse(url="/?added=1", status_code=303)


# ─────────────────────────────────────────────
# EDIT EXPENSE
# ─────────────────────────────────────────────

@app.get("/edit/{expense_id}", response_class=HTMLResponse)
def edit_expense_form(expense_id: int, request: Request, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return templates.TemplateResponse(
        request,
        "edit.html",
        {
            "expense": expense,
            "categories": CATEGORIES,
            "errors": [],
        },
    )


@app.post("/edit/{expense_id}", response_class=HTMLResponse)
def edit_expense(
    expense_id: int,
    request: Request,
    title: str = Form(...),
    amount: str = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    errors = []

    title = title.strip()
    if not title:
        errors.append("Title is required.")

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            errors.append("Amount must be a positive number.")
    except ValueError:
        amount_val = None
        errors.append("Amount must be a valid number (e.g. 12.50).")

    if category not in CATEGORIES:
        errors.append(f"Category must be one of: {', '.join(CATEGORIES)}.")

    try:
        date_val = datetime.date.fromisoformat(date)
    except ValueError:
        date_val = None
        errors.append("Date is invalid. Use YYYY-MM-DD format.")

    if errors:
        return templates.TemplateResponse(
            request,
            "edit.html",
            {
                "expense": expense,
                "categories": CATEGORIES,
                "errors": errors,
            },
            status_code=422,
        )

    expense.title = title
    expense.amount = amount_val
    expense.category = category
    expense.date = date_val
    expense.note = note.strip() or None
    db.commit()

    return RedirectResponse(url="/?updated=1", status_code=303)


# ─────────────────────────────────────────────
# DELETE EXPENSE
# ─────────────────────────────────────────────

@app.post("/delete/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return RedirectResponse(url="/?deleted=1", status_code=303)


# ─────────────────────────────────────────────
# MONTHLY SUMMARY
# ─────────────────────────────────────────────

@app.get("/summary", response_class=HTMLResponse)
def monthly_summary(request: Request, db: Session = Depends(get_db)):
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    month_expenses = (
        db.query(Expense)
        .filter(
            extract("month", Expense.date) == current_month,
            extract("year", Expense.date) == current_year,
        )
        .all()
    )

    total = sum(e.amount for e in month_expenses)

    category_totals: dict = {cat: 0.0 for cat in CATEGORIES}
    for expense in month_expenses:
        category_totals[expense.category] = category_totals.get(expense.category, 0.0) + expense.amount

    category_breakdown = [
        {
            "category": cat,
            "total": category_totals[cat],
            "percent": round((category_totals[cat] / total * 100) if total else 0, 1),
        }
        for cat in CATEGORIES
    ]

    return templates.TemplateResponse(
        request,
        "summary.html",
        {
            "total": total,
            "month_name": today.strftime("%B %Y"),
            "category_breakdown": category_breakdown,
            "expense_count": len(month_expenses),
        },
    )
