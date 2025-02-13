from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, ANY, MagicMock
from typing import List
from pydantic import BaseModel
from app.models.data_formats import Message
import psycopg2

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
    # Test database connection error
    with patch("app.database.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_db.execute.side_effect = psycopg2.OperationalError(
            "SSL error: decryption failed or bad record mac"
        )
        mock_session.return_value = mock_db

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-4o"}
        )

        assert response.status_code == 503
        assert "Database service unavailable" in response.json()["detail"]

    # Test conversation not found
    with patch("app.database.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_db.execute.return_value = True
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session.return_value = mock_db

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-4o"}
        )

        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]

    # Test empty themes from OpenAI
    with patch("app.database.SessionLocal") as mock_session, patch(
        "app.api.routes.extract_themes"
    ) as mock_extract:
        mock_db = MagicMock()
        mock_db.execute.return_value = True
        mock_conv = MagicMock()
        mock_conv.conversation = "[]"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conv
        mock_session.return_value = mock_db
        mock_extract.return_value = {}  # Empty themes from OpenAI

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-4o"}
        )

        assert response.status_code == 422
        assert "No themes extracted from LLM" in response.json()["detail"]

    # Test theme parsing error
    with patch("app.database.SessionLocal") as mock_session, patch(
        "app.api.routes.extract_themes"
    ) as mock_extract, patch("app.api.routes.parse_themes_response") as mock_parse:
        mock_db = MagicMock()
        mock_db.execute.return_value = True
        mock_conv = MagicMock()
        mock_conv.conversation = "[]"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conv
        mock_session.return_value = mock_db
        mock_extract.return_value = {"some": "themes"}  # Return some themes
        mock_parse.return_value = {}  # But parsing fails

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-4o"}
        )

        assert response.status_code == 422
        assert "Unable to parse extracted themes" in response.json()["detail"]

    # Test successful case
    with patch("app.database.SessionLocal") as mock_session, patch(
        "app.api.routes.extract_themes"
    ) as mock_extract, patch("app.api.routes.parse_themes_response") as mock_parse:
        mock_db = MagicMock()
        mock_db.execute.return_value = True
        mock_conv = MagicMock()
        mock_conv.conversation = "[]"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conv
        mock_session.return_value = mock_db

        themes = {"Theme 1": "Example 1"}
        mock_extract.return_value = themes
        mock_parse.return_value = themes

        response = client.post(
            "/conversation-themes", json={"conversation_id": "test_hash", "model": "gpt-4o"}
        )

        assert response.status_code == 200
        assert "themes" in response.json()
        assert response.json()["themes"] == {"Theme 1": "Example 1"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    # Check that the response is HTML (usually "text/html" in Content-Type)
    content_type = response.headers.get("content-type")
    assert content_type is not None and "text/html" in content_type.lower()
    # For example, ensure that the index.html contains a <div id="root">
    assert '<div id="root">' in response.text


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


class SimulationRequest(BaseModel):
    conversation: List[dict]
    author: str
    prompt: str
    language: str
    model: str


@pytest.fixture
def sample_simulation_data():
    return {
        "conversation": [
            {"date": "2025-01-18T20:31:00", "author": "Alice", "content": "Hey there!"},
            {"date": "2025-01-18T20:32:00", "author": "Bob", "content": "Hi Alice, how are you?"},
        ],
        "author": "Alice",
        "prompt": "Respond to Bob's question",
        "language": "en",
        "model": "gpt-4o",
    }


def test_simulate_message_endpoint_success(sample_simulation_data):
    with patch("app.api.routes.simulate_author_message") as mock_simulate:
        mock_simulate.return_value = "I'm doing well, thanks for asking!"

        response = client.post("/simulate-message", json=sample_simulation_data)

        assert response.status_code == 200
        assert "simulated_message" in response.json()
        mock_simulate.assert_called_once_with(
            [Message.model_validate(msg) for msg in sample_simulation_data["conversation"]],
            sample_simulation_data["author"],
            sample_simulation_data["prompt"],
            sample_simulation_data["language"],
            model=sample_simulation_data["model"],
        )


def test_simulate_message_endpoint_invalid_data():
    invalid_data = {
        "conversation": [],
        "author": "",  # Invalid empty author
        "prompt": "Test prompt",
        "language": "pt",
        "model": "gpt-4o",
    }

    response = client.post("/simulate-message", json=invalid_data)
    assert response.status_code == 422
    assert "author" in response.text  # Check validation error mentions author field


def test_simulate_message_model_selection(sample_simulation_data):
    with patch("app.api.routes.simulate_author_message") as mock_simulate:
        mock_simulate.return_value = "Simulated string response message."

        sample_simulation_data["model"] = "gpt-4o-mini"
        client.post("/simulate-message", json=sample_simulation_data)

        mock_simulate.assert_called_once_with(ANY, ANY, ANY, ANY, model="gpt-4o-mini")


def test_create_suggestion_success():
    suggestion_payload = {
        "suggestion": "I think we should improve the UI.",
        "conversation_id": "conversation123",
        "timestamp": "2023-10-21T15:00:00Z",
    }
    response = client.post("/suggestions", json=suggestion_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "status" in json_data
    assert json_data["status"] == "success"


def test_create_suggestion_invalid_payload():
    # Sending an invalid payload (missing required fields: "suggestion" and "timestamp")
    invalid_payload = {"conversation_id": "conversation123"}
    response = client.post("/suggestions", json=invalid_payload)
    assert response.status_code == 422  # Expecting a validation error
