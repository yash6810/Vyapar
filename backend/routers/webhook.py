import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import crud, schemas, auth, llm_service
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])


@router.post("/text", response_model=schemas.WebhookResponse)
async def webhook_text(
    message: schemas.TextMessage,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Process a text message: classify intent → extract data → save."""
    logger.info(f"Text from {current_user.email}: {message.text[:100]}")

    intent = await llm_service.classify_intent(message.text)
    logger.info(f"Intent: {intent}")

    if intent == "expense_record":
        try:
            data = await llm_service.extract_expense(message.text)
            expense = schemas.ExpenseCreate(
                date=data.get("date", date.today().isoformat()),
                description=data.get("description", "Unknown"),
                amount=float(data.get("amount", 0)),
                category=data.get("category", "misc"),
                vendor=data.get("vendor"),
                payment_method=data.get("payment_method", "cash"),
                gst_applicable=data.get("gst_applicable", False),
                gst_amount=float(data.get("gst_amount", 0)),
                notes=data.get("notes"),
                source="text",
            )
            result = crud.create_expense(db, expense, current_user.id)
            return schemas.WebhookResponse(
                status="ok",
                message=f"✅ Expense recorded: {result.description} — ₹{result.amount:.2f}",
                data={"expense_id": result.id, "extracted": data},
            )
        except Exception as e:
            logger.error(f"Expense extraction failed: {e}")
            return schemas.WebhookResponse(
                status="error",
                message="I understood you want to record an expense, but couldn't extract the details. Please try again with format: 'Paid ₹500 to Sharma Store for groceries'",
            )

    elif intent == "invoice_create":
        try:
            data = await llm_service.extract_invoice(message.text)
            invoice = schemas.InvoiceCreate(
                date=data.get("date", date.today().isoformat()),
                customer_name=data.get("customer_name", "Unknown"),
                customer_email=data.get("customer_email"),
                customer_phone=data.get("customer_phone"),
                description=data.get("description"),
                amount=float(data.get("amount", 0)),
                gst_rate=float(data.get("gst_rate", 18.0)),
                gst_amount=float(data.get("gst_amount", 0)),
                total_amount=float(data.get("total_amount", 0)),
                due_date=data.get("due_date"),
                notes=data.get("notes"),
            )
            result = crud.create_invoice(db, invoice, current_user.id)
            return schemas.WebhookResponse(
                status="ok",
                message=f"✅ Invoice #{result.invoice_number} created for {result.customer_name} — ₹{result.total_amount:.2f}",
                data={"invoice_id": result.id, "invoice_number": result.invoice_number, "extracted": data},
            )
        except Exception as e:
            logger.error(f"Invoice extraction failed: {e}")
            return schemas.WebhookResponse(
                status="error",
                message="I understood you want to create an invoice. Please try: 'Create invoice for Rahul Sharma, ₹5000 for web design'",
            )

    elif intent == "gst_query":
        answer = await llm_service.answer_gst_query(message.text)
        return schemas.WebhookResponse(status="ok", message=answer)

    elif intent == "summary_request":
        # Return this month's expense summary
        today = date.today()
        start = date(today.year, today.month, 1)
        summary = crud.get_expense_summary(db, current_user.id, start, today, period_label=f"{today.year}-{today.month:02d}")
        msg = (
            f"📊 Summary for {summary['period']}:\n"
            f"Total: ₹{summary['total_amount']:,.2f}\n"
            f"Expenses: {summary['expense_count']}\n"
            f"GST Input: ₹{summary['gst_total']:,.2f}"
        )
        return schemas.WebhookResponse(status="ok", message=msg, data=summary)

    else:
        response = await llm_service.chat_response(message.text)
        return schemas.WebhookResponse(status="ok", message=response)


@router.post("/image", response_model=schemas.WebhookResponse)
async def webhook_image(
    image: UploadFile = File(...),
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Process an uploaded receipt/bill image using Gemini Vision."""
    logger.info(f"Image from {current_user.email}: {image.filename}")

    try:
        image_bytes = await image.read()
        mime_type = image.content_type or "image/jpeg"

        data = await llm_service.extract_from_receipt_image(image_bytes, mime_type)

        expense = schemas.ExpenseCreate(
            date=data.get("date", date.today().isoformat()),
            description=data.get("description", "Receipt expense"),
            amount=float(data.get("amount", 0)),
            category=data.get("category", "misc"),
            vendor=data.get("vendor"),
            payment_method=data.get("payment_method", "cash"),
            gst_applicable=data.get("gst_applicable", False),
            gst_amount=float(data.get("gst_amount", 0)),
            notes=data.get("notes"),
            source="ocr",
        )

        return schemas.WebhookResponse(
            status="ok",
            message="📸 Receipt scanned! Please confirm the details.",
            data={
                "extracted": data,
                "expense_preview": expense.model_dump(),
                "needs_confirmation": True,
            },
        )
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {e}")


@router.post("/image/confirm", response_model=schemas.WebhookResponse)
async def confirm_image_expense(
    expense: schemas.ExpenseCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm and save an expense extracted from a receipt image."""
    result = crud.create_expense(db, expense, current_user.id)
    return schemas.WebhookResponse(
        status="ok",
        message=f"✅ Expense saved: {result.description} — ₹{result.amount:.2f}",
        data={"expense_id": result.id},
    )
