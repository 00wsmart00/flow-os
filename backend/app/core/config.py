from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_prefix="FLOWOS_",
        extra="ignore",
    )

    app_name: str = "FlowOS API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    env: str = "development"
    log_level: str = "INFO"

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "flowos"
    database_user: str = "flowos"
    database_password: str = Field(default="flowos_dev_only", repr=False)
    database_max_connections: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
