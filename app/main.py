from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import auth, categories, inventory, orders, products

app = FastAPI(title=get_settings().app_name, version="1.0.0")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
