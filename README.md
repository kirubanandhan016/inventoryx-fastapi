# InventoryX API

**Inventory and order management REST API built with Python and FastAPI.**

InventoryX demonstrates backend workflows for product and category management, stock adjustments, order placement and cancellation, and inventory transaction history.

## Features

- JWT-based registration, login, and current-user endpoint
- Product and category CRUD
- Inventory adjustment endpoint and transaction history
- Authenticated order placement, retrieval, and cancellation
- Atomic stock updates for order workflows
- SQLAlchemy ORM and Alembic migrations
- Interactive OpenAPI documentation
- Automated tests using an isolated in-memory SQLite database

## Tech stack

Python 3.10+ · FastAPI · SQLAlchemy · Alembic · SQLite · JWT · pytest

## Architecture at a glance

The API separates HTTP endpoints, database models, validation, and persistence. Alembic manages schema changes. Inventory changes are recorded in a transaction history so that stock movements can be inspected.

## Run locally (Windows PowerShell)

```powershell
git clone https://github.com/kirubanandhan016/inventoryx-fastapi.git
cd inventoryx-fastapi

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a unique, random `SECRET_KEY` in `.env`. Do not commit the `.env` file or real credentials.

Apply migrations and start the server:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

The default database is SQLite (`inventoryx.db`). Apply migrations before using the API.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register an account |
| POST | `/auth/login` | Obtain an access token |
| GET | `/auth/me` | Read current account |
| GET | `/categories` | List categories |
| GET | `/products` | List products |
| POST | `/inventory/{product_id}/adjust` | Adjust stock |
| GET | `/inventory/transactions` | Review stock history |
| POST | `/orders` | Place an order |
| GET | `/orders` | List orders |
| POST | `/orders/{id}/cancel` | Cancel an order |
| GET | `/health` | Health check |

For the complete endpoint schema, open `http://127.0.0.1:8000/docs` after starting the server.

Login accepts OAuth2 form fields: `username` (the account email) and `password`. Send the returned token as a bearer token to protected endpoints.

## Run tests

```powershell
python -m pytest -v
```

Tests use an isolated in-memory SQLite database. Run the command locally and check its exit status before reporting a passing test result.

## Engineering focus

- Request validation and clear HTTP errors
- Authentication for protected operations
- Stock validation and order lifecycle rules
- Database migrations and transaction-aware workflows
- Regression tests for important business behavior

## Current scope

This is a portfolio and learning project. Review the configuration, tests, deployment setup, and security controls before exposing it to public traffic. PostgreSQL compatibility and production deployment should be documented only after they are tested.

## Author

**Kirubanandhan V** · [GitHub](https://github.com/kirubanandhan016) · [Portfolio](https://kirubanandhan016.github.io/) · [LinkedIn](https://www.linkedin.com/in/kirubanandhan-v-98bb83443/)
