# InventoryX — API Examples

Run locally and open [Swagger UI](http://127.0.0.1:8000/docs) for the authoritative OpenAPI schema.

## Register
```http
POST /auth/register
Content-Type: application/json

{"email":"store@example.com","full_name":"Store Operator","password":"ChangeThisPassword123"}
```

## Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=store%40example.com&password=ChangeThisPassword123
```

## List products (authenticated where required by the schema)
```http
GET /products
Authorization: Bearer <access_token>
```

## Adjust stock
```http
POST /inventory/<product_id>/adjust
Authorization: Bearer <access_token>
Content-Type: application/json

{"quantity_change":10,"reason":"Initial stock receipt"}
```

The payload is illustrative. Use Swagger's generated request schema for the exact parameter and field names in the current version.
