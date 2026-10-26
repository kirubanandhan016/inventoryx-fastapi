def test_order_places_deducts_stock_and_cancellation_restores_it(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "ORDER-1", "name": "Order item", "price": "3.50", "quantity": 8},
        headers=auth_headers,
    ).json()

    created = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=auth_headers,
    )
    assert created.status_code == 201
    assert created.json()["total"] == "7.00"
    assert client.get(f"/products/{product['id']}").json()["quantity"] == 6

    order_id = created.json()["id"]
    cancelled = client.post(f"/orders/{order_id}/cancel", headers=auth_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert client.get(f"/products/{product['id']}").json()["quantity"] == 8
    assert client.post(f"/orders/{order_id}/cancel", headers=auth_headers).status_code == 409


def test_order_rejects_insufficient_stock_without_creating_order(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "ORDER-2", "name": "Order item", "price": "3.50", "quantity": 1},
        headers=auth_headers,
    ).json()

    response = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 2}]},
        headers=auth_headers,
    )
    assert response.status_code == 409
    assert client.get("/orders", headers=auth_headers).json() == []
