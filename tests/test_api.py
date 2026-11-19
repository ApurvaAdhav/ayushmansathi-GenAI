from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Test 1: Health check
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test 2: Ask endpoint with a fake LLM
@patch("app.main.rag_ask_question")
def test_ask_endpoint(mock_ask):
    mock_ask.return_value = {
        "answer": "Dental treatment is covered under the scheme.",
        "citations": [],
        "confidence": 0.95
    }

    response = client.post(
        "/ask",
        json={"question": "Is dental treatment covered?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Dental treatment is covered under the scheme."
    )
    mock_ask.assert_called_once()
