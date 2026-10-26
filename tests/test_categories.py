def test_category_can_be_created_and_used_by_a_product(client, auth_headers):
    created = client.post(
        "/categories",
        json={"name": " Hardware "},
        headers=auth_headers,
    )
    assert created.status_code == 201
    category = created.json()
    assert category["name"] == "Hardware"

    product = client.post(
        "/products",
        json={
            "sku": "CATEGORY-1",
            "name": "Hammer",
            "price": "7.99",
            "category_id": category["id"],
        },
        headers=auth_headers,
    )
    assert product.status_code == 201
    assert product.json()["category_id"] == category["id"]
    assert client.get("/categories").json()[0]["id"] == category["id"]
