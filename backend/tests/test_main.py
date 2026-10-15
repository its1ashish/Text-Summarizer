
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def fake_generate_summary(text, model, summary_length):
    return f"Mock summary from {model} ({summary_length})"


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_successful_summarization(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_summary",
        fake_generate_summary,
    )

    response = client.post(
        "/api/summarize",
        json={
            "text": "Artificial intelligence helps people analyze data.",
            "model": "t5",
            "summary_length": "short",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["summary"] == "Mock summary from t5 (short)"
    assert data["model"] == "t5"
    assert data["original_words"] == 6
    assert data["summary_words"] == 5
    assert data["processing_time_seconds"] >= 0


def test_all_supported_models(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_summary",
        fake_generate_summary,
    )

    for model in ["textrank", "t5", "bart"]:
        response = client.post(
            "/api/summarize",
            json={
                "text": "This is a sample article for testing.",
                "model": model,
                "summary_length": "medium",
            },
        )

        assert response.status_code == 200
        assert response.json()["model"] == model


def test_invalid_model():
    response = client.post(
        "/api/summarize",
        json={
            "text": "Some sample text.",
            "model": "unknown",
            "summary_length": "short",
        },
    )

    assert response.status_code == 400


def test_invalid_summary_length():
    response = client.post(
        "/api/summarize",
        json={
            "text": "Some sample text.",
            "model": "t5",
            "summary_length": "extra-large",
        },
    )

    assert response.status_code == 400


def test_empty_text():
    response = client.post(
        "/api/summarize",
        json={
            "text": "   ",
            "model": "textrank",
            "summary_length": "short",
        },
    )

    assert response.status_code == 400
