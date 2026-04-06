"""
Invoice CRUD tests — creation with auto-number, status management, summaries, data isolation.
"""
import pytest


class TestInvoiceCreation:
    def test_create_invoice(self, client, auth_headers):
        response = client.post("/api/invoices/", json={
            "date": "2026-04-01",
            "customer_name": "Sharma Enterprises",
            "customer_phone": "+919876543210",
            "description": "Web development",
            "amount": 50000,
            "gst_rate": 18.0,
            "gst_amount": 9000,
            "total_amount": 59000,
            "status": "draft",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "Sharma Enterprises"
        assert data["total_amount"] == 59000
        assert data["invoice_number"] is not None
        assert data["invoice_number"].startswith("VYP-")

    def test_invoice_number_uniqueness(self, client, auth_headers):
        """Two invoices should have different invoice numbers."""
        r1 = client.post("/api/invoices/", json={
            "date": "2026-04-01", "customer_name": "A", "amount": 100, "total_amount": 118,
        }, headers=auth_headers)
        r2 = client.post("/api/invoices/", json={
            "date": "2026-04-01", "customer_name": "B", "amount": 200, "total_amount": 236,
        }, headers=auth_headers)
        assert r1.json()["invoice_number"] != r2.json()["invoice_number"]


class TestInvoiceStatusManagement:
    def _create_invoice(self, client, auth_headers):
        r = client.post("/api/invoices/", json={
            "date": "2026-04-01", "customer_name": "Test Customer",
            "amount": 10000, "total_amount": 11800,
        }, headers=auth_headers)
        return r.json()["id"]

    def test_mark_sent(self, client, auth_headers):
        inv_id = self._create_invoice(client, auth_headers)
        response = client.post(f"/api/invoices/{inv_id}/mark-sent", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "sent"

    def test_mark_paid(self, client, auth_headers):
        inv_id = self._create_invoice(client, auth_headers)
        response = client.post(f"/api/invoices/{inv_id}/mark-paid", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paid"


class TestInvoiceDataIsolation:
    """CRITICAL: Users must never access each other's invoices."""

    def test_user_cannot_see_other_users_invoices(self, client, auth_headers, second_auth_headers):
        client.post("/api/invoices/", json={
            "date": "2026-04-01", "customer_name": "Secret Client",
            "amount": 100000, "total_amount": 118000,
        }, headers=auth_headers)

        response = client.get("/api/invoices/", headers=second_auth_headers)
        assert len(response.json()) == 0, "DATA LEAKAGE: User 2 sees User 1's invoices!"

    def test_user_cannot_mark_other_users_invoice_paid(self, client, auth_headers, second_auth_headers):
        r = client.post("/api/invoices/", json={
            "date": "2026-04-01", "customer_name": "Protected",
            "amount": 5000, "total_amount": 5900,
        }, headers=auth_headers)
        inv_id = r.json()["id"]

        response = client.post(f"/api/invoices/{inv_id}/mark-paid", headers=second_auth_headers)
        assert response.status_code == 404, "DATA LEAKAGE: User 2 can modify User 1's invoice!"


class TestInvoiceSummaries:
    def _seed(self, client, auth_headers):
        invoices = [
            {"date": "2026-04-01", "customer_name": "A", "amount": 10000, "total_amount": 11800, "status": "paid"},
            {"date": "2026-04-15", "customer_name": "B", "amount": 20000, "total_amount": 23600, "status": "sent"},
            {"date": "2026-04-20", "customer_name": "C", "amount": 5000, "total_amount": 5900, "status": "draft"},
        ]
        for inv in invoices:
            client.post("/api/invoices/", json=inv, headers=auth_headers)

    def test_monthly_invoice_summary(self, client, auth_headers):
        self._seed(client, auth_headers)
        response = client.get("/api/invoices/summary/monthly?year=2026&month=4", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_count"] == 3
        assert data["total_amount"] == 41300.0

    def test_summary_isolation(self, client, auth_headers, second_auth_headers):
        self._seed(client, auth_headers)
        response = client.get("/api/invoices/summary/monthly?year=2026&month=4", headers=second_auth_headers)
        data = response.json()
        assert data["invoice_count"] == 0, "DATA LEAKAGE in invoice summaries!"
