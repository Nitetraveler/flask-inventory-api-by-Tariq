import pytest

from inventory import create_app
from inventory.config import ProductionConfig


def test_info_reports_environment(client):
    body = client.get("/api/v1/info").get_json()
    assert body["app"] == "inventory"
    assert body["env"] == "testing"
    assert "hostname" in body and "pid" in body


def test_unknown_environment_is_rejected():
    with pytest.raises(ValueError):
        create_app("staging")


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "dev-insecure-key")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_request_id_is_echoed_when_valid(client):
    resp = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert resp.headers["X-Request-ID"] == "abc-123"


def test_request_id_is_replaced_when_invalid(client):
    resp = client.get("/health/live", headers={"X-Request-ID": "bad id!"})
    rid = resp.headers["X-Request-ID"]
    assert rid != "bad id!"
    assert len(rid) == 32


def test_unhandled_exception_returns_json_500(app, client):
    def broken():
        raise ZeroDivisionError("secret internal detail")

    app.add_url_rule("/broken", "broken", broken)
    resp = client.get("/broken")
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "Internal Server Error"
    assert "secret internal detail" not in resp.get_data(as_text=True)


def test_cli_init_and_seed(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["init-db", "--drop"])
    assert result.exit_code == 0
    assert "Initialised database" in result.output
    assert "Seeded 4 item(s)." in runner.invoke(args=["seed-db"]).output
    assert "Seeded 0 item(s)." in runner.invoke(args=["seed-db"]).output


def test_production_requires_api_key(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "valid-production-secret")
    monkeypatch.setattr(ProductionConfig, "API_KEY", None)

    with pytest.raises(RuntimeError, match="API_KEY"):
        create_app("production")
