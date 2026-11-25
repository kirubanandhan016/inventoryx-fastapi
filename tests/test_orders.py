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


def test_duplicate_order_lines_are_aggregated_before_stock_deduction(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "ORDER-DUP", "name": "Duplicate line item", "price": "3.50", "quantity": 5},
        headers=auth_headers,
    ).json()

    response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product["id"], "quantity": 1},
                {"product_id": product["id"], "quantity": 2},
            ]
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total"] == "10.50"
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3
    assert client.get(f"/products/{product['id']}").json()["quantity"] == 2


def test_order_is_not_visible_to_a_different_account(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "ORDER-PRIVATE", "name": "Private order item", "price": "5.00", "quantity": 4},
        headers=auth_headers,
    ).json()
    created = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=auth_headers,
    )
    assert created.status_code == 201

    registration = client.post(
        "/auth/register",
        json={
            "email": "another-owner@example.com",
            "full_name": "Another Owner",
            "password": "another-strong-password",
        },
    )
    assert registration.status_code == 201
    login = client.post(
        "/auth/login",
        data={"username": "another-owner@example.com", "password": "another-strong-password"},
    )
    assert login.status_code == 200
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    order_id = created.json()["id"]
    assert client.get(f"/orders/{order_id}", headers=other_headers).status_code == 404
    assert client.get("/orders", headers=other_headers).json() == []
