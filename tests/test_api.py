import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert response.json()["service"] == "Healthcare Intake Agent"

def test_message_endpoint():
    """Test message processing"""
    response = client.post(
        "/api/v1/message",
        json={"message": "I have a headache"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert isinstance(response.json()["response"], str)

def test_message_emergency():
    """Test emergency detection"""
    response = client.post(
        "/api/v1/message",
        json={"message": "I'm having chest pain and difficulty breathing"}
    )
    assert response.status_code == 200
    assert response.json()["emergency"] == True
    assert "URGENT" in response.json()["response"]

def test_summary_endpoint():
    """Test summary endpoint"""
    # First send a message
    client.post("/api/v1/message", json={"message": "I have a headache"})
    
    # Then get summary
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    assert "patient_data" in response.json()

def test_reset_endpoint():
    """Test reset endpoint"""
    response = client.post("/api/v1/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_status_endpoint():
    """Test status endpoint"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "status" in response.json()