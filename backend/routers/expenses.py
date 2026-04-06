from datetime import date, timedelta
from typing import Optional, List
from calendar import monthrange

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


@router.get("/", response_model=List[schemas.Expense])
def list_expenses(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    search: Optional[str] = None,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """List expenses with optional filters. Only returns current user's data."""
    return crud.get_expenses(
        db, user_id=current_user.id, skip=skip, limit=limit,
        start_date=start_date, end_date=end_date,
        category=category, vendor=vendor, search=search,
    )


@router.get("/summary/daily", response_model=schemas.ExpenseSummary)
def daily_summary(
    target_date: Optional[date] = None,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get expense summary for a specific day (defaults to today)."""
    d = target_date or date.today()
    return crud.get_expense_summary(db, current_user.id, d, d, period_label=d.isoformat())


@router.get("/summary/monthly", response_model=schemas.ExpenseSummary)
def monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get expense summary for a specific month."""
    today = date.today()
    y = year or today.year
    m = month or today.month
    start = date(y, m, 1)
    end = date(y, m, monthrange(y, m)[1])
    return crud.get_expense_summary(db, current_user.id, start, end, period_label=f"{y}-{m:02d}")


@router.get("/summary/yearly", response_model=schemas.ExpenseSummary)
def yearly_summary(
    year: int = Query(default=None),
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get expense summary for a full year."""
    y = year or date.today().year
    start = date(y, 1, 1)
    end = date(y, 12, 31)
    return crud.get_expense_summary(db, current_user.id, start, end, period_label=str(y))


@router.get("/{expense_id}", response_model=schemas.Expense)
def get_expense(
    expense_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific expense by ID."""
    expense = crud.get_expense(db, expense_id)
    if not expense or expense.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("/", response_model=schemas.Expense, status_code=201)
def create_expense(
    expense: schemas.ExpenseCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new expense."""
    return crud.create_expense(db, expense, current_user.id)


@router.put("/{expense_id}", response_model=schemas.Expense)
def update_expense(
    expense_id: int,
    expense: schemas.ExpenseUpdate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing expense."""
    updated = crud.update_expense(db, expense_id, expense, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@router.delete("/{expense_id}", response_model=schemas.Expense)
def delete_expense(
    expense_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an expense."""
    deleted = crud.delete_expense(db, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return deleted
