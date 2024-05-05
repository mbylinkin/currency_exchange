from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class AppSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="app_")

    environment: Environment = Environment.PRODUCTION

    debug: bool = False
    database_url: str = "sqlite:///./currency_exchange.db"

    cors_origins: list[str]
    cors_origins_regex: str | None = None
    cors_headers: list[str]

    version: str = "1"

    def fastapi_app_configs(self) -> dict[str, Any]:
        app_configs: dict[str, Any] = {"title": "App API"}
        if self.environment.is_deployed:
            app_configs["root_path"] = f"/v{self.version}"

        if not self.environment.is_debug:
            app_configs["openapi_url"] = None  # hide docs

        return app_configs


class ServerSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="server_")

    host: str = "127.0.0.1"
    port: int = 8000


app = AppSettings()
server = ServerSettings()
