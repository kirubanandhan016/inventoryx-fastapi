# InventoryX API

[![InventoryX tests](https://github.com/kirubanandhan016/inventoryx-fastapi/actions/workflows/tests.yml/badge.svg)](https://github.com/kirubanandhan016/inventoryx-fastapi/actions/workflows/tests.yml)

Inventory and order management REST API built with Python and FastAPI.

InventoryX demonstrates backend workflows for product and category management, stock adjustments, order placement and cancellation, and inventory transaction history.

## Features

- User registration, login, and authenticated current-user endpoint
- Password hashing with salted PBKDF2-HMAC-SHA256
- Signed JWT bearer access tokens with required subject, issued-at, and expiration claims
- Product and category CRUD
- Inventory adjustment endpoint and transaction history
- Authenticated order placement, retrieval, and cancellation
- SQLAlchemy ORM and Alembic migrations
- Interactive OpenAPI documentation
- Pytest API tests using an isolated in-memory SQLite database

## Technology stack

Python 3.10+ · FastAPI · SQLAlchemy · Alembic · SQLite · PostgreSQL (psycopg) · python-jose · Pytest

## Architecture

- `app/routers/`: HTTP endpoints and request orchestration
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic request and response schemas
- `app/repositories/`: database access functions
- `app/services/`: product, inventory, and order business logic
- `app/core/`: application configuration and security helpers
- `app/database/`: SQLAlchemy engine, session, and declarative base
- `alembic/`: versioned database migrations
- `tests/`: authentication, product, inventory, category, and order tests

## Run locally

Create and activate a virtual environment, then install dependencies:

```bash
git clone https://github.com/kirubanandhan016/inventoryx-fastapi.git
cd inventoryx-fastapi
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
python -m pip install -r requirements.txt
```

## Configure environment

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Generate a unique signing secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set the generated value in `.env`:

```env
SECRET_KEY=<your-unique-generated-secret>
DATABASE_URL=sqlite:///./inventoryx.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The application requires `SECRET_KEY` to be at least 32 characters. There is no fallback signing key; application configuration fails when the key is missing or too short. Never commit `.env`, real credentials, or access tokens.

## Database migrations and startup

Apply the committed Alembic migrations, then start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The default local database is SQLite. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL (for example, `postgresql+psycopg://user:password@localhost:5432/inventoryx`) to use PostgreSQL. The GitHub Actions workflow runs the API tests against isolated SQLite fixtures and applies the Alembic migrations to a temporary PostgreSQL 16 service. The migration directory is the schema-change source of truth; do not rely on automatic table creation for schema upgrades.

The API is available at `http://127.0.0.1:8000`. Interactive documentation is at `/docs` and `/redoc`.

## Authentication flow

1. Register with `POST /auth/register` using email, full name, and password.
2. Log in through `POST /auth/login` using OAuth2 form fields `username` (the email address) and `password`.
3. Copy `access_token` from the response.
4. Send `Authorization: Bearer <access_token>` to protected endpoints.

Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes, not plaintext. Access tokens are signed with HS256 and include `sub`, `iat`, and `exp` claims. Protected requests validate the signature, expiration, and required claim shapes before looking up the active user. Access tokens are stateless; there is no refresh-token or server-side revocation endpoint in this project.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register an account |
| POST | `/auth/login` | Obtain an access token |
| GET | `/auth/me` | Read the current account |
| GET | `/categories` | List categories |
| GET | `/products` | List products |
| POST | `/inventory/{product_id}/adjust` | Adjust stock |
| GET | `/inventory/transactions` | Review stock history |
| POST | `/orders` | Place an order |
| GET | `/orders` | List the current user's orders |
| POST | `/orders/{order_id}/cancel` | Cancel an order |
| GET | `/health` | Health check |

Consult the generated OpenAPI schema at `/docs` for request and response models, parameters, and security requirements.

## Run tests

```bash
python -m pytest -v
```

Tests configure a test-only secret and use an isolated in-memory SQLite database. They do not require the local development database. GitHub Actions runs the test suite on pushes and pull requests, then verifies that the Alembic migration head can be applied to PostgreSQL.

## Known scope and limitations

This is a portfolio and learning project. It is not independently security-audited for production deployment. Review deployment configuration, rate limiting, logging, database backup, operational monitoring, and token revocation requirements before exposing it to public traffic. PostgreSQL compatibility should be tested before claiming PostgreSQL support.

## Author

**Kirubanandhan V**

- GitHub: [@kirubanandhan016](https://github.com/kirubanandhan016)
- Portfolio: [kirubanandhan016.github.io](https://kirubanandhan016.github.io/)
- LinkedIn: [Kirubanandhan V](https://www.linkedin.com/in/kirubanandhan-v-98bb83443/)
