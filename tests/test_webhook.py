"""
Webhook endpoint tests — text processing and image upload with mocked Gemini API.
Tests the full pipeline: text → intent → extraction → database save.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# Mock the Gemini model responses
def _mock_classify(intent):
    """Create a mock for classify_intent that returns the specified intent."""
    async def mock_fn(text):
        return intent
    return mock_fn


def _mock_extract_expense():
    async def mock_fn(text):
        return {
            "date": "2026-04-05",
            "description": "Petrol",
            "amount": 2200.0,
            "category": "fuel",
            "vendor": "HP Pump",
            "payment_method": "upi",
            "gst_applicable": True,
            "gst_amount": 396.0,
        }
    return mock_fn


def _mock_extract_invoice():
    async def mock_fn(text):
        return {
            "date": "2026-04-05",
            "customer_name": "Rahul Sharma",
            "customer_phone": "+919876543210",
            "description": "Website Design",
            "amount": 25000.0,
            "gst_rate": 18.0,
            "gst_amount": 4500.0,
            "total_amount": 29500.0,
        }
    return mock_fn


def _mock_gst_answer():
    async def mock_fn(q):
        return "GST rate for electronics is 18%."
    return mock_fn


def _mock_chat():
    async def mock_fn(t):
        return "Hello! I'm Vyapar AI."
    return mock_fn


class TestTextWebhook:
    @patch("backend.routers.webhook.llm_service")
    def test_expense_recording_via_text(self, mock_llm, client, auth_headers):
        mock_llm.classify_intent = AsyncMock(return_value="expense_record")
        mock_llm.extract_expense = AsyncMock(return_value={
            "date": "2026-04-05", "description": "Petrol", "amount": 2200.0,
            "category": "fuel", "vendor": "HP Pump", "payment_method": "upi",
            "gst_applicable": True, "gst_amount": 396.0,
        })

        response = client.post("/api/webhook/text", json={
            "text": "Paid 2200 for petrol at HP pump via UPI"
        }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "2,200" in data["message"] or "2200" in data["message"]
        assert data["data"]["expense_id"] > 0

        # Verify it was actually saved in the database
        expenses = client.get("/api/expenses/", headers=auth_headers)
        assert len(expenses.json()) >= 1
        saved = [e for e in expenses.json() if e["description"] == "Petrol"]
        assert len(saved) == 1
        assert saved[0]["amount"] == 2200.0
        assert saved[0]["source"] == "text"

    @patch("backend.routers.webhook.llm_service")
    def test_invoice_creation_via_text(self, mock_llm, client, auth_headers):
        mock_llm.classify_intent = AsyncMock(return_value="invoice_create")
        mock_llm.extract_invoice = AsyncMock(return_value={
            "date": "2026-04-05", "customer_name": "Rahul Sharma",
            "amount": 25000.0, "gst_rate": 18.0, "gst_amount": 4500.0,
            "total_amount": 29500.0, "description": "Website Design",
        })

        response = client.post("/api/webhook/text", json={
            "text": "Create invoice for Rahul Sharma, 25000 for website design"
        }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["invoice_number"].startswith("VYP-")

    @patch("backend.routers.webhook.llm_service")
    def test_gst_query(self, mock_llm, client, auth_headers):
        mock_llm.classify_intent = AsyncMock(return_value="gst_query")
        mock_llm.answer_gst_query = AsyncMock(return_value="GST for electronics is 18%.")

        response = client.post("/api/webhook/text", json={
            "text": "What is GST rate for electronics?"
        }, headers=auth_headers)

        assert response.status_code == 200
        assert "18%" in response.json()["message"]

    @patch("backend.routers.webhook.llm_service")
    def test_fallback_response(self, mock_llm, client, auth_headers):
        mock_llm.classify_intent = AsyncMock(return_value="fallback")
        mock_llm.chat_response = AsyncMock(return_value="Hello! I'm Vyapar AI.")

        response = client.post("/api/webhook/text", json={
            "text": "Hello how are you"
        }, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_webhook_requires_auth(self, client):
        response = client.post("/api/webhook/text", json={"text": "test"})
        assert response.status_code == 401


class TestImageWebhook:
    @patch("backend.routers.webhook.llm_service")
    def test_image_upload_and_ocr(self, mock_llm, client, auth_headers):
        mock_llm.extract_from_receipt_image = AsyncMock(return_value={
            "date": "2026-04-05", "description": "Restaurant bill",
            "amount": 1500.0, "vendor": "Sharma's Dosa",
            "category": "food", "gst_applicable": True, "gst_amount": 270.0,
        })

        # Create a fake image file
        import io
        fake_image = io.BytesIO(b"\x89PNG\r\n" + b"\x00" * 100)
        fake_image.name = "receipt.png"

        response = client.post(
            "/api/webhook/image",
            files={"image": ("receipt.png", fake_image, "image/png")},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["needs_confirmation"] is True
        assert data["data"]["extracted"]["vendor"] == "Sharma's Dosa"

    def test_image_webhook_requires_auth(self, client):
        import io
        fake = io.BytesIO(b"\x00" * 10)
        response = client.post("/api/webhook/image", files={"image": ("x.png", fake, "image/png")})
        assert response.status_code == 401
