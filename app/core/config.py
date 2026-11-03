from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InventoryX API"
    database_url: str = "sqlite:///./inventoryx.db"
    # No fallback secret: configuration must provide a unique key.
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=30, gt=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
