# InventoryX — Architecture

```mermaid
flowchart TD
  Client[API client] --> App[FastAPI]
  App --> Router[Auth / products / categories / inventory / orders]
  Router --> Dep[JWT and database dependencies]
  Router --> Service[Business services]
  Service --> Repo[Repository layer]
  Repo --> Model[SQLAlchemy models]
  Model --> DB[(SQLite / PostgreSQL)]
  Migration[Alembic] --> DB
  Tests[Pytest] --> App
```

Routers handle HTTP concerns, dependencies provide authentication and sessions, services implement inventory/order rules, repositories perform persistence, and Alembic versions schema changes.
