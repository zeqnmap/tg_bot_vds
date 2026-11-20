from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr = Field(default=SecretStr(""), alias="BOT_TOKEN")
    admin_chat_ids: Annotated[list[int], NoDecode] = Field(default_factory=list, alias="ADMIN_CHAT_IDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("BOT_TOKEN must be set in .env")
        return value

    @field_validator("admin_chat_ids", mode="before")
    @classmethod
    def parse_admin_chat_ids(cls, value: object) -> list[int]:
        if value is None or value == "":
            raise ValueError("ADMIN_CHAT_IDS must be set in .env")
        if isinstance(value, str):
            result = [int(item.strip()) for item in value.split(",") if item.strip()]
            if not result:
                raise ValueError("ADMIN_CHAT_IDS must contain at least one chat ID")
            return result
        if not value:
            raise ValueError("ADMIN_CHAT_IDS must contain at least one chat ID")
        return value  # type: ignore[return-value]

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> str:
        level = str(value).strip().upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
        return level


@lru_cache
def get_settings() -> Settings:
    return Settings()
