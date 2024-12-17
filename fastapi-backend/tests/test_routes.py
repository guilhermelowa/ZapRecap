from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI backend!"}

def test_analyze_text():
    response = client.post("/analyze", json={"text": "Sample text for analysis."})
    assert response.status_code == 200
    assert "analysis_result" in response.json()