"""
Gemini API integration — replaces HF server, ASR service, intent classifier, and EasyOCR.
Single service handles: intent classification, expense/invoice extraction, receipt OCR, GST queries.
Free tier: 60 RPM for gemini-2.0-flash.
"""
import json
import logging
import base64
from typing import Optional
from datetime import date

import google.generativeai as genai
from .config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
_model = None


def _get_model():
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set. Get one free at https://aistudio.google.com")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(settings.GEMINI_MODEL)
    return _model


def _parse_json_from_text(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"Could not parse JSON from: {text[:200]}")


async def classify_intent(text: str) -> str:
    """Classify user intent into: expense_record, invoice_create, gst_query, summary_request, or fallback."""
    model = _get_model()
    prompt = f"""You are an intent classifier for an Indian SME accounting assistant. 
Classify the following text into exactly ONE of these intents:
- expense_record: User wants to record an expense/payment they made
- invoice_create: User wants to create/send an invoice to a customer
- gst_query: User is asking about GST rates, rules, compliance
- summary_request: User wants to see expense/invoice summaries or reports
- fallback: Anything else, greetings, or unclear intent

Text: "{text}"

Respond with ONLY the intent label, nothing else."""

    try:
        response = await model.generate_content_async(prompt)
        intent = response.text.strip().lower().replace('"', '').replace("'", "")
        valid_intents = ["expense_record", "invoice_create", "gst_query", "summary_request", "fallback"]
        if intent not in valid_intents:
            logger.warning(f"Unknown intent '{intent}', falling back")
            return "fallback"
        return intent
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return "fallback"


async def extract_expense(text: str) -> dict:
    """Extract structured expense data from natural language text (Hindi/English)."""
    today = date.today().isoformat()
    model = _get_model()
    prompt = f"""You are an expense extraction AI for Indian SMEs. Extract expense details from the following text.
The text may be in Hindi, English, or Hinglish.

Text: "{text}"

Return ONLY a valid JSON object with these fields:
{{
    "date": "YYYY-MM-DD (use {today} if not mentioned)",
    "description": "what was purchased/paid for",
    "amount": 0.0,
    "category": "one of: fuel, raw_material, utility, salary, travel, food, misc",
    "vendor": "who was paid (or null if unknown)",
    "payment_method": "one of: cash, upi, bank, cheque (default cash)",
    "gst_applicable": false,
    "notes": "any extra details or null"
}}"""

    try:
        response = await model.generate_content_async(prompt)
        data = _parse_json_from_text(response.text)
        # Ensure required fields
        data.setdefault("date", today)
        data.setdefault("description", "Unknown expense")
        data.setdefault("amount", 0)
        data.setdefault("category", "misc")
        data.setdefault("payment_method", "cash")
        data.setdefault("gst_applicable", False)
        return data
    except Exception as e:
        logger.error(f"Expense extraction failed: {e}")
        raise ValueError(f"Could not extract expense data: {e}")


async def extract_invoice(text: str) -> dict:
    """Extract structured invoice data from natural language text."""
    today = date.today().isoformat()
    model = _get_model()
    prompt = f"""You are an invoice extraction AI for Indian SMEs. Extract invoice details from the following text.

Text: "{text}"

Return ONLY a valid JSON object with these fields:
{{
    "date": "YYYY-MM-DD (use {today} if not mentioned)",
    "customer_name": "customer/client name",
    "customer_phone": "phone number or null",
    "description": "what the invoice is for",
    "amount": 0.0,
    "gst_rate": 18.0,
    "due_date": "YYYY-MM-DD or null",
    "notes": "any extra details or null"
}}"""

    try:
        response = await model.generate_content_async(prompt)
        data = _parse_json_from_text(response.text)
        data.setdefault("date", today)
        data.setdefault("customer_name", "Unknown")
        data.setdefault("amount", 0)
        data.setdefault("gst_rate", 18.0)
        # Calculate GST
        amount = float(data.get("amount", 0))
        gst_rate = float(data.get("gst_rate", 18.0))
        data["gst_amount"] = round(amount * gst_rate / 100, 2)
        data["total_amount"] = round(amount + data["gst_amount"], 2)
        return data
    except Exception as e:
        logger.error(f"Invoice extraction failed: {e}")
        raise ValueError(f"Could not extract invoice data: {e}")


async def extract_from_receipt_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Use Gemini Vision to extract data from a receipt/bill image. Replaces EasyOCR + LLM pipeline."""
    model = _get_model()
    today = date.today().isoformat()

    image_part = {
        "mime_type": mime_type,
        "data": image_bytes,
    }

    prompt = f"""You are an OCR and data extraction AI for Indian SMEs.
Analyze this receipt/bill image and extract the following information.

Return ONLY a valid JSON object:
{{
    "date": "YYYY-MM-DD (use {today} if not readable)",
    "description": "what was purchased",
    "amount": 0.0,
    "vendor": "shop/vendor name",
    "category": "one of: fuel, raw_material, utility, salary, travel, food, misc",
    "gst_applicable": false,
    "gst_amount": 0.0,
    "payment_method": "cash, upi, bank, or cheque",
    "notes": "any other relevant details from the receipt"
}}"""

    try:
        response = await model.generate_content_async([prompt, image_part])
        data = _parse_json_from_text(response.text)
        data.setdefault("date", today)
        data.setdefault("description", "Receipt expense")
        data.setdefault("amount", 0)
        data.setdefault("category", "misc")
        return data
    except Exception as e:
        logger.error(f"Receipt extraction failed: {e}")
        raise ValueError(f"Could not extract receipt data: {e}")


async def answer_gst_query(question: str) -> str:
    """Answer GST-related questions for Indian SME owners."""
    model = _get_model()
    prompt = f"""You are a helpful GST (Goods and Services Tax) expert assistant for Indian SME owners.
Answer the following question concisely and accurately. Use simple language.
If you mention tax rates, specify which category they apply to.
Keep the answer under 200 words.

Question: {question}"""

    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"GST query failed: {e}")
        return "Sorry, I couldn't process your GST query right now. Please try again."


async def chat_response(text: str) -> str:
    """General chat response for greetings and fallback messages."""
    model = _get_model()
    prompt = f"""You are Vyapar AI, a friendly WhatsApp accounting assistant for Indian SME owners.
The user said: "{text}"

Respond naturally and briefly. If they seem to need help, mention that you can:
- Record expenses (voice, text, or photo of bills)
- Create invoices
- Answer GST questions
- Show expense/invoice summaries

Keep response under 50 words. Be warm and professional."""

    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Chat response failed: {e}")
        return "Hello! I'm Vyapar AI. I can help you record expenses, create invoices, and answer GST questions. How can I help?"
