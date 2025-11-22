from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class ExpenseBase(BaseModel):
    date: date
    item: str
    amount: float


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    date: date
    customer_name: str
    amount: float


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    expenses: List[Expense] = []
    invoices: List[Invoice] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
