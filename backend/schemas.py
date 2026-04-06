from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ── User ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    name: Optional[str] = None
    business_name: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    phone: Optional[str] = None


class User(UserBase):
    id: int
    name: Optional[str] = None
    business_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Expense ───────────────────────────────────────────────────────────────────

class ExpenseBase(BaseModel):
    date: date
    description: str
    amount: float = Field(gt=0)
    category: str = "misc"
    vendor: Optional[str] = None
    payment_method: str = "cash"
    currency: str = "INR"
    gst_applicable: bool = False
    gst_amount: float = 0.0
    tags: Optional[str] = None
    notes: Optional[str] = None
    source: str = "manual"


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    vendor: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None
    gst_applicable: Optional[bool] = None
    gst_amount: Optional[float] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class Expense(ExpenseBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Invoice ───────────────────────────────────────────────────────────────────

class InvoiceBase(BaseModel):
    date: date
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    description: Optional[str] = None
    amount: float = Field(gt=0)
    currency: str = "INR"
    gst_rate: float = 18.0
    gst_amount: float = 0.0
    total_amount: float = Field(gt=0)
    status: str = "draft"
    due_date: Optional[date] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    date: Optional[date] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    gst_rate: Optional[float] = None
    gst_amount: Optional[float] = None
    total_amount: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class Invoice(InvoiceBase):
    id: int
    invoice_number: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Summaries ─────────────────────────────────────────────────────────────────

class ExpenseSummary(BaseModel):
    total_amount: float
    expense_count: int
    by_category: dict = {}
    top_vendors: List[str] = []
    gst_total: float = 0.0
    period: str = ""


class InvoiceSummary(BaseModel):
    total_amount: float
    invoice_count: int
    paid_amount: float = 0.0
    pending_amount: float = 0.0
    overdue_count: int = 0
    by_status: dict = {}
    period: str = ""


# ── Webhook ───────────────────────────────────────────────────────────────────

class TextMessage(BaseModel):
    text: str


class WebhookResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
