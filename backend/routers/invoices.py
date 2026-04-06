from datetime import date
from typing import Optional, List
from calendar import monthrange

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.get("/", response_model=List[schemas.Invoice])
def list_invoices(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """List invoices with optional filters. Only returns current user's data."""
    return crud.get_invoices(
        db, user_id=current_user.id, skip=skip, limit=limit,
        start_date=start_date, end_date=end_date,
        status=status, search=search,
    )


@router.get("/summary/monthly", response_model=schemas.InvoiceSummary)
def monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoice summary for a specific month."""
    today = date.today()
    y = year or today.year
    m = month or today.month
    start = date(y, m, 1)
    end = date(y, m, monthrange(y, m)[1])
    return crud.get_invoice_summary(db, current_user.id, start, end, period_label=f"{y}-{m:02d}")


@router.get("/summary/yearly", response_model=schemas.InvoiceSummary)
def yearly_summary(
    year: int = Query(default=None),
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoice summary for a full year."""
    y = year or date.today().year
    start = date(y, 1, 1)
    end = date(y, 12, 31)
    return crud.get_invoice_summary(db, current_user.id, start, end, period_label=str(y))


@router.get("/{invoice_id}", response_model=schemas.Invoice)
def get_invoice(
    invoice_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific invoice by ID."""
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice or invoice.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/", response_model=schemas.Invoice, status_code=201)
def create_invoice(
    invoice: schemas.InvoiceCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new invoice with auto-generated invoice number."""
    return crud.create_invoice(db, invoice, current_user.id)


@router.put("/{invoice_id}", response_model=schemas.Invoice)
def update_invoice(
    invoice_id: int,
    invoice: schemas.InvoiceUpdate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing invoice."""
    updated = crud.update_invoice(db, invoice_id, invoice, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.post("/{invoice_id}/mark-paid", response_model=schemas.Invoice)
def mark_invoice_paid(
    invoice_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Mark an invoice as paid."""
    update = schemas.InvoiceUpdate(status="paid")
    updated = crud.update_invoice(db, invoice_id, update, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.post("/{invoice_id}/mark-sent", response_model=schemas.Invoice)
def mark_invoice_sent(
    invoice_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Mark an invoice as sent."""
    update = schemas.InvoiceUpdate(status="sent")
    updated = crud.update_invoice(db, invoice_id, update, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.delete("/{invoice_id}", response_model=schemas.Invoice)
def delete_invoice(
    invoice_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an invoice."""
    deleted = crud.delete_invoice(db, invoice_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return deleted
