def test_product_create_list_update_delete(client, auth_headers):
    payload = {
        "sku": "WIDGET-1",
        "name": "Widget",
        "description": "A useful widget",
        "price": "2.50",
        "quantity": 4,
    }
    created = client.post("/products", json=payload, headers=auth_headers)
    assert created.status_code == 201
    product_id = created.json()["id"]

    assert client.get("/products").json()[0]["sku"] == "WIDGET-1"
    updated = client.patch(
        f"/products/{product_id}",
        json={"price": "3.00"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == "3.00"

    deleted = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404


def test_duplicate_sku_is_rejected(client, auth_headers):
    payload = {"sku": "DUP", "name": "Widget", "price": "1.00"}
    assert client.post("/products", json=payload, headers=auth_headers).status_code == 201
    assert client.post("/products", json=payload, headers=auth_headers).status_code == 409


def test_patch_rejects_null_for_required_product_fields(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "NULL-1", "name": "Widget", "price": "1.00"},
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/products/{product['id']}",
        json={"name": None},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_product_create_rejects_whitespace_only_name(client, auth_headers):
    response = client.post(
        "/products",
        json={"sku": "SPACE-1", "name": "   ", "price": "1.00"},
        headers=auth_headers,
    )

    assert response.status_code == 422
