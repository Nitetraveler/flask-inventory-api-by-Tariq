import pytest

from inventory import create_app
from inventory.extensions import db as _db


@pytest.fixture()
def app():
    """A fresh app with an empty in-memory database for every test."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_item(client):
    """Create an item through the API using the test API key."""
    def _make(sku="TST-001", name="Test item", quantity=10):
        resp = client.post(
            "/api/v1/items",
            json={"sku": sku, "name": name, "quantity": quantity},
            headers={"X-API-Key": "test-api-key"},
        )
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()

    return _make
