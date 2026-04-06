"""
Expense CRUD tests — creation, retrieval, filtering, summaries, updates, deletion.
Critical: tests cross-user data isolation to ensure no data leakage between users.
"""
import pytest
from datetime import date, timedelta


class TestExpenseCreation:
    def test_create_expense(self, client, auth_headers):
        response = client.post("/api/expenses/", json={
            "date": "2026-04-01",
            "description": "Office Supplies",
            "amount": 1500.0,
            "category": "misc",
            "vendor": "Gupta Stationery",
            "payment_method": "upi",
            "source": "manual",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Office Supplies"
        assert data["amount"] == 1500.0
        assert data["vendor"] == "Gupta Stationery"
        assert data["category"] == "misc"
        assert data["id"] > 0

    def test_create_expense_minimal(self, client, auth_headers):
        """Only required fields — defaults should fill in."""
        response = client.post("/api/expenses/", json={
            "date": "2026-04-01",
            "description": "Tea",
            "amount": 20.0,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["category"] == "misc"
        assert data["payment_method"] == "cash"
        assert data["currency"] == "INR"

    def test_create_expense_zero_amount_rejected(self, client, auth_headers):
        response = client.post("/api/expenses/", json={
            "date": "2026-04-01",
            "description": "Bad expense",
            "amount": 0,
        }, headers=auth_headers)
        assert response.status_code == 422  # Validation: amount > 0

    def test_create_expense_negative_amount_rejected(self, client, auth_headers):
        response = client.post("/api/expenses/", json={
            "date": "2026-04-01",
            "description": "Negative",
            "amount": -100,
        }, headers=auth_headers)
        assert response.status_code == 422


class TestExpenseRetrieval:
    def _create_expenses(self, client, auth_headers):
        """Helper: create multiple expenses for testing."""
        expenses = [
            {"date": "2026-04-01", "description": "Fuel", "amount": 2000, "category": "fuel", "vendor": "Indian Oil"},
            {"date": "2026-04-02", "description": "Lunch", "amount": 500, "category": "food", "vendor": "Zomato"},
            {"date": "2026-03-15", "description": "Salary", "amount": 25000, "category": "salary", "vendor": "Ramesh"},
            {"date": "2026-04-03", "description": "Electricity", "amount": 3000, "category": "utility", "vendor": "BSES"},
        ]
        for exp in expenses:
            r = client.post("/api/expenses/", json=exp, headers=auth_headers)
            assert r.status_code == 201

    def test_list_all_expenses(self, client, auth_headers):
        self._create_expenses(client, auth_headers)
        response = client.get("/api/expenses/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 4

    def test_filter_by_date_range(self, client, auth_headers):
        self._create_expenses(client, auth_headers)
        response = client.get(
            "/api/expenses/?start_date=2026-04-01&end_date=2026-04-02",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # All returned expenses should be in range
        for exp in data:
            assert "2026-04-01" <= exp["date"] <= "2026-04-02"

    def test_filter_by_category(self, client, auth_headers):
        self._create_expenses(client, auth_headers)
        response = client.get("/api/expenses/?category=fuel", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(e["category"] == "fuel" for e in data)

    def test_filter_by_vendor(self, client, auth_headers):
        self._create_expenses(client, auth_headers)
        response = client.get("/api/expenses/?vendor=Zomato", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_expenses(self, client, auth_headers):
        self._create_expenses(client, auth_headers)
        response = client.get("/api/expenses/?search=Electricity", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestExpenseDataIsolation:
    """CRITICAL: Ensure users can NEVER see each other's data."""

    def test_user_cannot_see_other_users_expenses(self, client, auth_headers, second_auth_headers):
        # User 1 creates an expense
        client.post("/api/expenses/", json={
            "date": "2026-04-01", "description": "Secret Expense", "amount": 9999,
        }, headers=auth_headers)

        # User 2 should see ZERO expenses
        response = client.get("/api/expenses/", headers=second_auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 0, "DATA LEAKAGE: User 2 can see User 1's expenses!"

    def test_user_cannot_delete_other_users_expense(self, client, auth_headers, second_auth_headers):
        # User 1 creates
        r = client.post("/api/expenses/", json={
            "date": "2026-04-01", "description": "Protected", "amount": 1000,
        }, headers=auth_headers)
        expense_id = r.json()["id"]

        # User 2 tries to delete — should fail
        response = client.delete(f"/api/expenses/{expense_id}", headers=second_auth_headers)
        assert response.status_code == 404, "DATA LEAKAGE: User 2 can delete User 1's expense!"

    def test_user_cannot_update_other_users_expense(self, client, auth_headers, second_auth_headers):
        r = client.post("/api/expenses/", json={
            "date": "2026-04-01", "description": "Untouchable", "amount": 500,
        }, headers=auth_headers)
        expense_id = r.json()["id"]

        response = client.put(f"/api/expenses/{expense_id}", json={
            "amount": 1,
        }, headers=second_auth_headers)
        assert response.status_code == 404, "DATA LEAKAGE: User 2 can modify User 1's expense!"


class TestExpenseSummaries:
    def _seed_expenses(self, client, auth_headers):
        expenses = [
            {"date": "2026-04-01", "description": "Fuel", "amount": 2000, "category": "fuel", "vendor": "HP", "gst_applicable": True, "gst_amount": 360},
            {"date": "2026-04-02", "description": "Lunch", "amount": 500, "category": "food", "vendor": "Zomato"},
            {"date": "2026-04-03", "description": "More Fuel", "amount": 1500, "category": "fuel", "vendor": "HP"},
        ]
        for exp in expenses:
            client.post("/api/expenses/", json=exp, headers=auth_headers)

    def test_monthly_summary(self, client, auth_headers):
        self._seed_expenses(client, auth_headers)
        response = client.get("/api/expenses/summary/monthly?year=2026&month=4", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["expense_count"] == 3
        assert data["total_amount"] == 4000.0
        assert "fuel" in data["by_category"]
        assert data["by_category"]["fuel"] == 3500.0

    def test_daily_summary(self, client, auth_headers):
        self._seed_expenses(client, auth_headers)
        response = client.get("/api/expenses/summary/daily?target_date=2026-04-01", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["expense_count"] == 1
        assert data["total_amount"] == 2000.0

    def test_yearly_summary(self, client, auth_headers):
        self._seed_expenses(client, auth_headers)
        response = client.get("/api/expenses/summary/yearly?year=2026", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["expense_count"] == 3

    def test_summary_isolation(self, client, auth_headers, second_auth_headers):
        """User 2's summary should NOT include User 1's expenses."""
        self._seed_expenses(client, auth_headers)
        response = client.get("/api/expenses/summary/monthly?year=2026&month=4", headers=second_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["expense_count"] == 0, "DATA LEAKAGE in summaries!"
        assert data["total_amount"] == 0.0


class TestExpenseUpdateDelete:
    def test_update_expense(self, client, auth_headers):
        r = client.post("/api/expenses/", json={
            "date": "2026-04-01", "description": "Old", "amount": 100,
        }, headers=auth_headers)
        expense_id = r.json()["id"]

        response = client.put(f"/api/expenses/{expense_id}", json={
            "description": "Updated",
            "amount": 200,
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["description"] == "Updated"
        assert response.json()["amount"] == 200

    def test_delete_expense(self, client, auth_headers):
        r = client.post("/api/expenses/", json={
            "date": "2026-04-01", "description": "To Delete", "amount": 50,
        }, headers=auth_headers)
        expense_id = r.json()["id"]

        response = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify it's gone
        response = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_expense(self, client, auth_headers):
        response = client.delete("/api/expenses/99999", headers=auth_headers)
        assert response.status_code == 404
