from fastapi.testclient import TestClient
import app.main as agenda


def test_create_reservation_persists_and_notifies(monkeypatch, tmp_path):
    monkeypatch.setattr(agenda, "DATABASE_PATH", str(tmp_path / "test.db"))
    agenda.init_db()
    calls = []

    class Response:
        def raise_for_status(self):
            pass

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        return Response()

    monkeypatch.setattr(agenda.requests, "post", fake_post)
    with TestClient(agenda.app) as client:
        response = client.post("/reservations", json={
            "customer_name": "Ana Pérez", "email": "ana@example.com",
            "service": "Corte de cabello", "starts_at": "2026-12-10T15:00:00",
        })
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert client.get("/reservations").json()[0]["customer_name"] == "Ana Pérez"
    assert calls[0][0] == f"{agenda.NOTIFICATIONS_URL}/internal/notifications"


def test_missing_reservation_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr(agenda, "DATABASE_PATH", str(tmp_path / "test.db"))
    agenda.init_db()
    with TestClient(agenda.app) as client:
        assert client.get("/reservations/99").status_code == 404
