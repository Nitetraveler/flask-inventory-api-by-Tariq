from inventory.extensions import db


def test_liveness(client):
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_readiness(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.get_json() == {"database": "ok", "status": "ready"}


def test_readiness_reports_db_failure(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("database is down")

    monkeypatch.setattr(db.session, "execute", boom)
    resp = client.get("/health/ready")
    assert resp.status_code == 503
    assert resp.get_json()["status"] == "unavailable"
