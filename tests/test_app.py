import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Debate Team" in data
    assert "participants" in data["Debate Team"]


def test_signup_success():
    # Test successful signup
    response = client.post("/activities/Debate%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Debate Team"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=newtest@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Math%20Club/signup?email=duplicate@mergington.edu")

    # Try to signup again for different activity
    response = client.post("/activities/Debate%20Team/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Art%20Class/signup?email=remove@mergington.edu")

    # Then unregister
    response = client.delete("/activities/Art%20Class/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "remove@mergington.edu" not in data["Art Class"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Debate%20Team/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]