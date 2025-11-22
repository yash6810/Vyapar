from sqlalchemy.orm import Session
from . import crud, schemas

def create_invoice(db: Session, invoice: schemas.InvoiceCreate, user_id: int):
    return crud.create_invoice(db=db, invoice=invoice, user_id=user_id)

def record_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    return crud.create_expense(db=db, expense=expense, user_id=user_id)

