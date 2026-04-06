"""
Test fixtures and configuration.
Uses an independent in-memory SQLite database per test session — 
complete isolation from production data (zero leakage risk).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.auth import get_password_hash
from backend import models

# ── Isolated test database (in-memory, destroyed after tests) ─────────────────

TEST_DATABASE_URL = "sqlite:///./test_vyapar.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once for the test session, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    import os
    try:
        if os.path.exists("test_vyapar.db"):
            os.remove("test_vyapar.db")
    except PermissionError:
        pass  # Windows file lock — cleaned up on next run


@pytest.fixture
def db():
    """Provide a clean database session per test with rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """FastAPI test client with overridden DB dependency."""
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user and return it."""
    user = models.User(
        email="test@vyapar.ai",
        hashed_password=get_password_hash("testpass123"),
        name="Test User",
        business_name="Test Business",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_user(db):
    """Create a second user for data isolation tests."""
    user = models.User(
        email="other@vyapar.ai",
        hashed_password=get_password_hash("otherpass123"),
        name="Other User",
        business_name="Other Business",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test_user."""
    response = client.post(
        "/api/auth/token",
        data={"username": "test@vyapar.ai", "password": "testpass123"},
    )
    assert response.status_code == 200, f"Auth failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client, second_user):
    """Get auth headers for second_user (for isolation tests)."""
    response = client.post(
        "/api/auth/token",
        data={"username": "other@vyapar.ai", "password": "otherpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
