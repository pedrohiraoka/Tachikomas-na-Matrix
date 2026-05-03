"""Test API endpoints."""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_register_experience():
    """Test experience registration."""
    response = client.post(
        "/api/v1/tachikomas/test-001/experience",
        json={"content": "Test experience", "shareable": True}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_state_not_found():
    """Test getting state for non-existent unit."""
    response = client.get("/api/v1/tachikomas/nonexistent/state")
    assert response.status_code == 404
