from enum import Enum
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotMode(str, Enum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    bot_token: SecretStr
    channel_id: int
    db_path: str = "store.db"
    default_language: str = "ru"

    mode: BotMode = BotMode.POLLING

    webhook_url: Optional[str] = None
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8443
    webhook_path: str = "/webhook"

    max_photos: int = 10
    min_photos: int = 1


settings = Settings()
