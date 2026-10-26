def test_adjustment_updates_stock_and_creates_audit_record(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "STOCK-1", "name": "Stock item", "price": "4.25", "quantity": 5},
        headers=auth_headers,
    ).json()

    adjustment = client.post(
        f"/inventory/{product['id']}/adjust",
        json={"change": 3, "reason": "restock", "note": "New shipment"},
        headers=auth_headers,
    )
    assert adjustment.status_code == 200
    assert client.get(f"/products/{product['id']}").json()["quantity"] == 8

    history = client.get(
        "/inventory/transactions",
        params={"product_id": product["id"]},
        headers=auth_headers,
    )
    assert len(history.json()) == 1
    assert history.json()[0]["change"] == 3


def test_adjustment_cannot_reduce_stock_below_zero(client, auth_headers):
    product = client.post(
        "/products",
        json={"sku": "STOCK-2", "name": "Stock item", "price": "4.25", "quantity": 2},
        headers=auth_headers,
    ).json()
    response = client.post(
        f"/inventory/{product['id']}/adjust",
        json={"change": -3, "reason": "correction"},
        headers=auth_headers,
    )
    assert response.status_code == 409
    assert client.get(f"/products/{product['id']}").json()["quantity"] == 2
