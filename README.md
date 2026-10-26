# InventoryX API

A FastAPI inventory service with JWT authentication, product management, stock
adjustments, and customer orders.

## Run locally

Use Python 3.10 or newer:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a unique `SECRET_KEY` in `.env` before exposing the service. Start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.
The default database is SQLite (`inventoryx.db`). Apply schema changes with
`alembic upgrade head` before starting the service.

## API overview

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET /categories`, `GET /categories/{id}` (public)
- `POST /categories`, `PATCH /categories/{id}`, `DELETE /categories/{id}` (authenticated)
- `GET /products`, `GET /products/{id}` (public)
- `POST /products`, `PATCH /products/{id}`, `DELETE /products/{id}` (authenticated)
- `POST /inventory/{product_id}/adjust` and `GET /inventory/transactions` (authenticated)
- `POST /orders`, `GET /orders`, `GET /orders/{id}`, `POST /orders/{id}/cancel` (authenticated)
- `GET /health`

Login accepts OAuth2 form fields `username` (the account email) and `password`.
Use the returned bearer token to access protected endpoints. Product stock is
updated atomically with order placement/cancellation and each stock change is
recorded in the inventory transaction history.

## Tests

```powershell
pytest
```

Tests use an isolated in-memory SQLite database.
