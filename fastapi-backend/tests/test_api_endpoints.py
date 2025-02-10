from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch

client = TestClient(app)


@pytest.fixture
def sample_chat_content():
    return """First line should be ignored, it's an automatic WhatsApp line
18/01/2025 20:31 - Messages and calls are end-to-end encrypted
18/01/2025 20:31 - Alice: Hey there!
18/01/2025 20:32 - Bob: Hi Alice, how are you?"""


def test_analyze_endpoint_success(sample_chat_content):
    response = client.post("/analyze", json={"content": sample_chat_content})
    assert response.status_code == 200
    assert "conversation_stats" in response.json()
    assert "heatmap_data" in response.json()


def test_analyze_endpoint_empty_content():
    response = client.post("/analyze", json={"content": ""})
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_json():
    response = client.post("/analyze", json={"wrong_field": "some content"})
    assert response.status_code == 422


def test_analyze_endpoint_malformed_chat():
    response = client.post("/analyze", json={"content": "This is not a WhatsApp chat format"})
    assert response.status_code == 500
    assert "Error analyzing conversation" in response.json()["detail"]


def test_conversation_themes_endpoint():
    with patch("app.services.chatgpt_utils.extract_themes") as mock_extract:
        mock_extract.return_value = {"Theme 1": "Example 1"}

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-3.5-turbo"}
        )
        assert response.status_code == 404  # Since we don't have the conversation in DB


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI Text Analyzer"}


def test_cors_headers():
    response = client.options(
        "/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] in [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
