import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PayPilot AI"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    database_url: str = "sqlite+aiosqlite:///./paypilot.db"

    # PayPal Sandbox Settings
    paypal_mode: str = "sandbox"
    paypal_base_url: str = "https://api-m.sandbox.paypal.com"
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_currency: str = "USD"
    gemini_api_key: str = ""

    @property
    def is_paypal_configured(self) -> bool:
        return bool(
            self.paypal_client_id
            and self.paypal_client_secret
            and len(self.paypal_client_id.strip()) > 5
            and len(self.paypal_client_secret.strip()) > 5
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
