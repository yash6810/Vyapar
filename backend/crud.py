from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from typing import Optional, List
import uuid

from . import models, schemas, auth


# ── Users ─────────────────────────────────────────────────────────────────────

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        business_name=user.business_name,
        phone=user.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


# ── Expenses ──────────────────────────────────────────────────────────────────

def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()


def get_expenses(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(models.Expense).filter(models.Expense.owner_id == user_id)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if category:
        query = query.filter(models.Expense.category == category)
    if vendor:
        query = query.filter(models.Expense.vendor.ilike(f"%{vendor}%"))
    if search:
        query = query.filter(
            models.Expense.description.ilike(f"%{search}%")
            | models.Expense.vendor.ilike(f"%{search}%")
            | models.Expense.notes.ilike(f"%{search}%")
        )
    return query.order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()


def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.model_dump(), owner_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def update_expense(db: Session, expense_id: int, expense: schemas.ExpenseUpdate, user_id: int):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, models.Expense.owner_id == user_id
    ).first()
    if db_expense:
        update_data = expense.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int, user_id: int):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id, models.Expense.owner_id == user_id
    ).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense


def get_expense_summary(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    period_label: str = "",
) -> dict:
    """Aggregate expense data for a date range."""
    query = db.query(models.Expense).filter(
        models.Expense.owner_id == user_id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date,
    )
    expenses = query.all()

    total = sum(e.amount for e in expenses)
    gst_total = sum(e.gst_amount for e in expenses)

    # Group by category
    by_category = {}
    for e in expenses:
        cat = e.category or "misc"
        by_category[cat] = by_category.get(cat, 0) + e.amount

    # Top vendors
    vendor_totals = {}
    for e in expenses:
        if e.vendor:
            vendor_totals[e.vendor] = vendor_totals.get(e.vendor, 0) + e.amount
    top_vendors = sorted(vendor_totals, key=vendor_totals.get, reverse=True)[:5]

    return {
        "total_amount": round(total, 2),
        "expense_count": len(expenses),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "top_vendors": top_vendors,
        "gst_total": round(gst_total, 2),
        "period": period_label,
    }


# ── Invoices ──────────────────────────────────────────────────────────────────

def get_invoice(db: Session, invoice_id: int):
    return db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()


def get_invoices(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(models.Invoice).filter(models.Invoice.owner_id == user_id)
    if start_date:
        query = query.filter(models.Invoice.date >= start_date)
    if end_date:
        query = query.filter(models.Invoice.date <= end_date)
    if status:
        query = query.filter(models.Invoice.status == status)
    if search:
        query = query.filter(
            models.Invoice.customer_name.ilike(f"%{search}%")
            | models.Invoice.description.ilike(f"%{search}%")
        )
    return query.order_by(models.Invoice.date.desc()).offset(skip).limit(limit).all()


def _generate_invoice_number() -> str:
    """Generate a unique invoice number like VYP-20260406-A1B2."""
    today = date.today().strftime("%Y%m%d")
    short_id = uuid.uuid4().hex[:4].upper()
    return f"VYP-{today}-{short_id}"


def create_invoice(db: Session, invoice: schemas.InvoiceCreate, user_id: int):
    data = invoice.model_dump()
    data["invoice_number"] = _generate_invoice_number()
    db_invoice = models.Invoice(**data, owner_id=user_id)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def update_invoice(db: Session, invoice_id: int, invoice: schemas.InvoiceUpdate, user_id: int):
    db_invoice = db.query(models.Invoice).filter(
        models.Invoice.id == invoice_id, models.Invoice.owner_id == user_id
    ).first()
    if db_invoice:
        update_data = invoice.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_invoice, key, value)
        db.commit()
        db.refresh(db_invoice)
    return db_invoice


def delete_invoice(db: Session, invoice_id: int, user_id: int):
    db_invoice = db.query(models.Invoice).filter(
        models.Invoice.id == invoice_id, models.Invoice.owner_id == user_id
    ).first()
    if db_invoice:
        db.delete(db_invoice)
        db.commit()
    return db_invoice


def get_invoice_summary(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    period_label: str = "",
) -> dict:
    """Aggregate invoice data for a date range."""
    query = db.query(models.Invoice).filter(
        models.Invoice.owner_id == user_id,
        models.Invoice.date >= start_date,
        models.Invoice.date <= end_date,
    )
    invoices = query.all()

    total = sum(i.total_amount for i in invoices)
    paid = sum(i.total_amount for i in invoices if i.status == "paid")
    pending = sum(i.total_amount for i in invoices if i.status in ("draft", "sent"))
    overdue = sum(1 for i in invoices if i.status == "overdue")

    by_status = {}
    for i in invoices:
        st = i.status or "draft"
        by_status[st] = by_status.get(st, 0) + 1

    return {
        "total_amount": round(total, 2),
        "invoice_count": len(invoices),
        "paid_amount": round(paid, 2),
        "pending_amount": round(pending, 2),
        "overdue_count": overdue,
        "by_status": by_status,
        "period": period_label,
    }
