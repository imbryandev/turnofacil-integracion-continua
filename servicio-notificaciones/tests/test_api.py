from fastapi.testclient import TestClient
import app.main as notifications


def test_accept_and_list_notification(monkeypatch, tmp_path):
    monkeypatch.setattr(notifications, "DATABASE_PATH", str(tmp_path / "test.db"))
    notifications.init_db()
    with TestClient(notifications.app) as client:
        response = client.post("/internal/notifications", json={
            "reservation_id": 7, "email": "ana@example.com", "message": "Reserva confirmada",
        })
        assert response.status_code == 202
        assert response.json()["status"] == "accepted"
        items = client.get("/notifications").json()
        assert len(items) == 1
        assert items[0]["reservation_id"] == 7


def test_health():
    with TestClient(notifications.app) as client:
        assert client.get("/health").json()["status"] == "ok"
