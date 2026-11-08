import pytest

URL = "/api/v1/items"
API_HEADERS = {"X-API-Key": "test-api-key"}


def test_list_starts_empty(client):
    resp = client.get(URL)
    assert resp.status_code == 200
    assert resp.get_json() == {
        "count": 0,
        "items": [],
        "page": 1,
        "per_page": 20,
        "total": 0,
    }


def test_create_item_returns_201_and_location(client):
    resp = client.post(
        URL,
        json={"sku": "ABC-1", "name": "Alpha", "quantity": 5},
        headers=API_HEADERS,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["sku"] == "ABC-1" and body["quantity"] == 5
    assert resp.headers["Location"] == f"{URL}/{body['id']}"


def test_create_defaults_quantity_to_zero(client):
    resp = client.post(
        URL,
        json={"sku": "ZERO-1", "name": "Zero stock"},
        headers=API_HEADERS,
    )
    assert resp.status_code == 201
    assert resp.get_json()["quantity"] == 0


@pytest.mark.parametrize(
    "payload, fragment",
    [
        ({"name": "No sku"}, "sku must be"),
        ({"sku": "X-1"}, "name must be"),
        ({"sku": "X-1", "name": "Negative", "quantity": -1}, "quantity must be"),
        ({"sku": "X-1", "name": "Boolean", "quantity": True}, "quantity must be"),
        ({"sku": "X-1", "name": "Extra", "colour": "red"}, "unknown fields: colour"),
    ],
)
def test_create_rejects_invalid_payload(client, payload, fragment):
    resp = client.post(URL, json=payload, headers=API_HEADERS)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"] == "Bad Request"
    assert fragment in body["message"]


def test_create_rejects_non_json(client):
    resp = client.post(
        URL,
        data="sku=abc",
        content_type="application/x-www-form-urlencoded",
        headers=API_HEADERS,
    )
    assert resp.status_code == 400
    assert "JSON object" in resp.get_json()["message"]


def test_duplicate_sku_returns_409(client, make_item):
    make_item(sku="DUP-1")
    resp = client.post(
        URL,
        json={"sku": "DUP-1", "name": "Again"},
        headers=API_HEADERS,
    )
    assert resp.status_code == 409
    body = resp.get_json()
    assert body["error"] == "Conflict"
    assert "DUP-1" in body["message"]
    assert client.get(URL).get_json()["count"] == 1


def test_get_missing_item_returns_json_404(client):
    resp = client.get(f"{URL}/999")
    assert resp.status_code == 404
    assert resp.get_json() == {
        "error": "Not Found",
        "message": "Item 999 not found",
        "status": 404,
    }


def test_patch_updates_only_given_fields(client, make_item):
    item = make_item(quantity=10)
    resp = client.patch(
        f"{URL}/{item['id']}",
        json={"quantity": 42},
        headers=API_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["quantity"] == 42
    assert body["sku"] == item["sku"] and body["name"] == item["name"]


def test_patch_missing_item_returns_404(client):
    resp = client.patch(
        f"{URL}/999",
        json={"quantity": 1},
        headers=API_HEADERS,
    )
    assert resp.status_code == 404


def test_patch_rejects_invalid_quantity(client, make_item):
    item = make_item()
    resp = client.patch(
        f"{URL}/{item['id']}",
        json={"quantity": -5},
        headers=API_HEADERS,
    )
    assert resp.status_code == 400


def test_patch_rejects_empty_body(client, make_item):
    item = make_item()
    resp = client.patch(
        f"{URL}/{item['id']}",
        json={},
        headers=API_HEADERS,
    )
    assert resp.status_code == 400
    assert "at least one" in resp.get_json()["message"]


def test_delete_item(client, make_item):
    item = make_item()
    resp = client.delete(f"{URL}/{item['id']}", headers=API_HEADERS)
    assert resp.status_code == 204
    assert resp.data == b""
    assert client.get(f"{URL}/{item['id']}").status_code == 404


def test_filters(client, make_item):
    make_item(sku="A-1", name="Hex bolt", quantity=5)
    make_item(sku="A-2", name="Hex nut", quantity=50)
    make_item(sku="A-3", name="Washer", quantity=500)

    resp = client.get(f"{URL}?min_quantity=40")
    assert [i["sku"] for i in resp.get_json()["items"]] == ["A-2", "A-3"]
    assert client.get(f"{URL}?q=hex").get_json()["count"] == 2


def test_method_not_allowed_is_json(client):
    resp = client.delete(URL)
    assert resp.status_code == 405
    assert resp.is_json
    assert "POST" in resp.headers["Allow"]


def test_write_routes_reject_missing_and_wrong_api_keys(client, make_item):
    item = make_item(sku="AUTH-1")

    requests = [
        client.post(URL, json={"sku": "AUTH-2", "name": "No key"}),
        client.post(
            URL,
            json={"sku": "AUTH-3", "name": "Wrong key"},
            headers={"X-API-Key": "wrong-key"},
        ),
        client.patch(f"{URL}/{item['id']}", json={"quantity": 20}),
        client.patch(
            f"{URL}/{item['id']}",
            json={"quantity": 20},
            headers={"X-API-Key": "wrong-key"},
        ),
        client.delete(f"{URL}/{item['id']}"),
        client.delete(
            f"{URL}/{item['id']}",
            headers={"X-API-Key": "wrong-key"},
        ),
    ]

    for resp in requests:
        assert resp.status_code == 401
        assert resp.is_json
        assert resp.get_json()["error"] == "Unauthorized"


def test_get_and_health_routes_remain_public(client, make_item):
    item = make_item(sku="PUBLIC-1")

    assert client.get(URL).status_code == 200
    assert client.get(f"{URL}/{item['id']}").status_code == 200
    assert client.get("/health/live").status_code == 200


def test_pagination_defaults_and_second_page(client, make_item):
    for number in range(25):
        make_item(sku=f"PAG-{number:03d}")

    first = client.get(URL).get_json()
    assert first["count"] == 25
    assert first["total"] == 25
    assert first["page"] == 1
    assert first["per_page"] == 20
    assert len(first["items"]) == 20

    second = client.get(f"{URL}?page=2").get_json()
    assert second["count"] == 25
    assert second["total"] == 25
    assert second["page"] == 2
    assert second["per_page"] == 20
    assert len(second["items"]) == 5


def test_pagination_beyond_last_page_returns_empty_items(client, make_item):
    make_item()
    body = client.get(f"{URL}?page=2").get_json()

    assert body["items"] == []
    assert body["count"] == 1
    assert body["total"] == 1
    assert body["page"] == 2


def test_pagination_maximum_page_size_is_accepted(client, make_item):
    for number in range(25):
        make_item(sku=f"MAX-{number:03d}")

    body = client.get(f"{URL}?per_page=100").get_json()
    assert body["per_page"] == 100
    assert len(body["items"]) == 25


@pytest.mark.parametrize("parameter", ["page", "per_page"])
@pytest.mark.parametrize("value", ["abc", "0", "-1", "1.5"])
def test_pagination_rejects_invalid_parameters(client, parameter, value):
    resp = client.get(f"{URL}?{parameter}={value}")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Bad Request"


def test_pagination_rejects_page_size_above_100(client):
    resp = client.get(f"{URL}?per_page=101")
    assert resp.status_code == 400
    assert "100" in resp.get_json()["message"]
