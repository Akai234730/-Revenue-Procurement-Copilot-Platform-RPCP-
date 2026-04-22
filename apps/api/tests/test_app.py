from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_health_metrics() -> None:
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "ai_task_count" in payload
    assert "audit_log_count" in payload
