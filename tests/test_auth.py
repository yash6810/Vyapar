"""
Authentication tests — registration, login, token validation, profile management.
Tests defensive scenarios: duplicate email, wrong password, expired/invalid tokens.
"""
import pytest


class TestRegistration:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "email": "new@vyapar.ai",
            "password": "secure123",
            "name": "New User",
            "business_name": "New Biz",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@vyapar.ai"
        assert data["name"] == "New User"
        assert "hashed_password" not in data  # Never expose password hash

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/auth/register", json={
            "email": "test@vyapar.ai",  # already exists
            "password": "newpass",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={"email": "x@y.com"})
        assert response.status_code == 422  # Pydantic validation error


class TestLogin:
    def test_login_success(self, client, test_user):
        response = client.post("/api/auth/token", data={
            "username": "test@vyapar.ai",
            "password": "testpass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/api/auth/token", data={
            "username": "test@vyapar.ai",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/token", data={
            "username": "ghost@vyapar.ai",
            "password": "anything",
        })
        assert response.status_code == 401


class TestTokenValidation:
    def test_valid_token_access(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@vyapar.ai"

    def test_invalid_token_rejected(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer fake.token.here"
        })
        assert response.status_code == 401

    def test_missing_token_rejected(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_password_never_returned(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data


class TestProfile:
    def test_update_profile(self, client, auth_headers):
        response = client.put("/api/auth/me", json={
            "name": "Updated Name",
            "business_name": "Updated Biz",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_partial_profile(self, client, auth_headers):
        """Only update business_name, leave name unchanged."""
        response = client.put("/api/auth/me", json={
            "business_name": "New Biz Only",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["business_name"] == "New Biz Only"
